"""Literal TASK coverage and navigation share the top-level fence contract."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_docs import parse_requirements, snapshot_project_docs
from agent_runtime.task_context import task_view
from agent_runtime.task_manifest import prepare


class TaskFenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.path = self.root / 'agent_doc/task/TASK.md'
        self.path.parent.mkdir(parents=True)

    @staticmethod
    def row(identity):
        return f'- [ ] [{identity}] Required {identity} ([detail](task_details/{identity}.md))'

    def bind(self, chunks):
        raw = ''.join(chunks).encode('utf-8')
        self.path.write_bytes(raw)
        return raw, hashlib.sha256(raw).hexdigest()

    def assert_index(self, chunks, expected, selected, omitted):
        raw, sha = self.bind(chunks)
        for canonical in (False, True):
            with self.subTest(stage='parse', canonical=canonical):
                self.assertEqual([t['id'] for t in parse_requirements(raw.decode(), canonical=canonical)], expected)
        with self.subTest(stage='view'):
            view = task_view(self.root, selected, sha)
            kept = [i for i in range(len(chunks)) if i not in omitted]
            self.assertEqual(view['text'], ''.join(chunks[i] for i in kept))
            self.assertEqual(view['source_lines'], [i + 1 for i in kept])
            self.assertEqual(view['omitted_task_rows'], len(omitted))
            self.assertEqual(view['source'], {'path': 'agent_doc/task/TASK.md', 'sha256': sha})
        self.assertEqual(self.path.read_bytes(), raw)

    def test_non_fence_prefixes_cannot_hide_required_rows(self):
        for ending in ('\n', '\r\n', '\r'):
            for token in ('```', '~~~'):
                for prefix in ('    ', '\t', '\u00a0', '\u2028'):
                    with self.subTest(ending=repr(ending), token=token, prefix=repr(prefix)):
                        chunks = [s + ending for s in ('## 2026-10-27', self.row('KEEP'), '',
                            prefix + token, self.row('CORRECT'), prefix + token, self.row('NEXT'))]
                        self.assert_index(chunks, ['KEEP', 'CORRECT', 'NEXT'], ['CORRECT'], {1, 6})

    def test_backtick_in_info_cannot_hide_required_rows(self):
        chunks = [s + '\n' for s in ('## 2026-10-27', self.row('KEEP'),
            '```bad`info', self.row('CORRECT'), '```bad`info', self.row('NEXT'))]
        self.assert_index(chunks, ['KEEP', 'CORRECT', 'NEXT'], ['CORRECT'], {1, 5})

    def test_valid_fences_keep_example_rows_outside_task_set(self):
        for token in ('```', '~~~'):
            for indent in range(4):
                for invalid in ('    ' + token, '\t' + token, token + '\u00a0',
                                token + 'suffix', token[:2], '~~~' if token == '```' else '```'):
                    with self.subTest(token=token, indent=indent, invalid=repr(invalid)):
                        chunks = [s + '\r\n' for s in ('## 2026-10-27', self.row('KEEP'),
                            ' ' * indent + token + 'md', '## 2099-01-01', invalid,
                            '- [ ] [KEEP] example, not a second requirement',
                            '   ' + token + token[0] + ' \t', self.row('NEXT'))]
                        self.assert_index(chunks, ['KEEP', 'NEXT'], ['NEXT'], {1})
                        with self.subTest(stage='date'):
                            self.assertEqual([t['date'] for t in parse_requirements(''.join(chunks), canonical=True)],
                                             ['2026-10-27', '2026-10-27'])

    def test_unclosed_real_fence_keeps_existing_eof_policy(self):
        for ending in ('\n', '\r\n', '\r'):
            for token in ('```', '~~~'):
                for close in ('    ' + token, '\t' + token, token + '\u00a0', token + 'suffix'):
                    with self.subTest(ending=repr(ending), token=token, close=repr(close)):
                        chunks = [s + ending for s in ('## 2026-10-27', self.row('KEEP'),
                            token, close, '- [ ] [KEEP] literal example at EOF')]
                        chunks[-1] = chunks[-1].removesuffix(ending)
                        self.assert_index(chunks, ['KEEP'], ['KEEP'], set())

    def test_identity_version_and_budget_guards_remain(self):
        chunks = ['## 2026-10-27\n', self.row('KEEP') + '\n']
        raw, sha = self.bind(chunks)
        for suffix in (self.row('KEEP') + '\n', '- [ ] no stable identity\n'):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                parse_requirements(raw.decode() + suffix, canonical=True)
        for ids, bound, budget in ((['UNKNOWN'], sha, 20000), (['KEEP'], '0' * 64, 20000),
                                  (['KEEP'], sha, 1)):
            with self.subTest(ids=ids, bound=bound, budget=budget), self.assertRaises(ValueError):
                task_view(self.root, ids, bound, max_chars=budget)
        self.assertEqual(self.path.read_bytes(), raw)

    def canonical_fixture(self):
        chunks = [s + '\n' for s in ('## 2026-10-27', self.row('KEEP'), '',
            '    ```', self.row('CORRECT'), '    ```', self.row('NEXT'))]
        raw, sha = self.bind(chunks)
        details = self.path.parent / 'task_details'
        details.mkdir()
        for identity in ('KEEP', 'CORRECT', 'NEXT'):
            (details / (identity + '.md')).write_bytes(
                f'# {identity}\nTask-ID: {identity}\nDate: 2026-10-27\n\n## Plan\n\nPreserve requirement.\n\n## Progress\n\nPending.\n'.encode())
        return raw, sha

    def test_real_snapshot_and_prepare_keep_complete_coverage(self):
        raw, sha = self.canonical_fixture()
        with self.subTest(stage='canonical'):
            snapshot = snapshot_project_docs(self.root)
            self.assertEqual(set(snapshot['task_details']), {'KEEP', 'CORRECT', 'NEXT'})
            draft = prepare(self.root, 'fence-draft', 'manual', 'synthetic fixture only')
            self.assertEqual([t['task_id'] for t in draft['tasks']], ['KEEP', 'CORRECT', 'NEXT'])
            self.assertEqual(draft['task_source']['sha256'], sha)
            self.assertEqual(draft['project_documents'], snapshot)
            self.assertEqual(draft['plan_review']['schema_version'], 'main-plan-review/v1')
            self.assertTrue(all(t['action'] == 'configure_host_action' for t in draft['tasks']))
            self.assertEqual(self.path.read_bytes(), raw)
        legacy = self.root / 'legacy'
        legacy.mkdir()
        source = legacy / 'TASK.md'
        source.write_bytes(b'- [ ] [KEEP] first\n\n    ```\n- [ ] [CORRECT] second\n    ```\n- [ ] [NEXT] third\n')
        legacy_draft = prepare(source, 'legacy-fence-draft', 'manual', 'synthetic fixture only')
        self.assertEqual([t['task_id'] for t in legacy_draft['tasks']], ['KEEP', 'CORRECT', 'NEXT'])
        self.assertEqual(legacy_draft['task_source']['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_actual_cli_prepares_and_reads_complete_task_scope(self):
        raw, sha = self.canonical_fixture()
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        repo = Path(__file__).resolve().parents[1]
        output = self.root / '.agent-runs/draft.json'
        commands = [
            [sys.executable, '-B', '-m', 'agent_runtime.task_supervisor', 'prepare',
             '--project-root', str(self.root), '--run-id', 'fence-cli',
             '--authorization-reference', 'synthetic fixture only', '--out', str(output)],
            [sys.executable, '-B', str(repo / 'scripts/task_context.py'), '--root', str(self.root),
             '--task-id', 'CORRECT', '--sha256', sha, '--compact']]
        for number, command in enumerate(commands):
            with self.subTest(command=number):
                run = subprocess.run(command, cwd=repo, capture_output=True, timeout=15,
                    env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936'))
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stderr, b'')
                value = json.loads(run.stdout.decode('utf-8'))
                if number == 0:
                    self.assertEqual(value, {'status': 'draft', 'plan': str(output), 'tasks': 3})
                    draft = json.loads(output.read_bytes())
                    self.assertEqual([t['task_id'] for t in draft['tasks']], ['KEEP', 'CORRECT', 'NEXT'])
                    self.assertIn('plan_review', draft)
                    self.assertTrue(all(t['action'] == 'configure_host_action' for t in draft['tasks']))
                else:
                    self.assertEqual(value['source_lines'], [1, 3, 4, 5, 6])
                    self.assertEqual(value['text'], '## 2026-10-27\n\n    ```\n' + self.row('CORRECT') + '\n    ```\n')
                    self.assertEqual(value['omitted_task_rows'], 2)
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual({p: after[p] for p in before}, before)
        self.assertEqual(set(after) - set(before), {Path('.agent-runs/draft.json')} if output.exists() else set())
        self.assertEqual(self.path.read_bytes(), raw)
