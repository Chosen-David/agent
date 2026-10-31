"""Installed role text must stay validated through actual native/adapter dispatch."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'scripts/run_role.py').is_file())
TASK = '保留约束𐀀\n原始行尾\r\n'
SENTINEL = 'ROLE_LATE_TEXT_0500'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def fake_host():
    raw = sys.stdin.buffer.read()
    calls = Path('host-calls')
    if '--agents' in sys.argv:
        definition = next(iter(json.loads(sys.argv[sys.argv.index('--agents') + 1]).values()))
        task = raw.decode('utf-8')
        operation = 'native'
    else:
        request = json.loads(raw)
        operation = request['operation']
        if operation == 'inventory':
            with calls.open('ab') as stream: stream.write(b'inventory\n')
            policy = json.loads((ROOT / 'config/role_model_policy.json').read_text(encoding='utf-8'))
            print(json.dumps({'schema_version': 1, 'models': [{**policy['models']['opus'],
                             'available': True, 'transport': 'adapter', 'capabilities': ['tools', 'vision']}]}))
            return
        definition, task = request['definition'], request['prompt']
    with calls.open('ab') as stream: stream.write((operation + '\n').encode())
    row = {'task': task, 'model': definition['model'],
           'sentinel': SENTINEL in definition['prompt'],
           'definition_sha256': hashlib.sha256(definition['prompt'].encode()).hexdigest()}
    Path('host-marker.json').write_text(json.dumps(row), encoding='utf-8')
    print(json.dumps(row))


def run_child(project, role, kind, transport):
    runner = module('role_snapshot_runner', ROOT / 'scripts/run_role.py')
    installer = runner.bootstrap()
    original = installer.check

    def check(target):
        status = original(target)
        (project / 'stage.json').write_text(json.dumps(status), encoding='utf-8')
        if status['errors']:
            return status
        if role in ('planner-main', 'review-main'):
            relative = '.claude/agent-workflows/' + role.replace('-', '_') + '.md'
        elif kind.startswith('skill-'):
            relative = '.claude/skills/research-write/SKILL.md'
        else:
            relative = '.claude/agents/agent-research-write.md'
        path = project / relative
        text = SENTINEL if role in ('planner-main', 'review-main') or kind.startswith('skill-') else '---\nname: fixture\n---\n' + SENTINEL
        if kind in ('text', 'skill-text'):
            path.write_text(text, encoding='utf-8')
        elif kind == 'link':
            outside = project / 'changed-definition.md'
            outside.write_text(text, encoding='utf-8')
            path.unlink()
            path.symlink_to(outside)
        elif kind in ('fifo', 'skill-fifo'):
            path.unlink()
            os.mkfifo(path)
        return status

    installer.check = check
    runner.bootstrap = lambda: installer
    argv = ['run_role.py', '--project', str(project), '--role', role]
    prefix = '--adapter' if transport == 'adapter' else '--claude'
    argv += [prefix, sys.executable, prefix + '-arg', str(Path(__file__).resolve()), prefix + '-arg=--fixture-host']
    sys.argv = argv
    raise SystemExit(runner.main())


class RoleDefinitionTests(unittest.TestCase):
    def check_case(self, name, role, kind, transport='native', copy=True):
        temp = tempfile.TemporaryDirectory(prefix='role-snapshot-')
        project = Path(temp.name).resolve()
        row = {'case': name, 'transport': transport, 'project': str(project)}
        result = None
        try:
            if kind == 'link' or not copy:
                probe = project / 'link-probe'
                try:
                    probe.symlink_to(project, target_is_directory=True)
                    probe.unlink()
                except OSError as exc:
                    self.skipTest('host lacks symlink privileges: ' + str(exc))
            installer = module('snapshot_setup', ROOT / 'setup.py')
            installer.install(project, copy_skills=copy, model_inventory=installer.EMPTY_INVENTORY)
            argv = [sys.executable, '-B', str(Path(__file__).resolve()), '--fixture-child', str(project), role, kind, transport]
            try:
                result = subprocess.run(argv, input=TASK.encode(), capture_output=True, cwd=ROOT, timeout=15)
                row.update(returncode=result.returncode, timed_out=False,
                           stdout=result.stdout.decode('utf-8'), stderr=result.stderr.decode('utf-8'))
            except subprocess.TimeoutExpired as exc:
                row.update(returncode=None, timed_out=True,
                           stdout=(exc.stdout or b'').decode('utf-8'), stderr=(exc.stderr or b'').decode('utf-8'))
            stage = json.loads((project / 'stage.json').read_text(encoding='utf-8'))
            row['stage'] = {'status': stage['status'], 'errors': stage['errors']}
            row['calls'] = (project / 'host-calls').read_text().splitlines() if (project / 'host-calls').exists() else []
            row['marker'] = json.loads((project / 'host-marker.json').read_text(encoding='utf-8')) if (project / 'host-marker.json').exists() else None
            self.assertEqual(row['stage'], {'status': 'configured', 'errors': []})
            self.assertFalse(row['timed_out'], row)
            if kind == 'none':
                self.assertEqual(result.returncode, 0, row)
                self.assertEqual(row['marker']['task'], TASK)
                self.assertEqual(row['marker']['model'], 'inherit')
                self.assertFalse(row['marker']['sentinel'])
                self.assertEqual(row['calls'], ['inventory', 'run'] if transport == 'adapter' else ['native'])
                if transport == 'adapter':
                    self.assertIn('\"transport\": \"adapter\"', row['stderr'])
            else:
                self.assertEqual(result.returncode, 2, row)
                self.assertEqual(row['calls'], [], row)
                self.assertIsNone(row['marker'], row)
        finally:
            # Do not infer cleanup from the context manager's return value.
            temp.cleanup()
            row['cleanup_absent'] = not os.path.lexists(project)
            evidence = os.environ.get('ROLE_SNAPSHOT_EVIDENCE')
            if evidence:
                with (Path(evidence) / (name + '-' + transport + '.json')).open('x', encoding='utf-8') as stream:
                    json.dump(row, stream, ensure_ascii=False, indent=2)
            self.assertTrue(row['cleanup_absent'], row)

    def test_healthy_copy_and_declared_link(self):
        for copy, transport in [(True, 'native'), (False, 'adapter')]:
            with self.subTest(copy=copy, transport=transport):
                self.check_case('healthy-copy' if copy else 'healthy-link', 'research-write', 'none', transport, copy)

    def test_changed_text_never_discovers_or_launches_backend(self):
        for role, kind in [('planner-main', 'text'), ('review-main', 'text'), ('research-write', 'text'), ('research-write', 'skill-text')]:
            for transport in ('native', 'adapter'):
                with self.subTest(role=role, kind=kind, transport=transport):
                    self.check_case(role + '-' + kind, role, kind, transport)

    def test_redirected_agent_never_discovers_or_launches_backend(self):
        for transport in ('native', 'adapter'):
            with self.subTest(transport=transport):
                self.check_case('agent-link', 'research-write', 'link', transport)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_is_rejected_without_blocking_or_backend_calls(self):
        for kind in ('fifo', 'skill-fifo'):
            for transport in ('native', 'adapter'):
                with self.subTest(kind=kind, transport=transport):
                    self.check_case('agent-' + kind, 'research-write', kind, transport)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--fixture-host':
        fake_host()
    elif len(sys.argv) > 1 and sys.argv[1] == '--fixture-child':
        run_child(Path(sys.argv[2]), *sys.argv[3:6])
    else:
        unittest.main()
