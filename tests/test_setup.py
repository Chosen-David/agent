"""Installation lifecycle tests in temporary project directories, no Claude calls."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bootstrap', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='agent setup space ')
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name)

    def test_install_full_catalog_and_preserve_existing_project_rules(self):
        (self.target / 'CLAUDE.md').write_text('# Project rules\nKeep my instructions.\n')
        result = setup.install(self.target)
        self.assertEqual(result['status'], 'configured')
        self.assertEqual(result['skills'], len(setup.catalog()))
        self.assertEqual(result['subagents'], len(setup.catalog()))
        manifest = json.loads((self.target / '.claude/agent-workflows/installation.json').read_text())
        self.assertEqual(manifest['project_root'], str(self.target.resolve()))
        self.assertEqual(manifest['repository'], str(ROOT))
        self.assertNotEqual(manifest['project_root'], manifest['repository'])
        self.assertIn('Keep my instructions.', (self.target / 'CLAUDE.md').read_text())
        self.assertIn('TASK.md', (self.target / 'CLAUDE.md').read_text())
        for role, source, _ in setup.catalog():
            skill = self.target / '.claude/skills' / role['id']
            self.assertEqual(skill.resolve(), source)
            self.assertEqual((skill / 'SKILL.md').read_bytes(), (source / 'SKILL.md').read_bytes())
            agent = self.target / '.claude/agents' / ('agent-' + role['id'] + '.md')
            self.assertIn('  - ' + role['id'], agent.read_text())
            self.assertNotIn('bypassPermissions', agent.read_text())

    def test_repeat_install_is_idempotent(self):
        setup.install(self.target)
        before = (self.target / 'CLAUDE.md').read_bytes()
        setup.install(self.target)
        self.assertEqual(before, (self.target / 'CLAUDE.md').read_bytes())
        self.assertEqual(before.decode().count(setup.BEGIN), 1)

    def test_canonical_task_created_without_fabricated_work_and_never_overwritten(self):
        setup.install(self.target)
        task_file = self.target / 'agent_doc/task/TASK.md'
        self.assertIn('尚未填写已授权任务', task_file.read_text())
        task_file.write_text('- [ ] [REAL] User task and constraints\n')
        setup.install(self.target)
        self.assertEqual(task_file.read_text(), '- [ ] [REAL] User task and constraints\n')
        setup.uninstall(self.target)
        self.assertEqual(task_file.read_text(), '- [ ] [REAL] User task and constraints\n')

    def test_conflicting_skill_aborts_before_any_entry_edits(self):
        path = self.target / '.claude/skills/research-assistant'
        path.mkdir(parents=True)
        (path / 'mine').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'preserving existing skill'): setup.install(self.target)
        self.assertFalse((self.target / 'CLAUDE.md').exists())
        self.assertEqual((path / 'mine').read_text(), 'keep')

    def test_locally_edited_generated_agent_is_preserved(self):
        setup.install(self.target)
        path = self.target / '.claude/agents/agent-research-assistant.md'
        path.write_text('my customized agent')
        with self.assertRaisesRegex(ValueError, 'locally edited'): setup.install(self.target)
        self.assertEqual(path.read_text(), 'my customized agent')

    def test_uninstall_removes_only_owned_unmodified_files(self):
        (self.target / 'CLAUDE.md').write_text('Original project rules\n')
        setup.install(self.target)
        agent = self.target / '.claude/agents/agent-research-assistant.md'
        agent.write_text('keep local edits')
        result = setup.uninstall(self.target)
        self.assertIn('.claude/agents/agent-research-assistant.md', result['preserved_local_edits'])
        self.assertEqual(agent.read_text(), 'keep local edits')
        self.assertIn('Original project rules', (self.target / 'CLAUDE.md').read_text())
        self.assertNotIn(setup.BEGIN, (self.target / 'CLAUDE.md').read_text())
        self.assertFalse((self.target / '.claude/skills/research-review').is_symlink())

    def test_check_is_read_only_and_detects_missing_setup(self):
        self.assertEqual(setup.check(self.target)['status'], 'needs_setup')
        self.assertEqual(list(self.target.iterdir()), [])

    def test_marketplace_and_setup_expose_same_registered_skills(self):
        marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        advertised = {path for plugin in marketplace['plugins'] for path in plugin['skills']}
        for role, _, _ in setup.catalog():
            self.assertIn('./' + str(Path(role['skill']).parent), advertised)

    def test_symlinked_config_directory_cannot_redirect_writes(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.target / '.claude').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'outside target'): setup.install(self.target)
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_malformed_managed_block_preserves_all_files(self):
        (self.target / 'CLAUDE.md').write_text(setup.BEGIN + '\nuser notes')
        with self.assertRaisesRegex(ValueError, 'malformed'): setup.install(self.target)
        self.assertFalse((self.target / '.claude/agents').exists())
