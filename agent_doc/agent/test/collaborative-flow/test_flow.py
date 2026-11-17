import importlib
import json
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys
import os
from unittest.mock import patch
from types import SimpleNamespace
import unittest


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.api = importlib.import_module('agent_runtime.collaborative_flow')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = 100.0
        self.flow = self.api.Flow(self.root, 'FLOW-01', clock=lambda: self.now)
        self.flow.create('Implement exact addition')

    def question(self, kind='implementation'):
        self.flow.ask([{'id': 'choice', 'question': 'Choose strategy',
                       'options': ['A', 'B'], 'allow_free_text': True,
                       'kind': kind}])

    def test_default_waiting_and_eventual_timeout(self):
        self.assertEqual(self.flow.state['mode'], 'human')
        self.question()
        self.now = 160
        self.assertFalse(self.flow.timeout())
        self.now = 900
        self.assertTrue(self.flow.timeout())
        self.assertEqual(self.flow.state['mode'], 'dual-ai')
        self.assertFalse(self.flow.state['choice_visible'])
        self.assertEqual(self.flow.state['phase'], 'discussion')

    def test_restart_preserves_question_deadline(self):
        self.question()
        deadline = self.flow.state['deadline']
        self.now = 200
        again = self.api.Flow(self.root, 'FLOW-01', clock=lambda: self.now)
        self.assertEqual(again.state['deadline'], deadline)
        self.assertFalse(again.timeout())

    def test_no_question_means_no_timeout(self):
        self.now = 9000
        self.assertFalse(self.flow.timeout())
        self.assertEqual(self.flow.state['mode'], 'human')

    def test_human_answer_closes_prompt(self):
        self.question()
        self.flow.answer({'choice': 'more detail'})
        self.now = 9000
        self.assertFalse(self.flow.timeout())
        self.assertEqual(self.flow.state['answers']['choice'], 'more detail')

    def test_late_human_reply_invalidates_plan(self):
        self.question()
        self.now = 900
        self.flow.timeout()
        self.flow.answer({'choice': 'B'})
        self.assertEqual(self.flow.state['mode'], 'human')
        self.assertEqual(self.flow.state['phase'], 'discussion')
        self.assertEqual(self.flow.state['revision'], 2)

    def test_nonimplementation_decisions_cannot_be_delegated(self):
        for kind in ('business', 'permission', 'budget'):
            with self.subTest(kind=kind):
                self.flow.ask([{'id': kind, 'question': 'Approve?', 'options': ['yes','no'],
                               'kind': kind}])
                self.now += 600
                self.flow.timeout()
                with self.assertRaisesRegex(ValueError, 'human decision'):
                    self.flow.resolve_review({'answers': {kind: 'yes'}})

    def test_cancellation_prevents_advancement(self):
        self.question()
        self.flow.cancel()
        self.now = 900
        with self.assertRaises(ValueError):
            self.flow.answer({'choice': 'A'})
        self.assertFalse(self.flow.timeout())

    def test_stale_writer_rejected(self):
        other = self.api.Flow(self.root, 'FLOW-01', clock=lambda: self.now)
        self.question()
        with self.assertRaisesRegex(ValueError, 'changed'):
            other.cancel()

    def test_environment_routes_load_actual_skill_content(self):
        workflow = Path(__file__).resolve().parents[4]
        env = {'python': '3.12', 'cpu': 'Xeon', 'gpus': ['NVIDIA H20'],
               'cuda_toolkit': '12.4', 'driver': '550'}
        routes = self.api.load_environment_skills(workflow, env)
        self.assertIn('research-implement-optimize', [r['skill'] for r in routes])
        self.assertIn('gpu-experiment-dispatch', [r['skill'] for r in routes])
        self.assertTrue(all(r['content'] and r['sha256'] for r in routes))
        cpu = self.api.load_environment_skills(workflow, dict(env, gpus=[]))
        self.assertNotIn('gpu-experiment-dispatch', [r['skill'] for r in cpu])

    def test_missing_backend_is_blocked_not_done(self):
        self.question()
        self.now = 900
        self.flow.timeout()
        with self.assertRaisesRegex(ValueError, 'backend'):
            self.flow.review(None, {'question': 'strategy'})
        self.assertNotEqual(self.flow.state['phase'], 'done')

    def test_plan_requires_task_specific_tests(self):
        with self.assertRaisesRegex(ValueError, 'suite'):
            self.flow.plan({'summary': 'implement addition', 'steps': [{'id':'one','depends_on':[]}]}, self.root, 'agent')

    def test_state_path_rejects_traversal(self):
        with self.assertRaises(ValueError):
            self.api.Flow(self.root, '../escape')

    def setup_pipeline(self, *, bad=False):
        repo = Path(__file__).resolve().parents[4]
        workflow = self.root / 'workflow'
        (workflow / 'scripts').mkdir(parents=True)
        shutil.copy(repo / 'scripts/project_test.py', workflow / 'scripts/project_test.py')
        for source in ('config/role_registry.json',
                       'plugins/research-assistant/skills/research-implement-optimize/SKILL.md',
                       'plugins/research-assistant/skills/gpu-experiment-dispatch/SKILL.md'):
            dest = workflow / source
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(repo / source, dest)
        suite = workflow / 'agent_doc/agent/test/FLOW-01'
        suite.mkdir(parents=True)
        (suite / 'check.py').write_text("from pathlib import Path\nassert Path('answer.txt').read_text() == '42'\n")
        (suite / 'suite.json').write_text(json.dumps({'version': 1, 'origin': 'https://example.invalid/flow',
            'checks': [{'id':'answer','kind':'python','path':'check.py','timeout_seconds':5,'requirement':'exact answer 42'}]}))
        subprocess.run(['git','init','-q',str(self.root)], check=True)
        subprocess.run(['git','-C',str(self.root),'remote','add','origin','https://example.invalid/flow'], check=True)
        (self.root / '.gitignore').write_text('.agent-runs/\n__pycache__/\n')
        subprocess.run(['git','-C',str(self.root),'add','.gitignore'],check=True)
        subprocess.run(['git','-C',str(self.root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid',
                        'commit','-qm','fixture'],check=True)
        self.flow.plan({'summary': 'Write exact answer 42; verify through existing task check',
                       'steps': [{'id':'write','depends_on':[]}]},workflow,'agent')
        calls = []
        def implement(payload):
            calls.append(payload)
            (self.root / 'answer.txt').write_text('wrong' if bad else '42')
        host = SimpleNamespace(implement=implement)
        output = Path(self.temp.name + '-output')
        self.addCleanup(lambda: shutil.rmtree(output, ignore_errors=True))
        return host, output, calls, suite

    def test_human_pipeline_runs_real_task_acceptance(self):
        host, output, calls, _ = self.setup_pipeline()
        self.flow.execute(host, output)
        self.assertEqual(self.flow.state['phase'], 'done')
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0]['skills'][0]['content'])
        self.assertEqual(json.loads((output/'report.json').read_text())['checks'][0]['id'], 'answer')
        self.assertIn('Decision summary', (self.root/'agent_doc/task/task_details/FLOW-01.md').read_text())

    def test_wrong_implementation_reaches_repair_not_done(self):
        host, output, _, _ = self.setup_pipeline(bad=True)
        self.flow.execute(host, output)
        self.assertEqual(self.flow.state['phase'], 'repair')
        self.assertNotEqual(self.flow.state['acceptance']['returncode'], 0)

    def test_test_tampering_blocks_implementation(self):
        host, output, calls, suite = self.setup_pipeline()
        (suite/'check.py').write_text('pass')
        with self.assertRaisesRegex(ValueError, 'acceptance changed'):
            self.flow.execute(host, output)
        self.assertEqual(calls, [])

    def test_failed_host_action_is_not_replayed_after_restart(self):
        host, output, calls, _ = self.setup_pipeline()
        def crash(payload):
            raise RuntimeError('ambiguous side effect')
        host.implement = crash
        with self.assertRaises(RuntimeError):
            self.flow.execute(host, output)
        again = self.api.Flow(self.root, 'FLOW-01')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            again.execute(host, output)

    def test_dual_pipeline_uses_authenticated_checkpoints(self):
        host, output, calls, _ = self.setup_pipeline()
        self.flow.state['mode'] = 'dual-ai'
        self.flow.save()
        records, stages = {}, []
        planner = {'invocation_id':'main','context_id':'main','host_source':'fixture',
                   'provider_id':'fixture','model_id':'model-a'}
        host.planner_identity = lambda payload: planner
        host.reviewer_model_id = 'model-b'
        def review(request):
            from agent_runtime.plan_review import CHECKS, sha
            stages.append(request['payload']['stage'])
            review = {'full_review':'Synthetic authenticated fixture, not a model call',
                'verdict': {'decision':'approve','summary':'fixture','findings':[],
                'checks': {key:{'status':'pass','reason':'fixture'} for key in (*CHECKS,'spec_compliance','code_quality')}}}
            proof = str(len(records))
            records[proof] = {'request_sha256':sha(request),'review_sha256':sha(review),
                'planner':planner,'reviewer':dict(planner,invocation_id='review',context_id='review',model_id='model-b'),
                'fresh_context':True,'budget_valid':True}
            return {'review':review,'proof':proof}
        host.review = review
        host.authenticate = lambda request, review, proof: records[proof]
        self.flow.execute(host, output)
        self.assertEqual(self.flow.state['phase'], 'done')
        self.assertEqual(stages, ['acceptance-design','implementation'])

    def test_task_runner_rejects_path_traversal(self):
        host, output, _, _ = self.setup_pipeline()
        run = subprocess.run([sys.executable, str(self.root/'workflow/scripts/project_test.py'),
            '--workflow-root',str(self.root/'workflow'),'--target',str(self.root),'--project','agent',
            '--task','../escape','--output',str(output)],capture_output=True,text=True)
        self.assertEqual(run.returncode,2)
        self.assertFalse(output.exists())

    def test_status_cli_reads_persisted_mode(self):
        run = subprocess.run([sys.executable,'-m','agent_runtime.collaborative_flow',
            '--project-root',str(self.root),'--project','agent','--task-id','FLOW-01','--status'],
            capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout)['mode'],'human')

    def test_numeric_choice_through_real_pipe(self):
        self.question()
        reader, writer = os.pipe()
        os.write(writer, b'2\n')
        os.close(writer)
        with os.fdopen(reader) as stream:
            self.api.wait_for_human(self.flow, stream, lambda _: None)
        self.assertEqual(self.flow.state['answers']['choice'], 'B')

    def test_expired_prompt_closes_without_reading_disconnected_stdin(self):
        self.question()
        self.now = 900
        reader, writer = os.pipe()
        os.close(writer)
        with os.fdopen(reader) as stream:
            self.api.wait_for_human(self.flow, stream, lambda _: None)
        self.assertEqual(self.flow.state['mode'], 'dual-ai')

    def test_reasked_question_does_not_reuse_old_answer(self):
        self.question()
        self.flow.answer({'choice':'A'})
        self.question()
        self.assertNotIn('choice', self.flow.state['answers'])
        self.assertTrue(any(e.get('answers', {}).get('choice') == 'A' for e in self.flow.state['events']))

    def test_inflight_human_reply_is_saved_but_does_not_replay(self):
        self.question()
        self.flow.state['inflight'] = {'method':'implement'}
        self.flow.save()
        self.flow.answer({'choice':'B'})
        self.assertEqual(self.flow.state['phase'], 'blocked')
        self.assertEqual(self.flow.state['answers']['choice'], 'B')
        self.assertIn('inflight', self.flow.state)

    def test_real_cli_resumes_plan_and_runs_task_tests(self):
        _, output, _, _ = self.setup_pipeline()
        adapter = self.root / 'host.py'
        adapter.write_text("from types import SimpleNamespace\n"
            "def build(root, task_id):\n"
            "    def implement(payload):\n"
            "        (root/'answer.txt').write_text('42')\n"
            "    return SimpleNamespace(implement=implement)\n")
        run = subprocess.run([sys.executable,'-m','agent_runtime.collaborative_flow',
            '--project-root',str(self.root),'--workflow-root',str(self.root/'workflow'),
            '--project','agent','--task-id','FLOW-01','--adapter',str(adapter),'--output',str(output)],
            capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('人类-AI模式',run.stdout)
        self.assertEqual(self.api.Flow(self.root,'FLOW-01').state['phase'],'done')

    def test_two_step_task_chain_runs_in_dependency_order(self):
        host, output, calls, _ = self.setup_pipeline()
        self.flow.state['plan']['steps'].append({'id':'second','depends_on':['write']})
        self.flow.save()
        self.flow.execute(host,output)
        self.assertEqual([p['step']['id'] for p in calls],['write','second'])

    def test_missing_gpu_probe_does_not_invent_cuda(self):
        with patch('subprocess.run',side_effect=FileNotFoundError):
            environment = self.api.probe_environment()
        self.assertEqual(environment['gpus'],[])
        self.assertIsNone(environment['cuda_toolkit'])
        self.assertEqual(environment['gpu_probe'],'unavailable-or-unknown')

    def test_new_questions_cannot_drop_unresolved_human_decisions(self):
        self.question('permission')
        self.flow.ask([{'id':'strategy','question':'Choose','options':['A','B'],'kind':'implementation'}])
        self.assertIn('choice', [q['id'] for q in self.flow.state['questions']])
        with self.assertRaisesRegex(ValueError,'cannot be replaced'):
            self.question('implementation')


if __name__ == '__main__':
    unittest.main()
