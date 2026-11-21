from tests.document_fixture import DocumentFixtureCase
import os
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location('collab_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
WORKFLOW = 'collaborative_implementation_workflow.md'
ROLES = ('research-assistant', 'research-implement-optimize')


class TaskContractTests(DocumentFixtureCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def load(self, role):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts/load_skill.py'),
             '--project', str(self.project), '--skill', role],
            capture_output=True, text=True, timeout=30)

    def assert_local_route(self, body, base):
        routes = re.findall(r'\[[^\]]+\]\(([^)]+)\)', body)
        route = next((p for p in routes if p.endswith(WORKFLOW)), None)
        self.assertIsNotNone(route, 'missing collaborative implementation route')
        self.assertFalse(route.startswith(('http:', 'https:')))
        target = (base / route).resolve()
        self.assertTrue(target.is_file(), str(target))
        self.assertEqual(target.read_text(), (ROOT / 'workflows' / WORKFLOW).read_text())

    def test_installed_copy_and_link_expose_local_contract(self):
        for copy in (False, True):
            project = self.project / str(copy)
            project.mkdir()
            setup.install(project, copy_skills=copy)
            original = self.project
            self.project = project
            try:
                for role in ROLES:
                    with self.subTest(copy=copy, role=role):
                        loaded = self.load(role)
                        self.assertEqual(loaded.returncode, 0, loaded.stderr)
                        result = json.loads(loaded.stdout)
                        self.assertFalse(result['launched'])
                        self.assertEqual(result['execution_mode'], 'single-main')
                        self.assert_local_route(result['content'], Path(result['source']).parent)
            finally:
                self.project = original

    def test_standalone_copy_contains_contract_without_siblings(self):
        setup.install(self.project, copy_skills=True)
        for role in ROLES:
            source = self.project / '.claude/skills' / role
            self.assert_local_route((source / 'SKILL.md').read_text(), source)
            contract = source / 'references' / WORKFLOW
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', contract.read_text()):
                if not target.startswith(('https:', 'http:', '#')):
                    path = (contract.parent / target).resolve()
                    self.assertTrue(path.is_relative_to(source), target)
                    self.assertTrue(path.is_file(), target)

    def test_missing_contract_is_rejected_by_real_loader(self):
        setup.install(self.project, copy_skills=True)
        contract = self.project / '.claude/skills' / ROLES[1] / 'references' / WORKFLOW
        self.assertTrue(contract.is_file())
        contract.unlink()
        loaded = self.load(ROLES[1])
        self.assertEqual(loaded.returncode, 2)
        self.assertIn('installation needs setup', loaded.stderr)

    def test_changed_contract_is_rejected_by_real_loader(self):
        setup.install(self.project, copy_skills=True)
        contract = self.project / '.claude/skills' / ROLES[1] / 'references' / WORKFLOW
        self.assertTrue(contract.is_file())
        contract.write_text('Implement first; manufacture passing evidence afterwards.\n')
        loaded = self.load(ROLES[1])
        self.assertEqual(loaded.returncode, 2)
        self.assertIn('installation needs setup', loaded.stderr)

    def test_repository_entries_route_to_contract(self):
        for name in ('AGENTS.md', 'prompts/orchestrator.md',
                     'prompts/research_orchestrator.md',
                     'workflows/implementation_optimization_workflow.md'):
            with self.subTest(entry=name):
                path = ROOT / name
                self.assert_local_route(path.read_text(), path.parent)


if __name__ == '__main__':
    unittest.main()
