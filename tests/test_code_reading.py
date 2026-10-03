"""Evidence extraction on disposable Git fixtures; not LLM comprehension tests."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/research-assistant/skills/code-reading'
spec = importlib.util.spec_from_file_location('source_evidence', SKILL / 'scripts/source_evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE).decode().strip()
        self.git = git
        git('init', '-q')
        self.source = '@decorate\nclass Engine:\n    async def run(self):\n        return 42\n\ndef other():\n    return 0\n'
        (self.repo / 'example.py').write_text(self.source)
        (self.repo / 'binary').write_bytes(b'\0bad')
        (self.repo / 'kernel.cu').write_text('int kernel() {\n  return 0;\n}\n')
        (self.repo / 'src').mkdir()
        (self.repo / 'src/file.txt').write_text('fixture')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
        self.sha = git('rev-parse', 'HEAD')

    def capture(self, **options):
        args = dict(repo=self.repo, commit=self.sha, path='example.py', symbol='Engine.run')
        args.update(options)
        return evidence.capture(**args)

    def test_immutable_symbol_evidence_ignores_dirty_checkout(self):
        (self.repo / 'example.py').write_text('raise Exception("must not execute")\n')
        before = self.git('status', '--porcelain')
        result = self.capture()
        self.assertEqual((result['start_line'], result['end_line']), (3, 4))
        self.assertIn('return 42', result['excerpt'])
        self.assertEqual(result['symbol_resolution'], 'python_ast')
        self.assertEqual(result['evidence_kind'], 'source_fact')
        self.assertEqual(self.git('status', '--porcelain'), before)
        self.assertEqual((self.repo / 'example.py').read_text(), 'raise Exception("must not execute")\n')

    def test_decorators_and_ranges(self):
        self.assertEqual(self.capture(symbol='Engine')['start_line'], 1)
        self.assertEqual(self.capture(start=4, end=4)['excerpt'].strip(), 'return 42')
        with self.assertRaises(ValueError):
            self.capture(start=6, end=7)

    def test_invalid_inputs_do_not_produce_evidence(self):
        for options in [dict(commit='HEAD'), dict(commit=self.git('rev-parse', 'HEAD:example.py')),
                        dict(path='../example.py'), dict(path='/example.py'), dict(path='./example.py'),
                        dict(symbol='run'), dict(start=0, end=2), dict(start=4),
                        dict(symbol=None, start=1, end=999), dict(path='binary', symbol=None, start=1, end=1)]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.capture(**options)

    def test_non_python_explicit_range_is_manual(self):
        result = self.capture(path='kernel.cu', symbol=None, label='kernel', start=1, end=3)
        self.assertEqual(result['symbol_resolution'], 'manual_label')
        with self.assertRaises(ValueError):
            self.capture(path='kernel.cu', symbol='kernel')

    def test_cli_works_without_target_import(self):
        output = subprocess.check_output(['python', str(SKILL / 'scripts/source_evidence.py'),
            '--repo', str(self.repo), '--commit', self.sha, '--path', 'example.py', '--symbol', 'Engine.run'])
        self.assertEqual(json.loads(output)['commit'], self.sha)

    def test_replace_refs_cannot_relabel_new_content_as_old_commit(self):
        (self.repo / 'example.py').write_text('class Engine:\n    def run(self):\n        return 999\n')
        self.git('add', 'example.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'new')
        self.git('replace', self.sha, self.git('rev-parse', 'HEAD'))
        self.assertIn('return 42', self.capture()['excerpt'])

    def test_tree_is_not_source(self):
        with self.assertRaises(ValueError):
            self.capture(path='src', symbol=None, start=1, end=1)

    def test_formfeed_preserves_ast_line_numbers(self):
        (self.repo / 'example.py').write_text('marker=1\n\fdef hello():\n    return marker\n')
        self.git('add', 'example.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'formfeed')
        result = self.capture(commit=self.git('rev-parse', 'HEAD'), symbol='hello')
        self.assertEqual((result['start_line'], result['end_line']), (2, 3))
        self.assertEqual(result['excerpt'], '\fdef hello():\n    return marker')

    def test_ambiguous_conditional_definitions_rejected(self):
        (self.repo / 'example.py').write_text('if True:\n    def f(): pass\nelse:\n    def f(): pass\n')
        self.git('add', 'example.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'ambiguous')
        with self.assertRaises(ValueError):
            self.capture(commit=self.git('rev-parse', 'HEAD'), symbol='f')


class DistributionTests(unittest.TestCase):
    def test_standalone_links_and_routes(self):
        for path in [SKILL / 'SKILL.md', *SKILL.glob('references/*.md')]:
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((path.parent / target).is_file(), (path, target))
        for file in ['README.md', 'prompts/orchestrator.md', 'prompts/research_orchestrator.md',
                     'plugins/research-assistant/skills/research-assistant/SKILL.md']:
            self.assertIn('code-reading', (ROOT / file).read_text())
        market = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertIn('./plugins/research-assistant/skills/code-reading', market['plugins'][0]['skills'])
        coordinator = ROOT / 'plugins/research-assistant/skills/research-assistant/references'
        self.assertTrue((coordinator / 'code_reading_workflow.md').is_file())
        self.assertTrue((coordinator / 'code-reading_execution.md').is_file())
