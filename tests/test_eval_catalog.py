"""Distribution and task catalog contracts, not behavioral success tests."""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare', ROOT/'scripts/prepare_agent_eval.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)

class CatalogTests(unittest.TestCase):
    def test_every_skill_has_an_isolated_task_and_rubric(self):
        skills={str(p.relative_to(ROOT)) for p in (ROOT/'plugins').glob('*/skills/*/SKILL.md')}
        roles=json.loads((ROOT/'config/role_registry.json').read_text())['roles']
        cases=json.loads((ROOT/'evals/tasks.json').read_text())['cases']
        rubric=json.loads((ROOT/'evals/rubric.json').read_text())['criteria']
        self.assertEqual(skills,{r['skill'] for r in roles})
        self.assertEqual(skills,{c['skill'] for c in cases})
        self.assertEqual(len(cases),len({c['id'] for c in cases}))
        self.assertEqual(set(rubric),{c['id'] for c in cases})
        for role in roles:
            self.assertTrue((ROOT/role['execution']).is_file())
            text=(ROOT/role['skill']).read_text()
            self.assertIn('(references/execution.md)',text)
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue(((ROOT/role['skill']).parent/target).is_file(),target)

    def test_preparation_contains_inputs_but_not_ground_truth(self):
        case=json.loads((ROOT/'evals/tasks.json').read_text())['cases'][0]
        with tempfile.TemporaryDirectory() as td:
            dest=prepare.prepare(case,Path(td)/'case')
            self.assertEqual((dest/'task.txt').read_text(),case['prompt'])
            self.assertTrue((dest/'skill/SKILL.md').is_file())
            self.assertEqual({p.name for p in (dest/'inputs').iterdir()},set(case['fixtures']))
            self.assertFalse((dest/'rubric.json').exists())
            with self.assertRaises(FileExistsError):
                prepare.prepare(case,dest)
