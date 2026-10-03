"""Declared report contracts, not correctness of natural-language analysis."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/research-assistant/skills/code-reading'
spec = importlib.util.spec_from_file_location('coverage_check', SKILL / 'scripts/check_coverage.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.report = json.loads((SKILL / 'references/coverage.example.json').read_text())

    def reject(self, report):
        with self.assertRaises(checker.ContractError):
            checker.validate(report)

    def test_unknown_gap_is_honest_not_complete(self):
        result = checker.validate(self.report)
        self.assertEqual(result['status'], 'contract_valid')
        self.assertEqual(result['unresolved_rows'], ['many'])
        self.assertIn('no source verification', result['limitation'])

    def test_cannot_extend_confirmed_claim_over_unread_consumer(self):
        self.report['claims'][0]['covers'].append('many')
        self.reject(self.report)

    def test_not_applicable_requires_reason_and_source(self):
        row = self.report['coverage'][1]
        row.update(status='not_applicable', reason='Model has no batch entry', evidence=['E1'])
        checker.validate(self.report)
        del row['reason']
        self.reject(self.report)

    def test_source_anchor_cannot_come_from_old_commit(self):
        self.report['evidence'][0]['commit'] = '1' * 40
        self.reject(self.report)

    def test_missing_or_invalid_anchor_rejected(self):
        for field, value in [('symbol', ''), ('start_line', True), ('end_line', 0), ('blob_sha256', 'hash')]:
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report['evidence'][0][field] = value
                self.reject(report)

    def test_bad_row_or_references_rejected(self):
        mutations = [('consumer', ''), ('condition', ''), ('model', ''), ('input', ''),
                     ('output', ''), ('status', 'complete'), ('evidence', []), ('evidence', ['missing'])]
        for field, value in mutations:
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report['coverage'][0][field] = value
                self.reject(report)

    def test_execution_requires_run_and_observed_scope(self):
        claim = self.report['claims'][0]
        claim['level'] = 'executed'
        self.reject(self.report)
        artifact = {'path': 'outside-target/log.txt', 'sha256': 'a' * 64}
        run = dict(id='R1', commit=self.report['commit'], covers=['one'], command='synthetic command',
                   environment='synthetic fixture; not real run', inputs=[artifact], outputs=[artifact], logs=[artifact])
        self.report['runs'] = [run]
        claim['runs'] = ['R1']
        checker.validate(self.report)
        self.report['coverage'][1].update(status='inspected', evidence=['E1'])
        claim['covers'].append('many')
        self.reject(self.report)

    def test_stale_or_unrecorded_run_rejected(self):
        artifact = {'path': 'fixture.txt', 'sha256': 'a' * 64}
        self.report['runs'] = [dict(id='R1',commit='1'*40,covers=['one'],command='cmd',environment='fixture',
                                   inputs=[artifact],outputs=[artifact],logs=[artifact])]
        self.reject(self.report)
        self.report['runs'][0]['commit'] = self.report['commit']
        self.report['runs'][0]['logs'] = []
        self.reject(self.report)

    def test_duplicates_and_malformed_structures_fail_closed(self):
        for field in ('evidence', 'coverage', 'claims'):
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report[field].append(copy.deepcopy(report[field][0]))
                self.reject(report)
        for bad in (None, [], {'schema_version': 1}, {**self.report, 'schema_version': True}, {**self.report, 'runs': None}):
            self.reject(bad)

    def test_cli_never_executes_report_commands(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            sentinel = Path(temp) / 'must-not-exist'
            artifact = {'path': 'fixture', 'sha256': 'a' * 64}
            self.report['runs'] = [dict(id='R1', commit=self.report['commit'], covers=['one'],
                command='touch ' + str(sentinel), environment='synthetic fixture',
                inputs=[artifact], outputs=[artifact], logs=[artifact])]
            path.write_text(json.dumps(self.report))
            before = path.read_bytes()
            result = subprocess.run(['python', str(SKILL / 'scripts/check_coverage.py'), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, path.read_bytes())
            self.assertFalse(sentinel.exists())
            path.write_text(json.dumps(self.report).replace('\"schema_version\": 1', '\"schema_version\": 0, \"schema_version\": 1'))
            result = subprocess.run(['python', str(SKILL / 'scripts/check_coverage.py'), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('duplicate JSON key', result.stderr)
            path.write_text('{broken')
            result = subprocess.run(['python', str(SKILL / 'scripts/check_coverage.py'), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_offline_coverage_and_example_are_local(self):
        for role in ('research-assistant', 'research-implement-optimize'):
            root = ROOT / 'plugins/research-assistant/skills' / role / 'references'
            self.assertTrue((root / 'code_reading_coverage.md').is_file())
            self.assertIn('(code_reading_coverage.md)', (root / 'code_reading_workflow.md').read_text())
        bundled = ROOT / 'plugins/research-assistant/skills/research-assistant/references/code_reading_coverage.example.json'
        self.assertEqual(json.loads(bundled.read_text()), self.report)

    def test_taskset_questions_and_oracle_match_without_leaking_into_catalog(self):
        taskset = json.loads((ROOT / 'evals/code_reading_v2/taskset.json').read_text())
        oracle = json.loads((ROOT / 'evals/code_reading_v2/oracle.json').read_text())
        self.assertEqual({x['id'] for x in taskset['tasks']}, set(oracle['criteria']))
        self.assertEqual(sum(map(len, oracle['criteria'].values())), 18)
        self.assertNotIn('oracle', json.dumps(json.loads((ROOT / 'evals/tasks.json').read_text())))
