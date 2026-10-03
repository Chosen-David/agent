"""Execute real synthetic bodies; known declaration blind spots remain explicit."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'evals/crossfeature'


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


class CrossfeatureDeliveryTests(unittest.TestCase):
    def test_architecture_executes_both_splits_against_frozen_oracle(self):
        core=load(BASE/'architecture_inputs/core.py','crossfeature_core')
        data=json.loads((BASE/'architecture_inputs/cases.json').read_text())
        oracle=json.loads((BASE/'architecture_oracle.json').read_text())
        for split,cases in data.items():
            for case in cases:
                with self.subTest(split=split,case=case['id']):
                    try: actual=core.run(case['rows'],mode=case.get('mode','default'))
                    except (ValueError,LookupError) as exc: actual={'error':type(exc).__name__}
                    self.assertEqual(actual,oracle[case['id']])

    def test_paper_declaration_detection_and_documented_semantic_gaps(self):
        paper=load(BASE/'paper_cases.py','crossfeature_paper')
        with tempfile.TemporaryDirectory() as tmp:
            outcomes=paper.evaluate(Path(tmp))
            self.assertEqual(len(outcomes),10)
            gaps={x['case_id'] for x in outcomes if x['classification']=='false_negative'}
            self.assertEqual(gaps,{'audit_disguised','copied_body','dispatch_as_start'})
            self.assertFalse([x for x in outcomes if x['classification']=='false_positive'])
            for row in outcomes:
                self.assertEqual(row['model_execution'],'not_run')
                self.assertTrue(row['artifact_sha256'])
            self.assertTrue((Path(tmp)/'paper.pdf').read_bytes().startswith(b'%PDF-1.4'))
            self.assertIn('input', (Path(tmp)/'exemplar-3.md').read_text())


if __name__ == '__main__': unittest.main()
