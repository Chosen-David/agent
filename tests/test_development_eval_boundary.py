"""Execute CLI routing boundaries; ordinary runtime never opens evaluation material."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DevelopmentBoundaryTests(unittest.TestCase):
    def command(self, *args, **kwargs):
        return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                              capture_output=True, text=True, **kwargs)

    def test_preparation_requires_explicit_flag_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'absent'
            for script, args in [('agent_eval_pipeline.py', ['prepare', '--revision', 'HEAD']),
                                 ('prepare_agent_eval.py', [])]:
                result = self.command(ROOT/'scripts'/script, *args, '--out', dest)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('--dev-eval', result.stderr)
                self.assertFalse(dest.exists())

    def test_developer_prepare_and_snapshot_dependency_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'run'
            result = self.command(ROOT/'scripts/agent_eval_pipeline.py', 'prepare', '--dev-eval',
                                  '--revision', 'HEAD', '--out', dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest/'manifest.json').is_file())
            # Real import in the pinned snapshot catches transitive dependency gaps.
            probe = self.command(dest/'snapshot/scripts/validate_paper_delivery.py', '--help')
            self.assertEqual(probe.returncode, 0, probe.stderr)
            self.assertTrue((dest/'snapshot/scripts/data_visualization_checks.py').is_file())

    def test_legacy_explicit_development_case_prepares(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'legacy'
            result = self.command(ROOT/'scripts/prepare_agent_eval.py', '--dev-eval',
                                  '--case', 'research-write', '--out', dest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest/'research-write/inputs/measurements.csv').is_file())

    def test_ordinary_artifact_task_never_reads_or_executes_eval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'artifact.txt').write_text('ordinary user result')
            plan = json.loads((ROOT/'templates/task_dag.json').read_text())
            plan['run_id'] = 'ordinary-task'
            plan['user_goal'] = 'Test and verify my actual result artifact; ordinary user task'
            plan['tasks'][0]['outputs'] = ['artifact.txt']
            plan['tasks'][0]['done_when']['artifacts'] = [dict(path='artifact.txt',
                sha256=hashlib.sha256((root/'artifact.txt').read_bytes()).hexdigest())]
            (root/'plan.json').write_text(json.dumps(plan))
            # Run the actual CLI under a Python audit hook. Any benchmark input,
            # hidden rubric or evaluation runner access is a test failure.
            guard = """
import sys, runpy
from pathlib import Path
repo = Path(sys.argv[1]); args = sys.argv[2:]
sys.path.insert(0, str(repo))
def audit(event, arguments):
    if event == 'open' and isinstance(arguments[0], (str, bytes)):
        path = str(arguments[0])
        if '/evals/' in path or any(s in path for s in ('agent_eval_pipeline', 'prepare_agent_eval', 'rubric.json')):
            raise RuntimeError('ordinary runtime touched evaluation material: ' + path)
sys.addaudithook(audit)
sys.argv = ['agent_runtime'] + args
runpy.run_module('agent_runtime', run_name='__main__')
"""
            for args in [['init', str(root/'plan.json')],
                         ['tick', 'ordinary-task', '--artifact-root', str(root), '--event-id', 'ordinary-1']]:
                result = self.command('-c', guard, ROOT, '--db', root/'state.sqlite', *args)
                self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(result.stdout)
            self.assertEqual(state['status'], 'done')
            self.assertFalse((root/'evals').exists())
            self.assertFalse((root/'manifest.json').exists())
            self.assertEqual((root/'artifact.txt').read_text(), 'ordinary user result')


if __name__ == '__main__':
    unittest.main()
