# Legacy fixture: exercises pre-dual-main invariants; independent review is tested separately.
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
from unittest.mock import patch

from agent_runtime.core import Store
from agent_runtime.task_manifest import atomic_json, prepare
from agent_runtime.task_supervisor import TMUX_SOCKET, start, status, tmux

class GuardCrashPolicyTests(unittest.TestCase):
    def test_guard_stops_rebuilding_after_three_crashes_and_after_restart(self):
        from unittest.mock import Mock,patch
        from agent_runtime.task_supervisor import guard
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);state=root/'run';state.mkdir()
            config=root/'launch.json'
            atomic_json(config,{'project_root':str(root),'state_dir':str(state),'run_id':'run'})
            store=Mock()
            store.snapshot.side_effect=[{'state':{'status':s}} for s in ['running']*4+['cancelled']]
            with patch.dict(os.environ,{'TMUX':'explicit-test'}),patch('agent_runtime.task_supervisor.Store',return_value=store),patch('agent_runtime.task_supervisor.subprocess.run',return_value=Mock(returncode=1)) as run,patch('agent_runtime.task_supervisor.time.sleep') as sleep:
                guard(config)
                self.assertEqual(run.call_count,3)
                self.assertEqual([c.args[0] for c in sleep.call_args_list],[5,10,30])
            store.snapshot.side_effect=[{'state':{'status':s}} for s in ['running','cancelled']]
            with patch.dict(os.environ,{'TMUX':'explicit-test'}),patch('agent_runtime.task_supervisor.Store',return_value=store),patch('agent_runtime.task_supervisor.subprocess.run') as run,patch('agent_runtime.task_supervisor.time.sleep'):
                guard(config);run.assert_not_called()

ROOT = Path(__file__).resolve().parents[1]


