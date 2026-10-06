"""Real worker subprocess/SQLite tests with a simulated tmux environment marker.

The container may prohibit Unix sockets. These do NOT prove tmux/SSH survival.
A separate opt-in real-tmux integration test below covers that host capability.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from agent_runtime.core import Store
from agent_runtime.task_manifest import atomic_json, prepare
from agent_runtime.task_supervisor import TMUX_SOCKET, start, status, tmux

ROOT = Path(__file__).resolve().parents[1]


def wait_for(predicate, seconds=8):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.05)
    raise AssertionError('condition did not become true within deadline')


class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='supervisor space ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / 'TASK.md'
        self.file.write_text('- [ ] [T1] Produce artifact\n')
        self.plan = prepare(self.file, 'worker-fixture', 'manual', 'unit-test')
        self.plan['supervision'].update(min_seconds=1, max_seconds=2)
        task = self.plan['tasks'][0]
        task.update(action='verify_artifacts', max_attempts=20, estimated_seconds=1)
        task['done_when'] = {'artifacts': [{'path': 'result.txt', 'sha256': hashlib.sha256(b'ok').hexdigest()}]}
        atomic_json(self.root / task['report_path'], {'task_id': 'T1', 'summary': 'fixture',
                    'data': [{'kind': 'synthetic', 'description': 'local test bytes'}]})
        self.state_dir = self.root / 'run'
        self.store = Store(self.state_dir / 'state.sqlite')
        self.store.create(self.plan)
        self.config = {'run_id': self.plan['run_id'], 'state_dir': str(self.state_dir),
                       'project_root': str(self.root), 'session': 'fixture', 'adapter': None}
        self.config_path = self.state_dir / 'launch.json'
        atomic_json(self.config_path, self.config)
        self.children = []
        self.addCleanup(self.stop_children)

    def stop_children(self):
        for child in self.children:
            if child.poll() is None:
                child.terminate()
                try: child.wait(timeout=4)
                except subprocess.TimeoutExpired: child.kill(); child.wait()
            child.stdout.close()
            child.stderr.close()

    def launch(self, command='_worker', marker=True):
        env = dict(os.environ)
        if marker: env['TMUX'] = 'explicit-unit-test-fixture'
        else: env.pop('TMUX', None)
        child = subprocess.Popen([sys.executable, '-m', 'agent_runtime.task_supervisor', command,
                                  '--config', str(self.config_path)], cwd=ROOT, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.children.append(child)
        return child

    def test_worker_requires_tmux_marker(self):
        child = self.launch(marker=False)
        child.wait(timeout=3)
        self.assertNotEqual(child.returncode, 0)
        self.assertIn('must run inside tmux', child.stderr.read())

    def test_worker_reports_result_and_stops_only_owned_monitor(self):
        child = self.launch()
        wait_for(lambda: self.store.snapshot(self.plan['run_id'])['monitor'])
        (self.root / 'result.txt').write_bytes(b'ok')
        final = self.state_dir / 'final-report.json'
        wait_for(final.exists)
        child.wait(timeout=4)
        self.assertEqual(child.returncode, 0, child.stderr.read())
        report = json.loads(final.read_text())
        self.assertTrue(report['all_reportable'])
        self.assertEqual(report['remaining'], [])
        self.assertEqual(report['monitor']['status'], 'stopped')
        self.assertFalse((self.state_dir / 'live.json').exists())

    def test_source_edit_keeps_owner_alive_without_dispatching_old_plan(self):
        self.file.write_text(self.file.read_text() + '- [ ] [T2] New requirement\n')
        child = self.launch()
        progress = self.state_dir / 'progress.json'
        wait_for(progress.exists)
        report = json.loads(progress.read_text())
        self.assertIn('T2', report['remaining'])
        self.assertTrue(report['source_error'])
        self.assertEqual(self.store.snapshot(self.plan['run_id'])['state']['tasks']['T1']['attempts'], 0)
        self.assertIsNone(child.poll())
        self.store.cancel(self.plan['run_id'], 'test stop')
        child.wait(timeout=4)
        self.assertFalse((self.state_dir / 'final-report.json').exists())

    def test_failed_task_keeps_supervisor_alive_for_main_ai_recovery(self):
        with self.store.transaction() as db:
            _, state = self.store.load(db, self.plan['run_id'])
            state['status'] = 'failed'; state['tasks']['T1']['status'] = 'failed'
            self.store.save(db, self.plan['run_id'], state)
        child = self.launch()
        wait_for((self.state_dir / 'progress.json').exists)
        self.assertIsNone(child.poll())
        self.assertFalse((self.state_dir / 'final-report.json').exists())
        self.store.cancel(self.plan['run_id'], 'test stop')
        child.wait(timeout=4)

    def test_guard_restarts_killed_worker_and_reuses_durable_state(self):
        child = self.launch('_guard')
        live = self.state_dir / 'live.json'
        first_pid = wait_for(lambda: json.loads(live.read_text())['pid'] if live.exists() else None)
        os.kill(first_pid, signal.SIGKILL)
        second_pid = wait_for(lambda: (p if (p := json.loads(live.read_text())['pid']) != first_pid else None)
                             if live.exists() else None, 10)
        self.assertNotEqual(first_pid, second_pid)
        (self.root / 'result.txt').write_bytes(b'ok')
        wait_for((self.state_dir / 'final-report.json').exists)
        child.wait(timeout=4)
        self.assertEqual(child.returncode, 0)
        self.assertIn('restart in 5 seconds', (self.state_dir / 'supervisor.log').read_text())

    def test_trusted_main_ai_maintenance_receives_failed_task_report(self):
        adapter = self.root / 'adapter.py'
        adapter.write_text('''from pathlib import Path
import json
def build(root, store, run_id):
    def maintain(report):
        (Path(root) / 'maintenance.json').write_text(json.dumps(report))
    return {'handlers': {}, 'authorize': lambda *_: False, 'maintain': maintain}
''')
        self.config['adapter'] = str(adapter)
        atomic_json(self.config_path, self.config)
        with self.store.transaction() as db:
            _, state = self.store.load(db, self.plan['run_id'])
            state['status'] = 'failed'; state['tasks']['T1']['status'] = 'failed'
            self.store.save(db, self.plan['run_id'], state)
        child = self.launch()
        path = self.root / 'maintenance.json'
        wait_for(path.exists)
        report = json.loads(path.read_text())
        self.assertEqual(report['remaining'], ['T1'])
        self.assertEqual(report['requirements'][0]['nodes'][0]['owner'], 'main-ai')
        self.assertIsNone(child.poll())
        self.store.cancel(self.plan['run_id'], 'test stop')
        child.wait(timeout=4)

    def test_cancel_stops_guard_even_when_adapter_cannot_load(self):
        self.config['adapter'] = str(self.root / 'missing-adapter.py')
        atomic_json(self.config_path, self.config)
        child = self.launch('_guard')
        wait_for((self.state_dir / 'supervisor.log').exists)
        self.store.cancel(self.plan['run_id'], 'test stop')
        child.wait(timeout=7)
        self.assertEqual(child.returncode, 0)


@unittest.skipUnless(os.environ.get('AGENT_TEST_REAL_TMUX') == '1',
                     'opt-in: requires working tmux server/Unix sockets on host')
class RealTmuxTests(unittest.TestCase):
    def test_detached_start_idempotence_and_completion_after_launcher_exit(self):
        with tempfile.TemporaryDirectory(prefix='real-tmux-fixture ') as directory:
            root = Path(directory)
            source = root / 'TASK.md'; source.write_text('- [ ] [T1] Test detached completion\n')
            plan = prepare(source, 'real-tmux-test', 'auto', 'explicit test')
            plan['supervision'].update(min_seconds=1, max_seconds=2)
            task = plan['tasks'][0]
            task.update(action='verify_artifacts', max_attempts=20, estimated_seconds=1)
            task['done_when'] = {'artifacts': [{'path': 'proof', 'sha256': hashlib.sha256(b'ok').hexdigest()}]}
            atomic_json(root / task['report_path'], {'task_id': 'T1', 'summary': 'tmux fixture',
                        'data': [{'kind': 'synthetic', 'description': 'deterministic test'}]})
            plan_path = root / 'plan.json'; atomic_json(plan_path, plan)
            state_dir = root / 'run'
            command = [sys.executable, '-m', 'agent_runtime.task_supervisor', 'start',
                       '--plan', str(plan_path), '--project-root', str(root), '--state-dir', str(state_dir)]
            config = None
            try:
                launcher = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=12)
                self.assertEqual(launcher.returncode, 0, launcher.stderr)
                receipt = json.loads(launcher.stdout)
                self.assertEqual(receipt['status'], 'started')
                config = json.loads((state_dir / 'launch.json').read_text())
                again = start(plan_path, root, state_dir)
                self.assertEqual(again['status'], 'already_running')
                self.assertEqual(receipt['session'], again['session'])
                self.assertTrue(status(config)['live'])
                (root / 'proof').write_bytes(b'ok')
                wait_for((state_dir / 'final-report.json').exists)
                wait_for(lambda: tmux('has-session', '-t', '=' + receipt['session'], check=False).returncode != 0)
                self.assertTrue(json.loads((state_dir / 'final-report.json').read_text())['all_reportable'])
            finally:
                if config:
                    Store(state_dir / 'state.sqlite').cancel(plan['run_id'], 'test cleanup')
                    tmux('kill-session', '-t', '=' + config['session'], check=False)
