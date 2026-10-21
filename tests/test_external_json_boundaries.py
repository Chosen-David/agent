"""External JSON inputs fail closed without blocking supervisors or mutating state."""
import fcntl
import copy
import json
import multiprocessing
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch

from agent_runtime.external_json import load_json
from agent_runtime.project_memory import MemoryError, _load_document_refs
from agent_runtime.task_manifest import atomic_json, prepare
from scripts.validate_handoff import _load_json
from scripts.token_probe import ProbeError, validate_answer


def _load_in_child(queue, kind, path):
    try:
        if kind == 'handoff':
            _load_json(Path(path))
        elif kind == 'memory':
            _load_document_refs(path)
        elif kind == 'plan':
            from agent_runtime.task_supervisor import submit_review
            root = Path(path).parent
            submit_review(path, root, root / 'state', None, root / 'reviewed.json')
        else:
            from agent_runtime.task_supervisor import guard
            os.environ['TMUX'] = 'fixture'
            guard(path)
    except BaseException as exc:  # Return the observed boundary, including unexpected failures.
        queue.put(('error', type(exc).__name__, str(exc)))
    else:
        queue.put(('accepted', None, None))


def _start_after_task_replacement(queue, root, plan_path, state_dir, task_path):
    from agent_runtime import task_supervisor

    original = task_supervisor.validate_contract
    replaced = False

    def replace_after_validation(*args, **kwargs):
        nonlocal replaced
        result = original(*args, **kwargs)
        if not replaced:
            replaced = True
            Path(task_path).unlink()
            os.mkfifo(task_path)
        return result

    mocked_tmux = None
    try:
        with patch.object(task_supervisor.shutil, 'which', return_value='/fixture/tmux'), \
             patch.object(task_supervisor, 'tmux') as mocked_tmux, \
             patch.object(task_supervisor, 'validate_contract', side_effect=replace_after_validation):
            task_supervisor.start(plan_path, root, state_dir, allow_legacy=True)
    except BaseException as exc:
        queue.put(('error', type(exc).__name__, str(exc), mocked_tmux.call_count))
    else:
        queue.put(('accepted', None, None, mocked_tmux.call_count))


def _start_with_crash_fifo(queue, root, plan_path, state_dir):
    from agent_runtime import task_supervisor

    calls = []
    def fake_tmux(*args, check=True):
        calls.append(args)
        return subprocess.CompletedProcess(args, 1 if args[0] in ('has-session', 'list-panes') else 0,
                                           stdout='', stderr='')

    try:
        with patch.object(task_supervisor.shutil, 'which', return_value='/fixture/tmux'), \
             patch.object(task_supervisor, 'tmux', side_effect=fake_tmux):
            task_supervisor.start(plan_path, root, state_dir, allow_legacy=True)
    except BaseException as exc:
        queue.put(('error', type(exc).__name__, str(exc), calls))
    else:
        queue.put(('accepted', None, None, calls))


def _optimizer_with_state_fifo(queue, root, state_dir, executable):
    from scripts.token_optimizer import tick
    try:
        tick(root, state_dir, executable, now=100)
    except BaseException as exc:
        queue.put(('error', type(exc).__name__, str(exc)))
    else:
        queue.put(('accepted', None, None))


@unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX special-file checks')
class ExternalJsonBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.context = multiprocessing.get_context('fork')

    def run_child(self, target, args):
        queue = self.context.Queue()
        process = self.context.Process(target=target, args=(queue, *args))
        process.start()
        process.join(2)
        if process.is_alive():
            process.terminate()
            process.join(2)
            self.fail('external input blocked instead of failing closed')
        self.assertEqual(process.exitcode, 0)
        return queue.get(timeout=1)

    def test_handoff_and_document_refs_reject_fifo_without_blocking(self):
        fifo = self.root / 'input.json'
        os.mkfifo(fifo)
        for kind in ('handoff', 'memory', 'plan', 'config'):
            with self.subTest(kind=kind):
                status, error_type, message = self.run_child(
                    _load_in_child, (kind, str(fifo)))
                self.assertEqual(status, 'error')
                self.assertIn(error_type, ('ExternalJSONError', 'MemoryError',
                                           'SupervisorInputError'))
                self.assertIn('regular file', message)

    def test_supervisor_cli_reports_special_config_as_structured_error(self):
        fifo = self.root / 'launch.json'
        os.mkfifo(fifo)
        command = [sys.executable, '-m', 'agent_runtime.task_supervisor',
                   'status', '--config', str(fifo)]
        result = subprocess.run(command, cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('regular file', json.loads(result.stderr)['error'])
        self.assertNotIn('Traceback', result.stderr)

    def test_core_and_supervisor_clis_report_malformed_json_without_traceback(self):
        source = self.root / 'bad.json'
        source.write_text('{bad')
        repo = Path(__file__).resolve().parents[1]
        commands = (
            [sys.executable, '-m', 'agent_runtime', '--db', str(self.root / 'bad.sqlite'),
             'init', str(source)],
            [sys.executable, '-m', 'agent_runtime.task_supervisor', 'status',
             '--config', str(source)],
        )
        for command in commands:
            with self.subTest(command=command[2:4]):
                result = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=3)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertIn('malformed', json.loads(result.stderr)['error'])
                self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((self.root / 'bad.sqlite').exists())

    def test_wrong_shape_clis_fail_before_state_creation_without_traceback(self):
        repo = Path(__file__).resolve().parents[1]
        source = self.root / 'wrong-shape.json'
        for index, payload in enumerate(('[]', '{}', 'null')):
            source.write_text(payload)
            db = self.root / f'wrong-{index}.sqlite'
            commands = (
                [sys.executable, '-m', 'agent_runtime', '--db', str(db), 'init', str(source)],
                [sys.executable, '-m', 'agent_runtime.task_supervisor', 'status',
                 '--config', str(source)],
                [sys.executable, '-m', 'agent_runtime.task_supervisor', 'review',
                 '--plan', str(source), '--project-root', str(self.root),
                 '--state-dir', str(self.root / 'review-state'),
                 '--adapter', str(self.root / 'missing.py'),
                 '--out', str(self.root / 'reviewed.json')],
                [sys.executable, str(repo / 'scripts' / 'discover_backends.py'),
                 '--registry', str(source)],
                [sys.executable, str(repo / 'scripts' / 'knowledge_maintenance.py'),
                 'status', '--config', str(source)],
            )
            for command in commands:
                with self.subTest(payload=payload, command=command[1:3]):
                    result = subprocess.run(command, cwd=repo, capture_output=True,
                                            text=True, timeout=3)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('error', json.loads(result.stderr))
                    self.assertNotIn('Traceback', result.stderr)
            self.assertFalse(db.exists())
            self.assertFalse((self.root / 'reviewed.json').exists())

    def test_core_cli_rejects_nested_plan_shapes_without_traceback_or_database(self):
        source = self.root / 'nested-plan.json'
        base = {'schema_version': 'task-dag/v1', 'run_id': 'nested',
                'user_goal': 'reject malformed nested structures',
                'authorization_reference': 'unit test',
                'tasks': [1],
                'supervision': {'min_seconds': 1, 'max_seconds': 2,
                                'rationale': 'bounded'}}
        for index, mutation in enumerate((
                {}, {'tasks': [{'task_id': 'a'}]}, {'tasks': [], 'supervision': []})):
            plan = {**base, **mutation}
            source.write_text(json.dumps(plan))
            db = self.root / f'nested-{index}.sqlite'
            result = subprocess.run(
                [sys.executable, '-m', 'agent_runtime', '--db', str(db),
                 'init', str(source)], cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn('error', json.loads(result.stderr))
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse(db.exists())

    def test_supervisor_rejects_nested_manifest_shapes_before_writes(self):
        task = self.root / 'TASK.md'
        task.write_text('- [ ] [T1] Reject nested shapes\n')
        base = prepare(task, 'nested-supervisor', 'manual', 'unit test',
                       review_required=False)
        mutations = (
            ('task_source', []), ('task_source', {}),
            ('project_documents', []),
            ('task.report_path', []), ('task.task_refs', {}),
            ('task.outputs', {}), ('task.outputs', [{}]))
        repo = Path(__file__).resolve().parents[1]
        for index, (field, value) in enumerate(mutations):
            candidate = copy.deepcopy(base)
            if field.startswith('task.'):
                candidate['tasks'][0][field.split('.', 1)[1]] = value
            else:
                candidate[field] = value
            source = self.root / f'nested-supervisor-{index}.json'
            source.write_text(json.dumps(candidate))
            state = self.root / f'nested-supervisor-{index}-state'
            out = self.root / f'nested-supervisor-{index}-reviewed.json'
            result = subprocess.run(
                [sys.executable, '-m', 'agent_runtime.task_supervisor', 'review',
                 '--plan', str(source), '--project-root', str(self.root),
                 '--state-dir', str(state), '--adapter', str(self.root / 'missing.py'),
                 '--out', str(out)], cwd=repo, capture_output=True, text=True, timeout=3)
            with self.subTest(field=field, value=value):
                self.assertEqual(result.returncode, 2)
                self.assertIn('error', json.loads(result.stderr))
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(state.exists())
                self.assertFalse(out.exists())

    def test_protected_prior_result_shapes_fail_before_review_or_start_writes(self):
        task = self.root / 'TASK.md'
        task.write_text('- [ ] [T1] Reject prior-result shapes\n')
        base = prepare(task, 'nested-prior', 'manual', 'unit test', review_required=True)
        (self.root / 'prior-regular.json').write_text('{}')
        (self.root / 'prior-dir').mkdir()
        os.mkfifo(self.root / 'prior.fifo')
        (self.root / 'prior-link.json').symlink_to(self.root / 'prior-regular.json')
        def hit(path):
            return {'results': [{'record_path': path, 'record_sha256': '0' * 64}]}
        mutations = (
            ('prior_result_search', []), ('prior_result_search', None),
            ('prior_result_search', {'results': None}),
            ('prior_result_search', {'results': [{}]}),
            ('prior_result_search', {'results': [{'record_sha256': '0' * 64}]}),
            ('prior_result_search', {'results': [{'record_path': 'record.json'}]}),
            ('prior_result_search', {'results': [{'record_path': '',
                                                  'record_sha256': '0' * 64}]}),
            ('prior_result_search', {'results': [{'record_path': '../escape',
                                                  'record_sha256': '0' * 64}]}),
            ('prior_result_search', {'results': [{'record_path': str(self.root / 'escape'),
                                                  'record_sha256': '0' * 64}]}),
            ('prior_result_search', hit('missing.json')),
            ('prior_result_search', hit('prior.fifo')),
            ('prior_result_search', hit('prior-dir')),
            ('prior_result_search', hit('prior-link.json')),
            ('prior_result_search', hit('prior-regular.json')),
            ('prior_result_review', []), ('prior_result_review', None),
            ('prior_result_review', {'record_refs': None}),
            ('prior_result_review', {'record_refs': [{'run_id': '../escape',
                                                       'record_sha256': '0' * 64}]}),
            ('prior_result_review', {'record_refs': [{'run_id': 'old',
                                                       'record_sha256': True}]}),
            ('prior_result_review', {'record_refs': [{'run_id': 'missing-review',
                                                       'record_sha256': '0' * 64}]}),
            ('plan_review.evidence_refs', [{'path': 'missing-evidence.json',
                                            'sha256': '0' * 64}]))
        repo = Path(__file__).resolve().parents[1]
        for index, (field, value) in enumerate(mutations):
            candidate = copy.deepcopy(base)
            if field == 'plan_review.evidence_refs':
                candidate['plan_review']['evidence_refs'] = value
            else:
                candidate['tasks'][0][field] = value
            source = self.root / f'prior-shape-{index}.json'
            source.write_text(json.dumps(candidate))
            for command in ('core', 'review', 'start'):
                state = self.root / f'prior-shape-{index}-{command}-state'
                out = self.root / f'prior-shape-{index}-reviewed.json'
                db = self.root / f'prior-shape-{index}.sqlite'
                if command == 'core':
                    args = [sys.executable, '-m', 'agent_runtime', '--db', str(db),
                            'init', str(source)]
                else:
                    args = [sys.executable, '-m', 'agent_runtime.task_supervisor', command,
                            '--plan', str(source), '--project-root', str(self.root),
                            '--state-dir', str(state)]
                if command == 'review':
                    args += ['--adapter', str(self.root / 'missing.py'), '--out', str(out)]
                result = subprocess.run(args, cwd=repo, capture_output=True,
                                        text=True, timeout=3)
                with self.subTest(field=field, value=value, command=command):
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('error', json.loads(result.stderr))
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertFalse(state.exists())
                    self.assertFalse(out.exists())
                    self.assertFalse(db.exists())

    def test_probe_answer_validator_rejects_nested_shapes(self):
        for answer in ([], None, {}, {'proceed': False, 'reasons': [1]},
                       {'proceed': 0, 'reasons': []}):
            with self.subTest(answer=answer), self.assertRaises(ProbeError):
                validate_answer(answer)

    def test_core_and_registry_clis_reject_fifo_without_blocking(self):
        fifo = self.root / 'input.json'
        os.mkfifo(fifo)
        repo = Path(__file__).resolve().parents[1]
        commands = (
            ([sys.executable, '-m', 'agent_runtime', '--db', str(self.root / 'state.sqlite'),
              'init', str(fifo)], 'stderr'),
            ([sys.executable, str(repo / 'scripts' / 'result_store.py'), '--root', str(self.root),
              'decide', 'query', '--context', str(fifo)], 'stdout'),
            ([sys.executable, '-m', 'agent_runtime.knowledge', '--root', str(repo / 'knowledge'),
              'decision', 'query', '--context', str(fifo)], 'stderr'),
            ([sys.executable, str(repo / 'scripts' / 'validate_experiment_result.py'),
              '--root', str(self.root), '--contract', str(fifo)], 'stderr'),
            ([sys.executable, str(repo / 'scripts' / 'validate_paper_delivery.py'), str(fifo),
              '--root', str(self.root)], 'stdout'),
            ([sys.executable, str(repo / 'scripts' / 'knowledge_maintenance.py'), 'status',
              '--config', str(fifo)], 'stderr'),
            ([sys.executable, str(repo / 'scripts' / 'agent_eval_pipeline.py'), 'prepare',
              '--dev-eval', '--repo', str(repo), '--revision', 'HEAD',
              '--out', str(self.root / 'eval-out'), '--tasks', str(fifo)], 'stderr'),
            ([sys.executable, str(repo / 'scripts' / 'discover_backends.py'),
              '--registry', str(fifo)], 'stderr'),
        )
        for command, stream in commands:
            with self.subTest(command=command[1:3]):
                result = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=3)
                self.assertNotEqual(result.returncode, 0)
                output = getattr(result, stream)
                self.assertIn('regular file', output)
                self.assertNotIn('Traceback', result.stderr)
        self.assertFalse((self.root / 'state.sqlite').exists())

    def test_workflow_clis_reject_fifo_without_blocking_or_writing(self):
        fifo = self.root / 'workflow.json'
        os.mkfifo(fifo)
        repo = Path(__file__).resolve().parents[1]
        output = self.root / 'token-output'
        commands = (
            [sys.executable, str(repo / 'scripts' / 'codex_tool_scope.py'),
             '--root', str(self.root), '--contract', str(fifo)],
            [sys.executable, str(repo / 'scripts' / 'eval_knowledge.py'),
             '--root', str(repo / 'knowledge'), '--cases', str(fifo),
             '--output', str(self.root / 'retrieval.json')],
            [sys.executable, str(repo / 'scripts' / 'token_probe.py'),
             '--root', str(self.root), '--output', str(output),
             '--codex', sys.executable, '--quota', str(fifo)],
        )
        for command in commands:
            with self.subTest(command=Path(command[1]).name):
                result = subprocess.run(command, cwd=repo, capture_output=True,
                                        text=True, timeout=3)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('regular file', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse((self.root / 'retrieval.json').exists())

    def test_communication_payloads_fail_before_mailbox_creation(self):
        repo = Path(__file__).resolve().parents[1]
        plan = self.root / 'communication-plan.json'
        plan.write_text(json.dumps({'schema_version': 1, 'run_id': 'run',
            'input_version': 'v1', 'routes': [{'sender': 'worker', 'recipient': 'writer',
            'task_id': 'T1', 'kind': 'artifact'}]}))
        base = [sys.executable, '-m', 'agent_runtime.communication',
                '--root', str(self.root), '--plan', str(plan)]
        for invalid_kind in ('fifo', 'malformed', 'wrong-shape'):
            for command in ('publish', 'publish-many', 'ack', 'consume', 'context', 'context-known'):
                case = self.root / f'communication-{invalid_kind}-{command}'
                case.mkdir()
                external = case / 'input.json'
                if invalid_kind == 'fifo': os.mkfifo(external)
                elif invalid_kind == 'malformed': external.write_text('{broken')
                else: external.write_text('{}' if command == 'publish-many' else '[]')
                db = case / 'mail.sqlite'
                args = [*base, '--db', str(db)]
                if command == 'publish': args += ['publish', str(external)]
                elif command == 'publish-many': args += ['publish-many', str(external)]
                elif command == 'ack': args += ['ack', 'writer', '1', str(external)]
                elif command == 'consume': args += ['consume', 'writer', '1', '--request', str(external)]
                elif command == 'context': args += ['context', 'writer', '1', '--request', str(external)]
                else:
                    request = case / 'request.json'; request.write_text('{}')
                    args += ['context', 'writer', '1', '--request', str(request), '--known', str(external)]
                result = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=3)
                with self.subTest(invalid_kind=invalid_kind, command=command):
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('error', json.loads(result.stdout))
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertFalse(db.exists())

        valid_request = {'schema_version': 1, 'input_version': 'v1',
                         'tasks': [{'task_id': 'T1'}]}
        semantic_cases = (
            ('publish-empty', 'publish', {}, None),
            ('publish-empty-refs', 'publish', {'event_id': 'e1', 'run_id': 'run',
                'input_version': 'v1', 'sender': 'worker', 'task_id': 'T1',
                'kind': 'artifact', 'summary': 'summary', 'action': 'act', 'refs': []}, None),
            ('batch-bad-event', 'publish-many', [{}], None),
            ('ack-bad-receipt', 'ack', {}, None),
            ('consume-bad-request', 'consume', {}, None),
            ('context-bad-request', 'context', {}, None),
            ('context-bad-known-list', 'context', valid_request,
             {'knowledge_refs': {}, 'memory_refs': []}),
            ('context-bad-known-ref', 'context', valid_request,
             {'knowledge_refs': [{}], 'memory_refs': []}),
            ('context-bad-known-memory', 'context', valid_request,
             {'knowledge_refs': [], 'memory_refs': [1]}),
        )
        for name, command, payload, known in semantic_cases:
            case = self.root / name; case.mkdir()
            external = case / 'input.json'; external.write_text(json.dumps(payload))
            db = case / 'mail.sqlite'
            args = [*base, '--db', str(db)]
            if command == 'publish': args += ['publish', str(external)]
            elif command == 'publish-many': args += ['publish-many', str(external)]
            elif command == 'ack': args += ['ack', 'writer', '1', str(external)]
            elif command == 'consume': args += ['consume', 'writer', '1', '--request', str(external)]
            else:
                args += ['context', 'writer', '1', '--request', str(external)]
                if known is not None:
                    known_path = case / 'known.json'; known_path.write_text(json.dumps(known))
                    args += ['--known', str(known_path)]
            result = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=3)
            with self.subTest(semantic=name):
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('error', json.loads(result.stdout))
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(db.exists())

    def test_invalid_json_precedes_trusted_verifier_import(self):
        repo = Path(__file__).resolve().parents[1]
        for invalid_kind in ('fifo', 'malformed', 'wrong-shape'):
            case = self.root / f'adapter-order-{invalid_kind}'
            case.mkdir()
            source = case / 'input.json'
            if invalid_kind == 'fifo': os.mkfifo(source)
            elif invalid_kind == 'malformed': source.write_text('{broken')
            else: source.write_text('[]')
            for script in ('validate_experiment_result.py', 'result_store.py'):
                marker = case / (script + '.marker')
                adapter = case / (script + '.adapter.py')
                adapter.write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('imported')\ndef verify(*args): return None\n")
                if script == 'validate_experiment_result.py':
                    args = [sys.executable, str(repo / 'scripts' / script), '--root', str(self.root),
                            '--contract', str(source), '--verifier-adapter', str(adapter)]
                else:
                    args = [sys.executable, str(repo / 'scripts' / script), '--root', str(self.root),
                            'decide', 'query', '--context', str(source), '--verifier-adapter', str(adapter)]
                result = subprocess.run(args, cwd=repo, capture_output=True, text=True, timeout=3)
                with self.subTest(invalid_kind=invalid_kind, script=script):
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertFalse(marker.exists())

    def test_optimizer_state_fifo_fails_without_sync_or_model_work(self):
        state_dir = self.root / '.agent-runs' / 'hourly'
        state_dir.mkdir(parents=True)
        os.mkfifo(state_dir / 'state.json')
        executable = self.root / 'codex'
        executable.write_bytes(b'not invoked')
        status, error_type, message = self.run_child(
            _optimizer_with_state_fifo,
            (str(self.root), str(state_dir), str(executable)))
        self.assertEqual(status, 'error')
        self.assertEqual(error_type, 'ExternalJSONError')
        self.assertIn('regular file', message)
        self.assertCountEqual(list(state_dir.iterdir()), [state_dir / 'state.json',
                                                          state_dir / 'worker.lock'])

    def test_optimizer_rejects_nested_state_before_durable_mutation(self):
        repo = Path(__file__).resolve().parents[1]
        executable = self.root / 'codex'
        executable.write_bytes(b'not invoked')
        base = {'project_root': str(self.root), 'interval_seconds': 3600,
                'next_due': 10**15}
        def checkpoint(head):
            return {'thread_id': 'saved', 'thread_total_tokens': 1,
                    'stagnant_ticks': 0, 'profile_version': 'bounded-resumable-v1',
                    'work_snapshot': {'head': head, 'status': '', 'files': {},
                                      'index_sha256': '0' * 64}}
        invalid = (
            {key: value for key, value in base.items() if key != 'next_due'},
            {**base, 'checkpoint': []},
            {**base, 'checkpoint': {}},
            {**base, 'checkpoint': {'thread_id': 'saved', 'thread_total_tokens': 1,
                                    'stagnant_ticks': 0,
                                    'profile_version': 'bounded-resumable-v1',
                                    'work_snapshot': []}},
            {**base, 'checkpoint': checkpoint('')},
            {**base, 'checkpoint': checkpoint('g' * 40)},
            {**base, 'checkpoint': checkpoint('a' * 39)},
            {**base, 'checkpoint': {**checkpoint('a' * 40), 'thread_id': '   '}},
            {**base, 'failure_latch': []},
            {**base, 'failure_latch': ''},
            {**base, 'last_started': True},
            {**base, 'last_result': []},
        )
        for index, payload in enumerate(invalid):
            state_dir = self.root / '.agent-runs' / f'invalid-{index}'
            state_dir.mkdir(parents=True)
            state_path = state_dir / 'state.json'
            state_path.write_text(json.dumps(payload, separators=(',', ':')))
            before = state_path.read_bytes()
            result = subprocess.run(
                [sys.executable, str(repo / 'scripts' / 'token_optimizer.py'),
                 '--root', str(self.root), '--state-dir', str(state_dir),
                 '--codex', str(executable)], cwd=repo, capture_output=True,
                text=True, timeout=3)
            with self.subTest(index=index):
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('error', json.loads(result.stderr))
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(state_path.read_bytes(), before)
                self.assertEqual({path.name for path in state_dir.iterdir()},
                                 {'state.json', 'worker.lock'})
    def test_optimizer_cli_reports_state_fifo_without_traceback(self):
        state_dir = self.root / '.agent-runs' / 'hourly'
        state_dir.mkdir(parents=True)
        os.mkfifo(state_dir / 'state.json')
        executable = self.root / 'codex'
        executable.write_bytes(b'not invoked')
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(repo / 'scripts' / 'token_optimizer.py'),
             '--root', str(self.root), '--state-dir', str(state_dir),
             '--codex', str(executable)], cwd=repo, capture_output=True,
            text=True, timeout=3)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('regular file', json.loads(result.stderr)['error'])
        self.assertNotIn('Traceback', result.stderr)

    def test_optimizer_cli_rejects_nonobject_state_without_traceback(self):
        state_dir = self.root / '.agent-runs' / 'hourly'
        state_dir.mkdir(parents=True)
        executable = self.root / 'codex'
        executable.write_bytes(b'not invoked')
        repo = Path(__file__).resolve().parents[1]
        for payload in ('[]', 'null'):
            (state_dir / 'state.json').write_text(payload)
            result = subprocess.run(
                [sys.executable, str(repo / 'scripts' / 'token_optimizer.py'),
                 '--root', str(self.root), '--state-dir', str(state_dir),
                 '--codex', str(executable)], cwd=repo, capture_output=True,
                text=True, timeout=3)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn('JSON object', json.loads(result.stderr)['error'])
            self.assertNotIn('Traceback', result.stderr)

    def test_probe_rejects_quota_semantics_before_output_creation(self):
        repo = Path(__file__).resolve().parents[1]
        output = self.root / 'probe-output'
        quota = self.root / 'quota.json'
        commands = []
        for payload in (
                {'result': {'ordinaryUsageAllowed': False}},
                {'result': {'ordinaryUsageAllowed': True,
                            'rateLimits': {'primary': {'usedPercent': True}}}}):
            quota.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(repo / 'scripts' / 'token_probe.py'),
                 '--root', str(self.root), '--output', str(output),
                 '--codex', sys.executable, '--quota', str(quota)],
                cwd=repo, capture_output=True, text=True, timeout=3)
            commands.append(result)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse(output.exists())
        self.assertEqual(len(commands), 2)

    def test_probe_rejects_special_or_invalid_config_before_output_creation(self):
        repo = Path(__file__).resolve().parents[1]
        quota = self.root / 'valid-quota.json'
        quota.write_text(json.dumps({'result': {'ordinaryUsageAllowed': True,
            'rateLimits': {'primary': {'usedPercent': 0}}}}))
        for kind in ('fifo', 'directory', 'symlink', 'oversize', 'utf8', 'toml',
                     'model-date', 'effort-array', 'model-empty'):
            home = self.root / ('codex-home-' + kind)
            home.mkdir()
            config = home / 'config.toml'
            if kind == 'fifo':
                os.mkfifo(config)
            elif kind == 'directory':
                config.mkdir()
            elif kind == 'symlink':
                target = self.root / 'valid-config.toml'
                target.write_text('model = "fixture"\n')
                config.symlink_to(target)
            elif kind == 'oversize':
                config.write_bytes(b'x' * (1024 * 1024 + 1))
            elif kind == 'utf8':
                config.write_bytes(b'\xff')
            elif kind == 'model-date':
                config.write_text('model = 1979-05-27\n')
            elif kind == 'effort-array':
                config.write_text('model_reasoning_effort = ["high"]\n')
            elif kind == 'model-empty':
                config.write_text('model = ""\n')
            else:
                config.write_text('model =')
            output = self.root / ('probe-output-' + kind)
            env = dict(os.environ, CODEX_HOME=str(home))
            result = subprocess.run(
                [sys.executable, str(repo / 'scripts' / 'token_probe.py'),
                 '--root', str(self.root), '--output', str(output),
                 '--codex', sys.executable, '--quota', str(quota)],
                cwd=repo, env=env, capture_output=True, text=True, timeout=3)
            with self.subTest(kind=kind):
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertIn('error', json.loads(result.stderr))
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(output.exists())

    def test_handoff_reader_rejects_directory_symlink_duplicates_and_nonfinite(self):
        source = self.root / 'source.json'
        source.write_text('{}')
        link = self.root / 'link.json'
        link.symlink_to(source)
        for path in (self.root, link):
            with self.subTest(path=path), self.assertRaises((OSError, ValueError)):
                _load_json(path)
        for payload in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":1e400}',
                        b'{"x":' + b'1' * 5000 + b'}', b'{bad', b'\xff'):
            with self.subTest(payload=payload):
                source.write_bytes(payload)
                with self.assertRaises(ValueError):
                    _load_json(source)

    def test_handoff_reader_honors_exact_byte_boundary(self):
        source = self.root / 'source.json'
        source.write_bytes(b'{"x":"12345678"}')
        self.assertEqual(_load_json(source, max_bytes=16), {'x': '12345678'})
        source.write_bytes(b'{"x":"123456789"}')
        with self.assertRaisesRegex(ValueError, 'byte bound'):
            _load_json(source, max_bytes=16)

    def test_plan_loader_preserves_multi_megabyte_compatibility(self):
        source = self.root / 'large-plan.json'
        prefix, suffix = b'{"payload":"', b'"}'
        total = 6_800_000
        source.write_bytes(prefix + b'x' * (total - len(prefix) - len(suffix)) + suffix)
        value = load_json(source)
        self.assertEqual(len(value['payload']), total - len(prefix) - len(suffix))

    def test_tiny_snapshot_does_not_allocate_configured_ceiling(self):
        source = self.root / 'tiny.json'
        source.write_bytes(b'{}')
        tracemalloc.start()
        try:
            value = load_json(source, max_bytes=256 * 1024 * 1024)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(value, {})
        self.assertLess(peak, 2 * 1024 * 1024)

    def test_task_fifo_after_initial_validation_fails_and_releases_launch_lock(self):
        task = self.root / 'TASK.md'
        original = '- [ ] [T1] Verify bounded input\n'
        task.write_text(original)
        plan = prepare(task, 'fifo-start', 'manual', 'unit-test', review_required=False)
        node = plan['tasks'][0]
        node['action'] = 'verify_artifacts'
        node['done_when'] = {'artifacts': []}
        plan_path = self.root / 'plan.json'
        atomic_json(plan_path, plan)
        state_dir = self.root / 'run'

        status, error_type, message, tmux_calls = self.run_child(
            _start_after_task_replacement,
            (str(self.root), str(plan_path), str(state_dir), str(task)))
        self.assertEqual(status, 'error')
        self.assertEqual(error_type, 'DocumentError')
        self.assertIn('regular file', message)
        self.assertEqual(tmux_calls, 0)
        self.assertCountEqual(list(state_dir.iterdir()), [state_dir / 'launch.lock'])

        lock_path = state_dir / 'launch.lock'
        fd = os.open(lock_path, os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)

    def test_crash_state_fifo_during_start_fails_and_releases_launch_lock(self):
        task = self.root / 'TASK.md'
        task.write_text('- [ ] [T1] Verify crash-state input\n')
        plan = prepare(task, 'crash-fifo-start', 'manual', 'unit-test', review_required=False)
        plan['tasks'][0]['action'] = 'verify_artifacts'
        plan['tasks'][0]['done_when'] = {'artifacts': []}
        plan_path = self.root / 'plan.json'
        atomic_json(plan_path, plan)
        state_dir = self.root / 'run'
        state_dir.mkdir()
        os.mkfifo(state_dir / 'guard-failure.json')

        status, error_type, message, tmux_calls = self.run_child(
            _start_with_crash_fifo, (str(self.root), str(plan_path), str(state_dir)))
        self.assertEqual(status, 'error')
        self.assertEqual(error_type, 'ExternalJSONError')
        self.assertIn('regular file', message)
        self.assertEqual(tmux_calls, [])
        self.assertCountEqual(list(state_dir.iterdir()),
                              [state_dir / 'guard-failure.json', state_dir / 'launch.lock'])

        fd = os.open(state_dir / 'launch.lock', os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)


if __name__ == '__main__':
    unittest.main()