class ProcessIdentityTests(unittest.TestCase):
    def fixture(self):
        value = WorkerTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        return value

    def proc_view(self, value):
        from unittest.mock import mock_open
        original = open
        def open_status(path, *args, **kwargs):
            if os.fspath(path) == '/proc/self/status':
                if isinstance(value, Exception):
                    raise value
                return mock_open(read_data=value)(path, *args, **kwargs)
            return original(path, *args, **kwargs)
        return patch('builtins.open', side_effect=open_status)

    def invalid_proc_views(self):
        pid = str(os.getpid()).encode()
        return (b'NStgid:\t999999999\n', b'NStgid:\tnot-a-pid\n', FileNotFoundError(),
                b'NStgid:\t999999999\t' + pid + b'\n',
                b'NStgid:\t' + pid + b'\t' + pid + b'\n', b'Name:\tpython\n',
                b'NStgid:\n', (b'NStgid:\t' + pid + b'\n') * 2)

    def test_worker_rejects_unverifiable_pid_namespace_before_backend(self):
        from agent_runtime.task_supervisor import worker
        from unittest.mock import Mock
        value = self.fixture()
        backend = Mock(side_effect=RuntimeError('backend reached'))
        for namespace in self.invalid_proc_views():
            with self.subTest(namespace=namespace), self.proc_view(namespace), \
                 patch.dict(os.environ, {'TMUX': 'explicit-test-marker'}), \
                 patch('agent_runtime.task_supervisor.load_backend', backend):
                with self.assertRaisesRegex(RuntimeError, 'PID namespace'):
                    worker(value.config)
                backend.assert_not_called()
        with self.proc_view(b'NStgid:\t' + str(os.getpid()).encode() + b'\n'), \
             patch.dict(os.environ, {'TMUX': 'explicit-test-marker'}), \
             patch('agent_runtime.task_supervisor.load_backend', backend):
            with self.assertRaisesRegex(RuntimeError, 'backend reached'):
                worker(value.config)
        self.assertEqual(backend.call_count, 1)

    def test_status_rejects_foreign_proc_view_before_numeric_pid_lookup(self):
        value = self.fixture()
        atomic_json(value.state_dir / 'live.json', {
            'run_id': value.plan['run_id'], 'session': 'fixture', 'pid': os.getpid(),
            'heartbeat_at': time.time(), 'service_id': 's', 'starttime': '123'})
        for namespace in self.invalid_proc_views():
            with self.subTest(namespace=namespace), self.proc_view(namespace), \
                 patch('agent_runtime.task_supervisor.tmux', return_value=subprocess.CompletedProcess([], 0, '0\n', '')), \
                 patch('agent_runtime.task_supervisor.read_process_starttime', return_value='123') as read_identity:
                self.assertFalse(status(value.config)['live'])
                read_identity.assert_not_called()
        with self.proc_view(b'NStgid:\t' + str(os.getpid()).encode() + b'\n'), \
             patch('agent_runtime.task_supervisor.tmux', return_value=subprocess.CompletedProcess([], 0, '0\n', '')), \
             patch('agent_runtime.task_supervisor.read_process_starttime', return_value='123'):
            self.assertTrue(status(value.config)['live'])

    @unittest.skipUnless(sys.platform == 'linux', 'requires Linux procfs and PR_SET_NAME')
    def test_starttime_survives_arbitrary_process_name_bytes(self):
        body = r'''
import ctypes, json, os, sys
from pathlib import Path
from agent_runtime.task_supervisor import read_process_starttime
name = bytes.fromhex(sys.argv[1])
libc = ctypes.CDLL(None, use_errno=True)
if libc.prctl(15, ctypes.c_char_p(name), 0, 0, 0) != 0:
    raise OSError(ctypes.get_errno(), 'PR_SET_NAME')
raw = Path('/proc/self/stat').read_bytes()
# /proc can expose a parent namespace; query this process in that mount's view.
pid = int(raw.split(b' ', 1)[0])
expected = raw.rsplit(b')', 1)[1].split()[19].decode('ascii')
print(json.dumps({'actual': read_process_starttime(pid), 'expected': expected,
                  'name_hex': name.hex(), 'pid': pid, 'namespace_pid': os.getpid()}))
'''
        for name in (b'python', b'a) space', '测试) x'.encode(), b'n\xff) x'):
            with self.subTest(name=name):
                child = subprocess.run([sys.executable, '-B', '-c', body, name.hex()],
                                       cwd=ROOT, capture_output=True, text=True, timeout=5)
                self.assertEqual(child.returncode, 0, child.stderr)
                result = json.loads(child.stdout)
                self.assertEqual(result['actual'], result['expected'], result)

    def test_starttime_rejects_missing_or_invalid_numeric_field(self):
        from unittest.mock import mock_open
        from agent_runtime.task_supervisor import read_process_starttime
        prefix = b'123 (name) space) S ' + b'0 ' * 18
        for raw in (b'123 (short) S 0', prefix + b'\xff', prefix + b'-1', prefix + b'123x'):
            def open_stat(path, mode, **kwargs):
                data = raw if 'b' in mode else raw.decode(kwargs.get('encoding', 'utf-8'))
                return mock_open(read_data=data)(path, mode)
            with self.subTest(raw=raw), patch('builtins.open', side_effect=open_stat):
                self.assertIsNone(read_process_starttime(123))
        with patch('builtins.open', side_effect=ProcessLookupError):
            self.assertIsNone(read_process_starttime(123))


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
        self.plan = prepare(self.file, 'worker-fixture', 'manual', 'unit-test', review_required=False)
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
                       'project_root': str(self.root), 'session': 'fixture', 'adapter': None, 'allow_legacy': True}
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

    def require_process_namespace(self):
        try:
            rows = [line.split()[1:] for line in Path('/proc/self/status').read_bytes().splitlines()
                    if line.startswith(b'NStgid:')]
            matched = rows == [[str(os.getpid()).encode()]]
        except (OSError, ValueError):
            matched = False
        if not matched:
            reason = 'worker integration requires matching /proc and process PID namespaces'
            if os.environ.get('AGENT_REQUIRE_NATIVE_PROC') == '1':
                self.fail(reason)
            self.skipTest(reason)

    def launch(self, command='_worker', marker=True):
        if marker:
            self.require_process_namespace()
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

    def test_status_treats_malformed_live_snapshot_as_not_live(self):
        live = self.state_dir / 'live.json'
        for payload in ('[]', '{"pid":"wrong","heartbeat_at":0}',
                        '{"run_id":"worker-fixture","session":"fixture",'
                        '"pid":1,"heartbeat_at":"wrong"}'):
            with self.subTest(payload=payload):
                live.write_text(payload)
                with patch('agent_runtime.task_supervisor.tmux') as mocked_tmux:
                    mocked_tmux.return_value = subprocess.CompletedProcess([], 0, '0\n', '')
                    self.assertFalse(status(self.config)['live'])

    def test_status_verifies_worker_process_identity_against_pid_reuse(self):
        self.require_process_namespace()
        from agent_runtime.task_supervisor import read_process_starttime
        starttime = read_process_starttime(os.getpid())
        self.assertIsNotNone(starttime)
        self.assertIsNone(read_process_starttime(999999999))
        live = self.state_dir / 'live.json'
        base = {'run_id': self.plan['run_id'], 'session': 'fixture',
                'pid': os.getpid(), 'heartbeat_at': time.time(), 'service_id': 's'}
        # A fresh heartbeat whose recorded starttime belongs to another process is
        # rejected: it is a recycled PID, not the worker that wrote live.json.
        live.write_text(json.dumps({**base, 'starttime': 'not-this-process'}))
        with patch('agent_runtime.task_supervisor.tmux') as mocked_tmux:
            mocked_tmux.return_value = subprocess.CompletedProcess([], 0, '0\n', '')
            self.assertFalse(status(self.config)['live'])
        # The same heartbeat with the current process's own starttime is accepted.
        live.write_text(json.dumps({**base, 'starttime': starttime}))
        with patch('agent_runtime.task_supervisor.tmux') as mocked_tmux:
            mocked_tmux.return_value = subprocess.CompletedProcess([], 0, '0\n', '')
            self.assertTrue(status(self.config)['live'])

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
        # Kill at a settled pending observation, not the random interval between
        # durable claim and outcome. Live leases must remain fenced after crashes.
        wait_for(lambda: (node.get('pending_polls', 0) > 0 and node['status'] == 'todo' and node.get('token') is None)
                 if (node := self.store.snapshot(self.plan['run_id'])['state']['tasks']['T1']) else False)
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
            plan = prepare(source, 'real-tmux-test', 'auto', 'explicit test', review_required=False)
            plan['supervision'].update(min_seconds=1, max_seconds=2)
            task = plan['tasks'][0]
            task.update(action='verify_artifacts', max_attempts=20, estimated_seconds=1)
            task['done_when'] = {'artifacts': [{'path': 'proof', 'sha256': hashlib.sha256(b'ok').hexdigest()}]}
            atomic_json(root / task['report_path'], {'task_id': 'T1', 'summary': 'tmux fixture',
                        'data': [{'kind': 'synthetic', 'description': 'deterministic test'}]})
            plan_path = root / 'plan.json'; atomic_json(plan_path, plan)
            state_dir = root / 'run'
            command = [sys.executable, '-m', 'agent_runtime.task_supervisor', 'start', '--legacy-unprotected',
                       '--plan', str(plan_path), '--project-root', str(root), '--state-dir', str(state_dir)]
            config = None
            try:
                launcher = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=12)
                self.assertEqual(launcher.returncode, 0, launcher.stderr)
                receipt = json.loads(launcher.stdout)
                self.assertEqual(receipt['status'], 'started')
                config = json.loads((state_dir / 'launch.json').read_text())
                again = start(plan_path, root, state_dir, allow_legacy=True)
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
