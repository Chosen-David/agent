"""Single-main installation and durable step ownership, without model calls."""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from agent_runtime.core import Engine, Outcome, Store

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('serial_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def plan():
    return {'schema_version': 'task-dag/v1', 'run_id': 'serial',
            'user_goal': 'Two skill steps, one main', 'authorization_reference': 'fixture',
            'supervision': {'min_seconds': 1, 'max_seconds': 2, 'rationale': 'bounded fixture'},
            'tasks': [{'task_id': name, 'action': 'step', 'owner': 'main',
                       'done_when': {'verified': True}, 'depends_on': [],
                       'max_attempts': 3, 'estimated_seconds': 1, 'risk': 'low'}
                      for name in ('A', 'B')]}


class SingleMainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_install_skills_without_subagent_entries(self):
        result = setup.install(self.root)
        self.assertEqual(result['skills'], len(setup.catalog()))
        self.assertEqual(result['subagents'], 0)
        self.assertEqual(list(self.root.glob('.claude/agents/agent-*.md')), [])
        self.assertIn('single_main_workflow.md', (self.root / 'CLAUDE.md').read_text(encoding='utf-8'))

    def legacy_entry(self, edited=False):
        setup.install(self.root)
        path = self.root / '.claude/agents/agent-research-write.md'
        path.parent.mkdir(exist_ok=True)
        path.write_text('old owned role\n')
        manifest = self.root / '.claude/agent-workflows/installation.json'
        data = json.loads(manifest.read_text(encoding='utf-8'))
        data['files'][path.relative_to(self.root).as_posix()] = setup.sha(path.read_text(encoding='utf-8'))
        manifest.write_text(json.dumps(data))
        if edited:
            path.write_text('user edits\n')
        return path

    def test_upgrade_removes_only_unchanged_owned_agent(self):
        old = self.legacy_entry()
        custom = old.with_name('my-agent.md')
        custom.write_text('custom\n')
        self.assertEqual(setup.install(self.root)['status'], 'configured')
        self.assertFalse(old.exists())
        self.assertEqual(custom.read_text(encoding='utf-8'), 'custom\n')

    def test_upgrade_rejects_edited_owned_agent_before_writes(self):
        old = self.legacy_entry(edited=True)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*')
                  if p.is_file() and not p.is_symlink()}
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            setup.install(self.root)
        self.assertEqual(old.read_text(encoding='utf-8'), 'user edits\n')
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*')
                                  if p.is_file() and not p.is_symlink()})

    def test_obsolete_manifest_cannot_redirect_cleanup_into_guide(self):
        setup.install(self.root)
        manifest = self.root / '.claude/agent-workflows/installation.json'
        data = json.loads(manifest.read_text(encoding='utf-8'))
        data['files']['.claude/agents/agent-x/../../../agent_doc/guide/GUIDE.md'] = '0' * 64
        manifest.write_text(json.dumps(data))
        before = manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, 'unknown obsolete'):
            setup.install(self.root)
        self.assertEqual(manifest.read_bytes(), before)
        self.assertEqual(list((self.root / 'agent_doc/guide').iterdir()), [])

    def engine(self, store, handler, clock=lambda: 1):
        return Engine(store, {'step': handler}, authorize=lambda *_: True,
                      allow_legacy=True, clock=clock)

    def test_simultaneous_ticks_cannot_enter_second_step(self):
        store = Store(self.root / 'state.sqlite')
        store.create(plan())
        entered, release, calls = threading.Event(), threading.Event(), []

        class Handler:
            idempotent = False
            def run(self, task, context):
                calls.append(task['task_id'])
                if task['task_id'] == 'A':
                    entered.set()
                    if not release.wait(10):
                        raise RuntimeError('fixture release timeout')
                return Outcome('complete', evidence=['verified'])
            def verify(self, task, evidence):
                return evidence == ['verified']

        engine = self.engine(store, Handler())
        errors = []
        def first():
            try:
                engine.tick('serial', 'first')
            except BaseException as exc:
                errors.append(exc)
        thread = threading.Thread(target=first)
        thread.start()
        try:
            self.assertTrue(entered.wait(10))
            second = self.engine(Store(store.path), Handler()).tick('serial', 'second')
            self.assertEqual(calls, ['A'])
            self.assertEqual(second['tasks']['B']['attempts'], 0)
        finally:
            release.set()
            thread.join(10)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(self.engine(Store(store.path), Handler()).tick('serial', 'third')['status'], 'done')
        self.assertEqual(calls, ['A', 'B'])

    def test_pending_step_survives_restart_before_next_skill(self):
        store = Store(self.root / 'state.sqlite')
        store.create(plan())
        calls, now = [], [1]
        class Handler:
            idempotent = False
            def run(self, task, context):
                calls.append(task['task_id'])
                return Outcome('pending') if len(calls) == 1 else Outcome('complete', evidence=['verified'])
            def verify(self, task, evidence):
                return evidence == ['verified']
        self.engine(store, Handler(), lambda: now[0]).tick('serial', 'pending')
        restarted = self.engine(Store(store.path), Handler(), lambda: now[0])
        restarted.tick('serial', 'too-early')
        self.assertEqual(calls, ['A'])
        now[0] = 5
        restarted.tick('serial', 'poll')
        self.assertEqual(calls, ['A', 'A'])
        restarted.tick('serial', 'next')
        self.assertEqual(calls, ['A', 'A', 'B'])

    def test_actual_skill_loader_has_no_backend(self):
        for copy in (False, True):
            with self.subTest(copy=copy):
                project = self.root / ('copy' if copy else 'link')
                project.mkdir()
                setup.install(project, copy_skills=copy)
                run = subprocess.run([sys.executable, str(ROOT / 'scripts/load_skill.py'),
                                      '--project', str(project), '--skill', 'research-write'],
                                     capture_output=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stderr.decode())
                result = json.loads(run.stdout)
                self.assertEqual(result['execution_mode'], 'single-main')
                self.assertFalse(result['launched'])
                self.assertIn('research-write', result['skill'])
                self.assertIn('SKILL.md', result['source'])
                self.assertIn('论文', result['content'])
                expected = (ROOT / 'plugins/research-assistant/skills/research-write/SKILL.md').read_text(encoding='utf-8')
                self.assertEqual(result['content'], expected)
                self.assertEqual(result.get('content_sha256'), hashlib.sha256(expected.encode('utf-8')).hexdigest())
