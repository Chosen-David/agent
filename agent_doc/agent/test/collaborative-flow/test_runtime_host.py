"""Runtime acceptance: real Windows boundaries and explicit, non-downgrading modes."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy


class RuntimeHostTests(unittest.TestCase):
    def host_fixture(self, directory, *, root=None, task_id='HOST-01', write_paths=('source.py',),
                     workflow=None, project='test'):
        import hashlib
        from agent_runtime.codex_host import CodexHost
        from agent_runtime.plan_review import CHECKS, sha
        root = Path(root) if root is not None else Path(directory) / 'project'
        root.mkdir(exist_ok=True)
        (root / 'source.py').write_text('old', encoding='utf8')
        executable = Path(sys.executable)
        profile = Path(directory) / 'runtime.json'
        profile.write_text(json.dumps({'version': 1, 'command': [str(executable)],
            'executable_sha256': hashlib.sha256(executable.read_bytes()).hexdigest(),
            'writer_model': 'fixture-writer', 'reviewer_model': 'fixture-reviewer'}))
        calls = []

        class FixtureClient:
            def __init__(self, *args):
                pass

            def run(self, model, prompt, schema, cwd):
                calls.append(json.loads(prompt.rsplit('\n', 1)[1]))
                operation = calls[-1]['operation']
                identity = {'invocation_id': 'fixture-turn-' + str(len(calls)),
                    'context_id': 'fixture-context-' + str(len(calls)), 'host_source': 'synthetic-test',
                    'provider_id': 'fixture', 'model_id': model}
                if operation == 'review':
                    result = {'full_review': 'Synthetic fixture only', 'verdict': {
                        'decision': 'approve', 'summary': 'fixture', 'findings': [],
                        'checks': {k: {'status': 'pass', 'reason': 'fixture'} for k in
                                   (*CHECKS, 'spec_compliance', 'code_quality')}}}
                    if self.review_decisions and self.review_decisions.pop(0) == 'revise':
                        result['verdict'].update(decision='revise', findings=[{
                            'blocking': True, 'target': 'fixture evidence', 'feedback': 'Synthetic rejection',
                            'requested_change': 'Recheck current evidence', 'acceptance_check': 'Current tests and review pass'}])
                        result['verdict']['checks']['code_quality']['status'] = 'fail'
                elif operation == 'implement':
                    result = {'summary': 'fixture', 'files': deepcopy(self.proposals)}
                else:
                    result = {'summary': 'fixture', 'steps': [{'id': 'one', 'depends_on': []}]}
                return identity, result, {'status': 'completed', 'tools': [], 'identity': identity,
                                         'response_sha256': sha(result), 'sandbox': {'type': 'readOnly'}}

            def close(self):
                pass

        FixtureClient.proposals = [{'path': 'source.py', 'before_sha256': hashlib.sha256(b'old').hexdigest(),
                                    'content': 'new'}]
        FixtureClient.review_decisions = []
        host = CodexHost(root, task_id, profile, workflow=workflow or Path(directory)/'workflow', project=project,
                         write_paths=write_paths, trust_project_code=True, client_factory=FixtureClient)
        return host, root, FixtureClient, calls

    def test_native_entry_imports_without_posix_only_dependencies(self):
        result = subprocess.run([sys.executable, '-B', '-c',
                                 'import agent_runtime.collaborative_flow; import agent_runtime.task_supervisor'],
                                capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_mode_switch_preserves_task_budget_answers_and_history(self):
        api = importlib.import_module('agent_runtime.collaborative_flow')
        with tempfile.TemporaryDirectory() as directory:
            flow = api.Flow(Path(directory), 'SWITCH-01')
            flow.create('Implement the approved behavior', mode='dual-ai')
            flow.state.update(review_calls=3, answers={'intent': 'keep scope'},
                              design_review={'old': True}, plan={'old': True})
            flow.save()
            flow.switch_mode('human', 'User requests discussion')
            self.assertEqual(flow.state['mode'], 'human')
            self.assertEqual(flow.state['review_calls'], 3)
            self.assertEqual(flow.state['answers'], {'intent': 'keep scope'})
            self.assertNotIn('design_review', flow.state)
            self.assertNotIn('plan', flow.state)
            self.assertEqual(flow.task_id, 'SWITCH-01')
            flow.switch_mode('dual-ai', 'User requests independent review')
            loaded = api.Flow(Path(directory), 'SWITCH-01')
            self.assertEqual(loaded.state['mode'], 'dual-ai')
            self.assertEqual(loaded.state['review_calls'], 3)
            self.assertTrue(any(e['event'] == 'mode-switched' for e in loaded.state['events']))
            loaded.add_review_calls(2, 'Explicit bounded continuation')
            self.assertEqual(loaded.state['review_calls'], 3)
            self.assertEqual(loaded.state['review_limit'], 8)
            self.assertEqual(loaded.state['budget_history'][0]['used_calls'], 3)

    def test_inflight_switch_is_refused_without_state_changes(self):
        api = importlib.import_module('agent_runtime.collaborative_flow')
        with tempfile.TemporaryDirectory() as directory:
            flow = api.Flow(Path(directory), 'SWITCH-02')
            flow.create('Preserve ambiguous effects', mode='dual-ai')
            flow.state['inflight'] = {'method': 'implement'}
            flow.save()
            before = flow.path.read_bytes()
            with self.assertRaises(ValueError):
                flow.switch_mode('human', 'must not bypass inflight effects')
            self.assertEqual(flow.path.read_bytes(), before)

    def test_nonblocking_lock_excludes_another_process(self):
        locks = importlib.import_module('agent_runtime.file_lock')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'lock'
            with path.open('a+b') as stream:
                locks.flock(stream, locks.LOCK_EX)
                code = ('from agent_runtime import file_lock as l; import sys\n'
                        'with open(sys.argv[1],"a+b") as f:\n'
                        ' try: l.flock(f,l.LOCK_EX|l.LOCK_NB)\n'
                        ' except BlockingIOError: print("blocked")\n'
                        ' else: raise RuntimeError("lock was bypassed")\n')
                child = subprocess.run([sys.executable, '-B', '-c', code, str(path)],
                                       capture_output=True, timeout=10)
                self.assertEqual(child.returncode, 0, child.stderr)
                self.assertEqual(child.stdout.strip(), b'blocked')

    def test_runtime_profile_cannot_select_same_writer_and_reviewer_model(self):
        api = importlib.import_module('agent_runtime.codex_host')
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / 'runtime.json'
            profile.write_text(json.dumps({'version': 1, 'command': [sys.executable],
                                           'writer_model': 'same', 'reviewer_model': 'same'}))
            with self.assertRaises(ValueError):
                api.load_profile(profile)

    def test_host_receipt_authenticates_exact_request_and_rejects_tampering(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            host, root, _, _ = self.host_fixture(directory)
            flow = Flow(root, 'HOST-01')
            flow.create('Scoped fixture', mode='dual-ai')
            flow.review(host, {'stage': 'discussion', 'state': flow.state})
            row = flow.state['reviews'][-1]
            self.assertTrue(host.authenticate(row['request'], row['review'], row['proof'])['fresh_context'])
            changed = deepcopy(row['request'])
            changed['request_id'] = 'replay'
            with self.assertRaises(ValueError):
                host.authenticate(changed, row['review'], row['proof'])
            before = host.ledger.read_bytes()
            flow.cancel()
            self.assertTrue(host.authenticate(row['request'], row['review'], row['proof'])['fresh_context'])
            self.assertEqual(host.ledger.read_bytes(), before)
            path = host.base / (row['proof']['receipt_id'] + '.json')
            receipt = json.loads(path.read_text())
            receipt['receipt']['budget_valid'] = False
            path.write_text(json.dumps(receipt))
            with self.assertRaises(ValueError):
                host.authenticate(row['request'], row['review'], row['proof'])
            # Review state must stay serializable; embedded state cannot alias itself.
            self.assertEqual(Flow(root, 'HOST-01').state['review_calls'], 1)

    def test_host_rejects_stale_and_outside_allowlist_proposals_before_writing(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            host, root, client, _ = self.host_fixture(directory)
            flow = Flow(root, 'HOST-01')
            flow.create('Scoped fixture', mode='dual-ai')
            flow.state.update(phase='implementing')
            flow.save()
            client.proposals.append({'path': 'outside.py', 'before_sha256': '', 'content': 'bad'})
            with self.assertRaises(ValueError):
                flow.call(host, 'implement', {'step': 'one'})
            self.assertEqual((root/'source.py').read_text(), 'old')
            self.assertFalse((root/'outside.py').exists())
            client.proposals.pop()
            client.proposals[0]['before_sha256'] = 'stale'
            flow.state['phase'] = 'implementing'
            flow.save()
            with self.assertRaisesRegex(ValueError, 'stale'):
                flow.call(host, 'implement', {'step': 'one'})
            self.assertEqual((root/'source.py').read_text(), 'old')

    def test_host_applies_only_current_approved_file_and_retains_call_budget_on_restart(self):
        from agent_runtime.collaborative_flow import Flow
        from agent_runtime.codex_host import CodexHost
        with tempfile.TemporaryDirectory() as directory:
            host, root, client, _ = self.host_fixture(directory)
            flow = Flow(root, 'HOST-01')
            flow.create('Scoped fixture', mode='dual-ai')
            flow.state.update(phase='implementing')
            flow.save()
            flow.call(host, 'implement', {'step': 'one'})
            self.assertEqual((root/'source.py').read_text(), 'new')
            again = CodexHost(root, 'HOST-01', host.profile['profile_path'], workflow=host.workflow,
                project=host.project, write_paths=['source.py'], client_factory=client)
            self.assertEqual(json.loads(again.ledger.read_text())['calls'], 1)
            again.trust_project_code = False
            with self.assertRaisesRegex(ValueError, 'trust-project-code'):
                again.implement({'step': 'one'})
            self.assertEqual(json.loads(again.ledger.read_text())['calls'], 1)

    def test_host_protects_guides_tests_state_aliases_and_terminal_tasks(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            host, root, _, _ = self.host_fixture(directory)
            for path in ('../escape', 'agent_doc/guide/GUIDE.md', '.agent-runs/state.json',
                         'tests/check.py', 'AGENTS.md', 'source.py/../outside'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    host._path(path)
            os.link(root/'source.py', root/'alias.py')
            with self.assertRaisesRegex(ValueError, 'hard-linked'):
                host._path('source.py')
            flow = Flow(root, 'HOST-01')
            flow.create('Scoped fixture', mode='dual-ai')
            flow.cancel()
            before = flow.path.read_bytes()
            with self.assertRaises(ValueError):
                flow.switch_mode('human', 'cannot revive cancellation')
            self.assertEqual(flow.path.read_bytes(), before)

    def test_native_pipe_eof_cancel_and_partial_line_deadline(self):
        from agent_runtime.collaborative_flow import Flow, wait_for_human, input_line
        with tempfile.TemporaryDirectory() as directory:
            flow = Flow(Path(directory), 'INPUT-01')
            flow.create('Human choice')
            question = {'id': 'q', 'question': 'Choose', 'options': ['A', 'B'], 'kind': 'permission'}
            flow.ask([question])
            read, write = os.pipe()
            os.close(write)
            with os.fdopen(read) as stream, self.assertRaisesRegex(ValueError, 'disconnected'):
                wait_for_human(flow, stream, lambda _: None)
            self.assertEqual(flow.state['phase'], 'waiting')
            read, write = os.pipe()
            os.write(write, b'/cancel\n')
            os.close(write)
            with os.fdopen(read) as stream:
                wait_for_human(flow, stream, lambda _: None)
            self.assertEqual(flow.state['phase'], 'cancelled')
            read, write = os.pipe()
            try:
                os.write(write, b'partial')
                with os.fdopen(read) as stream:
                    self.assertIsNone(input_line(stream, .1))
            finally:
                os.close(write)

    def pipeline_fixture(self):
        import importlib.util
        path = Path(__file__).with_name('test_flow.py')
        spec = importlib.util.spec_from_file_location('runtime_pipeline_fixture', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        case = module.FlowTests('test_human_pipeline_runs_real_task_acceptance')
        case.setUp()
        self.addCleanup(case.doCleanups)
        return case

    def test_resumed_acceptance_requires_builtin_host_execution_consent(self):
        from agent_runtime.codex_host import CodexHost
        from unittest.mock import patch
        import hashlib
        case = self.pipeline_fixture()
        trusted, output, _, _ = case.setup_pipeline()
        case.flow.execute(trusted, output)
        case.flow.state['phase'] = 'implementing'
        case.flow.save()
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory)/'runtime.json'
            profile.write_text(json.dumps({'version': 1, 'command': [sys.executable],
                'executable_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                'writer_model': 'fixture-writer', 'reviewer_model': 'fixture-reviewer'}))
            host = CodexHost(case.root, 'FLOW-01', profile, workflow=case.root/'workflow', project='agent')
            second_output = Path(directory)/'acceptance'
            with patch.object(case.api, 'probe_environment', return_value=case.flow.state['environment']), \
                 patch.object(case.api, 'load_environment_skills', return_value=case.flow.state['execution_context']['skills']), \
                 patch.object(case.api.subprocess, 'run') as launch:
                with self.assertRaisesRegex(ValueError, 'trust-project-code'):
                    case.flow.execute(host, second_output)
                launch.assert_not_called()
            self.assertEqual(case.flow.state['phase'], 'implementing')
            host.trust_project_code = True
            case.flow.execute(host, second_output)
            self.assertEqual(case.flow.state['phase'], 'done')

    def test_timed_out_test_descendant_blocks_automatic_replay_after_restart(self):
        import time
        case = self.pipeline_fixture()
        host, output, calls, suite = case.setup_pipeline()
        check = ("import os,pathlib,subprocess,sys,time\n"
                 "out=pathlib.Path(os.environ['AGENT_TEST_OUTPUT'])\n"
                 "child=subprocess.Popen([sys.executable,'-c',\"import pathlib,sys,time; time.sleep(4); pathlib.Path(sys.argv[1]).write_text('done')\",str(out/'child-done')])\n"
                 "(out/'child-pid').write_text(str(child.pid))\n"
                 "time.sleep(8)\n")
        (suite/'check.py').write_text(check)
        manifest = json.loads((suite/'suite.json').read_text())
        manifest['checks'][0]['timeout_seconds'] = 2
        (suite/'suite.json').write_text(json.dumps(manifest))
        case.flow.plan({'summary': 'Exercise timeout without replay',
                        'steps': [{'id': 'write', 'depends_on': []}]}, case.root/'workflow', 'agent')
        case.flow.execute(host, output)
        self.assertEqual(case.flow.state['phase'], 'blocked')
        self.assertEqual(case.flow.state['inflight']['method'], 'acceptance')
        self.assertTrue((output/'child-pid').is_file())
        self.assertEqual(len(calls), 1)
        again = case.api.Flow(case.root, 'FLOW-01')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            again.execute(host, output.with_name(output.name+'-never'))
        self.assertEqual(len(calls), 1)
        # Let only this owned, short-lived fixture child finish before teardown.
        end = time.monotonic() + 8
        while not (output/'child-done').exists() and time.monotonic() < end:
            time.sleep(.05)
        self.assertTrue((output/'child-done').exists())

    def rejected_tracked_docs_pipeline(self, *, external_workflow=False, diagnostic=None):
        import hashlib
        import time
        case = self.pipeline_fixture()
        case.flow.clock = time.time
        _, output, _, _ = case.setup_pipeline()
        if diagnostic:
            script = case.root/'workflow/agent_doc/agent/test/FLOW-01/check.py'
            script.write_text(script.read_text() + '\nprint(' + repr(diagnostic) + ')\n')
            case.flow.plan({'summary': 'Include diagnostic output in evidence',
                            'steps': [{'id': 'write', 'depends_on': []}]}, case.root/'workflow', 'agent')
        for args in (['add', 'agent_doc'], ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                                           'commit', '-qm', 'tracked controller documents']):
            subprocess.run(['git', '-C', str(case.root), *args], check=True, capture_output=True)
        profile_directory = tempfile.TemporaryDirectory()
        self.addCleanup(profile_directory.cleanup)
        workflow = case.root/'workflow'
        if external_workflow:
            import shutil
            workflow = Path(profile_directory.name)/'external-workflow'
            shutil.copytree(case.root/'workflow', workflow)
            case.flow.plan({'summary': 'Accept against external task suite',
                            'steps': [{'id': 'write', 'depends_on': []}]}, workflow, 'agent')
        host, _, client, calls = self.host_fixture(profile_directory.name, root=case.root,
            task_id='FLOW-01', write_paths=('answer.txt',), workflow=workflow, project='agent')
        client.proposals = [{'path': 'answer.txt', 'before_sha256': hashlib.sha256(b'').hexdigest(), 'content': '42'}]
        client.review_decisions = ['approve', 'revise']
        case.flow.state['mode'] = 'dual-ai'
        case.flow.save()
        case.flow.execute(host, output)
        self.assertEqual(case.flow.state['phase'], 'repair')
        self.assertFalse(case.flow.state.get('inflight'))
        self.assertEqual(case.flow.state['review_calls'], 2)
        return case, host, client, calls, profile_directory.name

    def test_review_only_retry_accepts_exact_controller_progress_but_not_external_edits(self):
        case, host, _, calls, _ = self.rejected_tracked_docs_pipeline()
        implementation_calls = sum(c['operation'] == 'implement' for c in calls)
        case.flow.retry_final_review(host, 'Review-only rejection, source and tests unchanged')
        self.assertEqual(case.flow.state['phase'], 'done')
        self.assertEqual(case.flow.state['review_calls'], 3)
        self.assertEqual(sum(c['operation'] == 'implement' for c in calls), implementation_calls)
        self.assertTrue(host._context()['tested_source_manifest']['host_verified_matches_report_after'])
        (case.root/'agent_doc/task/task_details/FLOW-01.md').write_text('External modification')
        with self.assertRaisesRegex(ValueError, 'changed externally'):
            host._context()
        with self.assertRaisesRegex(ValueError, 'changed externally'):
            case.flow.write_detail()
        self.assertEqual((case.root/'agent_doc/task/task_details/FLOW-01.md').read_text(), 'External modification')

    def test_repair_can_read_stale_acceptance_and_requires_fresh_tests_for_changed_code(self):
        import hashlib
        case, host, client, _, directory = self.rejected_tracked_docs_pipeline()
        (case.root/'answer.txt').write_text('wrong')
        with self.assertRaisesRegex(ValueError, 'tested inputs changed'):
            case.flow.retry_final_review(host, 'Must reject changed code')
        case.flow.call(host, 'discuss', case.flow.discussion_context())
        self.assertFalse(case.flow.state.get('inflight'))
        self.assertFalse(host._context()['tested_source_manifest']['host_verified_matches_report_after'])
        previous = case.flow.state['acceptance']['report']
        case.flow.plan({'summary': 'Repair changed output with fresh acceptance',
                        'steps': [{'id': 'write', 'depends_on': []}]}, case.root/'workflow', 'agent')
        client.proposals = [{'path': 'answer.txt', 'before_sha256': hashlib.sha256(b'wrong').hexdigest(), 'content': '42'}]
        case.flow.execute(host, Path(directory)/'new-acceptance')
        self.assertEqual(case.flow.state['phase'], 'done')
        self.assertEqual(case.flow.state['review_calls'], 4)
        self.assertNotEqual(case.flow.state['acceptance']['report'], previous)

    def test_rejected_replan_cannot_reuse_old_acceptance_after_external_suite_change(self):
        import hashlib
        case, host, client, _, directory = self.rejected_tracked_docs_pipeline(external_workflow=True)
        original_report = case.flow.state['acceptance']['report']
        suite = host.workflow/'agent_doc/agent/test/FLOW-01'
        (suite/'check.py').write_text("from pathlib import Path\nassert Path('answer.txt').read_text() == 'NEW'\n")
        plan = {'summary': 'New version requires NEW output and new acceptance',
                'steps': [{'id': 'write', 'depends_on': []}]}
        case.flow.plan(plan, host.workflow, 'agent')
        client.review_decisions = ['revise']
        case.flow.execute(host, Path(directory)/'design-rejected')
        self.assertEqual(case.flow.state['phase'], 'repair')
        self.assertNotIn('acceptance', case.flow.state)
        self.assertEqual(case.flow.state['acceptance_history'][-1]['report'], original_report)
        used = case.flow.state['review_calls']
        with self.assertRaisesRegex(ValueError, 'fresh design and tests'):
            case.flow.retry_final_review(host, 'Must not reuse old passing suite')
        self.assertEqual(case.flow.state['review_calls'], used)
        case.flow.plan(plan, host.workflow, 'agent')
        client.proposals = [{'path': 'answer.txt', 'before_sha256': hashlib.sha256(b'42').hexdigest(), 'content': 'NEW'}]
        case.flow.execute(host, Path(directory)/'new-suite-accepted')
        self.assertEqual(case.flow.state['phase'], 'done')
        report = json.loads(Path(case.flow.state['acceptance']['report']).read_text())
        self.assertEqual(report['sources'], case.flow.state['test_binding'])
        self.assertEqual((case.root/'answer.txt').read_text(), 'NEW')

    def test_review_receives_bound_raw_logs_and_rejects_changed_missing_or_oversized_output(self):
        from agent_runtime.codex_host import MAX_PACKET
        marker = 'DISTINCTIVE_ACCEPTANCE_DIAGNOSTIC_8137'
        case, host, _, calls, _ = self.rejected_tracked_docs_pipeline(diagnostic=marker)
        case.flow.retry_final_review(host, 'Review raw check output')
        packet = calls[-1]
        self.assertIn(marker, packet['context']['acceptance_logs']['answer']['content'])
        self.assertTrue(packet['context']['acceptance_logs']['answer']['bound_to_report'])
        manifest = packet['context']['tested_source_manifest']
        binding = manifest['file_bindings']['answer.txt']
        self.assertTrue(binding['bound_to_report_after'])
        self.assertEqual(binding['submitted_file_sha256'], binding['manifest_file_sha256'])
        self.assertTrue(manifest['aggregate_binding']['matches'])
        self.assertNotEqual(binding['submitted_file_sha256'], manifest['aggregate_binding']['report_project_manifest_sha256'])
        path = Path(case.flow.state['acceptance']['report']).with_name('answer.log')
        original = path.read_bytes()
        row = case.flow.state['reviews'][-1]
        for data in (b'tampered', b'x' * (MAX_PACKET + 1), None):
            if data is None:
                path.unlink()
            else:
                path.write_bytes(data)
            with self.assertRaisesRegex(ValueError, 'log evidence'):
                host.review(row['request'])
            self.assertIn('_unavailable', host._context()['acceptance_logs'])
        path.write_bytes(original)
        self.assertIn(marker, host._context()['acceptance_logs']['answer']['content'])

    def test_review_rejects_stale_submitted_bytes_before_model_call_even_when_report_aggregate_matches(self):
        from unittest.mock import patch
        from agent_runtime import codex_host
        case,host,_,calls,_=self.rejected_tracked_docs_pipeline()
        request=case.flow.state['reviews'][-1]['request'];original=codex_host.regular_bytes
        before=host.ledger.read_bytes();count=len(calls)
        (case.root/'path-alias').mkdir()
        case.root=case.root/'path-alias'/'..'
        injected=[]
        def stale(root,relative):
            data=original(root,relative)
            if Path(root).resolve()==case.root.resolve() and relative=='answer.txt':
                injected.append(relative)
                return b'stale submitted bytes'
            return data
        with patch.object(codex_host,'regular_bytes',side_effect=stale):
            with self.assertRaisesRegex(ValueError,'source is not bound'):
                host.review(request)
        self.assertTrue(injected)
        self.assertEqual(host.ledger.read_bytes(),before)
        self.assertEqual(len(calls),count)
        self.assertEqual((case.root/'answer.txt').read_bytes(),b'42')

    def test_startup_failure_has_bounded_safe_diagnostic_and_verified_cleanup(self):
        from agent_runtime.codex_host import AppServer, BackendStartupError
        from agent_runtime.model_process import pid_running
        fixture = Path(__file__).with_name('rpc_fixture.py')
        with tempfile.TemporaryDirectory() as directory:
            for mode, diagnostic in (('startup-sqlite', 'state_database_unavailable'),
                                     ('startup-unknown', 'unclassified')):
                with self.subTest(mode=mode):
                    with self.assertRaises(BackendStartupError) as caught:
                        AppServer([sys.executable, '-B', str(fixture), mode], directory, 5)
                    self.assertEqual(getattr(caught.exception, 'startup_diagnostic', None), diagnostic)
                    self.assertFalse(pid_running(caught.exception.closed_backend_pid))
                    self.assertNotIn('private-fixture-token', str(caught.exception))

    def test_app_server_rejects_tools_approvals_writable_sandbox_stale_or_failed_turn(self):
        from agent_runtime.codex_host import AppServer, object_schema
        fixture = Path(__file__).with_name('rpc_fixture.py')
        with tempfile.TemporaryDirectory() as directory:
            for mode in ('tool', 'approval', 'writable', 'stale', 'failed', 'good'):
                with self.subTest(mode=mode):
                    client = AppServer([sys.executable, '-B', str(fixture), mode], directory, 5)
                    try:
                        if mode == 'good':
                            identity, result, observed = client.run('fixture-writer', 'fixture',
                                object_schema({'ready': {'type': 'boolean'}}), directory)
                            self.assertTrue(result['ready'])
                            self.assertEqual(identity['provider_id'], 'fixture')
                            self.assertEqual(observed['tools'], [])
                        else:
                            with self.assertRaises(ValueError):
                                client.run('fixture-writer', 'fixture', object_schema({}), directory)
                    finally:
                        client.close()

    def test_discussion_packet_preserves_decisions_without_nested_history(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            flow = Flow(Path(directory), 'COMPACT-01')
            flow.create('Keep current constraints', mode='dual-ai')
            flow.state['answers'] = {'human': 'Do not widen scope'}
            flow.state['events'].extend([{'event': 'old', 'detail': 'historical text' * 1000}] * 10)
            packet = flow.discussion_context()
            self.assertEqual(packet['answers'], flow.state['answers'])
            self.assertEqual(packet['history']['events']['records'], 11)
            self.assertNotIn('historical text', json.dumps(packet))
            self.assertEqual(len(flow.state['events']), 11)

    def test_no_change_proposal_does_not_force_cosmetic_source_edits(self):
        from agent_runtime.collaborative_flow import Flow
        with tempfile.TemporaryDirectory() as directory:
            host, root, client, _ = self.host_fixture(directory)
            flow = Flow(root, 'HOST-01')
            flow.create('Already satisfied scope', mode='dual-ai')
            flow.state.update(phase='implementing')
            flow.save()
            client.proposals = []
            result = flow.call(host, 'implement', {'step': 'one'})
            self.assertEqual(result['paths'], [])
            self.assertEqual((root/'source.py').read_bytes(), b'old')

    def test_generator_preserves_committed_aliases_on_symlinks_false_checkout(self):
        from unittest.mock import patch
        import importlib.util
        repo = Path(__file__).resolve().parents[4]
        spec = importlib.util.spec_from_file_location('test_reference_generator', repo/'scripts/sync_plugin_references.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args, data=None):
                return subprocess.check_output(['git', '-C', str(root), *args], input=data)
            git('init', '-q')
            git('config', 'core.symlinks', 'false')
            (root/'bundle').mkdir()
            (root/'source.md').write_text('Authoritative shared text\n')
            (root/'shared.py').write_text('VALUE = 42\n')
            for path, target in (('bundle/link.md', '../source.md'), ('alias.py', 'shared.py')):
                (root/path).write_text(target)
                blob = git('hash-object', '-w', '--stdin', data=target.encode()).decode().strip()
                git('update-index', '--add', '--cacheinfo', '120000,' + blob + ',' + path)
            mappings = {'source.md': ['bundle/link.md'], 'alias.py': ['bundle/copy.py']}
            with patch.object(module, 'ROOT', root), patch.object(module, 'MAPPINGS', mappings), patch.object(sys, 'argv', ['sync']):
                self.assertEqual(module.main(), 0)
                self.assertEqual((root/'bundle/link.md').read_text(), '../source.md')
                self.assertEqual((root/'bundle/copy.py').read_text(), 'VALUE = 42\n')
                (root/'bundle/link.md').write_text('human local change')
                self.assertEqual(module.main(), 1)
                self.assertEqual((root/'bundle/link.md').read_text(), 'human local change')


if __name__ == '__main__':
    unittest.main()
