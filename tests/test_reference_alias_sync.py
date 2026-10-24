import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sync_plugin_references as sync


class ReferenceAliasSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = 'workflows/shared.md'
        self.one = 'plugins/demo/skills/one/references/shared.md'
        self.two = 'plugins/demo/skills/two/references/shared.md'
        self.planner = 'plugins/demo/skills/one/references/planner.md'
        self.write(self.source, '[planner](../prompts/planner.md)\n')
        self.write('prompts/planner.md', 'planner\n')
        self.write('shared/shared.md', 'old shared\n')
        self.write(self.planner, 'planner\n')
        for name in (self.one, self.two):
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.symlink_to(self.root / 'shared/shared.md')
        self.mappings = {
            'prompts/planner.md': [self.planner],
            self.source: [self.one, self.two],
        }

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def invoke(self, check=False):
        output = io.StringIO()
        argv = ['sync_plugin_references.py'] + (['--check'] if check else [])
        with patch.object(sync, 'ROOT', self.root), patch.object(sync, 'MAPPINGS', self.mappings), patch('sys.argv', argv), contextlib.redirect_stdout(output):
            code = sync.main()
        return code, output.getvalue()

    def test_conflict_rejects_before_any_write(self):
        # An unrelated stale destination precedes the conflicting aliases.
        self.write(self.planner, 'keep stale planner\n')
        before = (self.root / self.planner).read_bytes()
        code, output = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertIn(self.one, output)
        self.assertIn(self.two, output)
        self.assertEqual((self.root / self.planner).read_bytes(), before)
        self.assertEqual((self.root / self.one).read_text(), 'old shared\n')
        self.assertTrue((self.root / self.one).is_symlink())
        self.assertTrue((self.root / self.two).is_symlink())

    def test_check_reports_conflicting_destinations_without_writes(self):
        code, output = self.invoke(check=True)
        self.assertNotEqual(code, 0)
        self.assertIn(self.one, output)
        self.assertIn(self.two, output)
        self.assertEqual((self.root / self.one).read_text(), 'old shared\n')

    def test_equal_alias_outputs_remain_shared_and_converge(self):
        self.write(self.source, 'same output\n')
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(self.invoke(check=True)[0], 0)
        before = (self.root / self.one).read_bytes()
        self.assertEqual(self.invoke(), (0, ''))
        self.assertEqual((self.root / self.two).read_bytes(), before)
        self.assertTrue((self.root / self.one).is_symlink())
        self.assertTrue((self.root / self.two).is_symlink())

    def test_distinct_local_output_can_be_generated_independently(self):
        (self.root / self.one).unlink()
        self.write(self.one, 'old local\n')
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual(self.invoke(check=True)[0], 0)
        self.assertIn('](planner.md)', (self.root / self.one).read_text())
        self.assertIn(sync.REPO_BLOB + 'prompts/planner.md', (self.root / self.two).read_text())
        self.assertFalse((self.root / self.one).is_symlink())
        self.assertTrue((self.root / self.two).is_symlink())
        self.assertEqual(self.invoke(), (0, ''))


    def test_raw_snapshot_keeps_crlf_bytes(self):
        self.mappings = {'prompts/raw.json': ['bundled/raw.json']}
        self.write('prompts/raw.json', '')
        expected = b'{"value": 1}\r\n'
        (self.root / 'prompts/raw.json').write_bytes(expected)
        self.assertEqual(self.invoke()[0], 0)
        self.assertEqual((self.root / 'bundled/raw.json').read_bytes(), expected)
        self.assertEqual(self.invoke(check=True)[0], 0)

    def test_current_markdown_crlf_remains_unchanged(self):
        self.write(self.source, 'same output\n')
        self.assertEqual(self.invoke()[0], 0)
        path = self.root / self.one
        expected = path.read_bytes().replace(b'\n', b'\r\n')
        path.write_bytes(expected)
        self.assertEqual(self.invoke(check=True)[0], 0)
        self.assertEqual(self.invoke(), (0, ''))
        self.assertEqual(path.read_bytes(), expected)


if __name__ == '__main__':
    unittest.main()
