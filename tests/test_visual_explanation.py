"""Package closure and real existing handoff API checks for visual teaching.

These are not LLM/visual tests. Real role execution and image review belong in
an isolated forward run; the integrity checker cannot certify a rendered idea.
"""
import copy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

try:
    from .markdown_links import package_markdown_targets
except ImportError:  # unittest discover -s tests imports top-level test modules.
    from markdown_links import package_markdown_targets

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'plugins/research-assistant/skills'
ROLES = ('explain-research-concepts', 'research-figures', 'research-diagrams',
         'research-data-visualization', 'paper-reading-companion', 'research-assistant')


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


handoff = module_at('visual_teaching_handoff', ROOT / 'scripts/validate_handoff.py')
sync = module_at('visual_teaching_sync', ROOT / 'scripts/sync_plugin_references.py')


class VisualTeachingPackageTests(unittest.TestCase):
    def test_shared_contract_is_bundled_for_all_actual_consumers(self):
        source = 'workflows/visual_explanation_workflow.md'
        expected = {f'plugins/research-assistant/skills/{r}/references/visual_explanation_workflow.md'
                    for r in ROLES}
        self.assertEqual(set(sync.MAPPINGS[source]), expected)
        for dest in expected:
            self.assertEqual((ROOT / dest).read_text(), sync.render(source, dest))

    def test_entry_and_shared_workflow_links_stay_inside_each_skill(self):
        for role in ROLES:
            package = SKILLS / role
            # Follow actual local references, not token/heading matches. A skill
            # distributed alone must not need this checkout or a sibling skill.
            todo = [package / 'SKILL.md']
            visited = set()
            while todo:
                path = todo.pop()
                if path in visited:
                    continue
                visited.add(path)
                self.assertTrue(path.is_file(), str(path))
                for resolved in package_markdown_targets(path, package):
                    if resolved.suffix == '.md':
                        todo.append(resolved)
            self.assertIn(package / 'references/visual_explanation_workflow.md', visited)


class VisualTeachingExistingHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Actual small local artifacts; no claim that an image was visually read.
        files = {'A-source': ('diagram.svg', '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="30"><text x="2" y="20">S1: x</text></svg>'),
                 'A-notes': ('review.txt', 'Synthetic integrity fixture; not a semantic or visual certification.')}
        artifacts = []
        for aid, (name, text) in files.items():
            (self.root / name).write_text(text)
            artifacts.append(dict(id=aid, path=name, sha256=hashlib.sha256(text.encode()).hexdigest()))
        self.request = dict(schema_version=1, input_version='EXPL-test:v1',
                            tasks=[dict(task_id='EXPL-test:S1'), dict(task_id='EXPL-test:visual-check')])
        self.result = dict(schema_version=1, run_id='visual-test', role='research-diagrams',
                           input_version='EXPL-test:v1', status='completed', limitations=[],
                           artifacts=artifacts, checks=[dict(criterion='fixture declared check',
                           status='pass', artifact_ids=['A-notes'])], tasks=[
                           dict(task_id='EXPL-test:S1', depends_on=[], status='done', evidence=['A-source']),
                           dict(task_id='EXPL-test:visual-check', depends_on=['EXPL-test:S1'],
                                status='done', evidence=['A-notes'])])

    def validate(self, record=None):
        return handoff.validate(record or self.result, self.root, True, consumer_request=self.request)

    def test_existing_api_accepts_bound_scope_and_artifact_bytes(self):
        self.assertEqual(self.validate(), [])

    def test_producer_cannot_omit_consumer_requested_visual_check(self):
        result = copy.deepcopy(self.result)
        result['tasks'].pop()
        self.assertTrue(any('consumer task missing' in e for e in self.validate(result)))

    def test_visual_check_not_run_cannot_count_as_complete(self):
        result = copy.deepcopy(self.result)
        result['checks'][0]['status'] = 'not_run'
        self.assertTrue(any('incomplete check' in e for e in self.validate(result)))

    def test_same_filename_after_figure_change_invalidates_old_handoff(self):
        (self.root / 'diagram.svg').write_text('<svg/>')
        self.assertTrue(any('sha256 mismatch' in e for e in self.validate()))

    def test_new_explanation_input_cannot_consume_old_picture_result(self):
        self.request['input_version'] = 'EXPL-test:v2'
        self.assertTrue(any('input version mismatch' in e for e in self.validate()))


if __name__ == '__main__':
    unittest.main()
