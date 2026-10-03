"""Executed synthetic figure audits; optional render stack is explicit, never faked."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from evals.crossfeature.viz_suite import audit, run

AVAILABLE = (all(importlib.util.find_spec(name) for name in ('matplotlib', 'numpy', 'PIL', 'fitz'))
             and Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc').is_file())


@unittest.skipUnless(AVAILABLE, 'requires matplotlib, numpy, Pillow, PyMuPDF and Noto Sans CJK font')
class CrossFeatureVizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.tmp.name)
        cls.result = run(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_all_cases_have_actual_evidence_and_no_mismatch(self):
        self.assertEqual(len(self.result['cases']), 12)
        for case in self.result['cases']:
            with self.subTest(case=case['id']):
                self.assertFalse(case['false_positive'])
                self.assertFalse(case['false_negative'])
                self.assertEqual(len(case['input_sha256']), 64)
                self.assertIn('figure.pdf', case['artifacts'])
                self.assertIn('pdf_render.png', case['artifacts'])
        self.assertEqual(self.result['host_model'], 'not_run')

    def test_both_positive_and_negative_chinese_exports(self):
        by_id = {x['id']: x for x in self.result['cases']}
        self.assertEqual(by_id['v09']['actual'], [])
        for cid in ('v07', 'v12'):
            self.assertEqual(by_id[cid]['actual'], ['pdf_glyphs'])
            self.assertGreater(by_id[cid]['render']['export_only_pixel_mae'], 0.5)
        # The production validator cannot detect false semantic pass declarations.
        self.assertTrue(by_id['v07']['production_declaration_control']['self_reported_pass_accepted'])
        self.assertTrue(by_id['v07']['production_declaration_control']['png_proxy_rejection'])

    def test_neutral_case_rename_preserves_detection(self):
        dest = self.output / 'innocent-name'
        shutil.copytree(self.output / 'v11', dest)
        reasons, _ = audit(dest)
        self.assertEqual(set(reasons), {'unit', 'protocol', 'palette'})

    def test_source_change_changes_observed_decision_without_expected_labels(self):
        dest = self.output / 'altered-source'
        shutil.copytree(self.output / 'v01', dest)
        source = json.loads((dest / 'source.json').read_text())
        source['samples_ms'][0][0] += 50
        (dest / 'source.json').write_text(json.dumps(source))
        reasons, _ = audit(dest)
        self.assertIn('unit', reasons)
        self.assertIn('uncertainty', reasons)

    def test_replacing_pdf_invalidates_cached_text_and_pixels(self):
        dest = self.output / 'stale-pdf'
        shutil.copytree(self.output / 'v09', dest)
        shutil.copyfile(self.output / 'v07' / 'figure.pdf', dest / 'figure.pdf')
        reasons, render = audit(dest)
        self.assertIn('pdf_glyphs', reasons)
        self.assertGreater(render['export_only_pixel_mae'], 0.5)

    def test_white_overlay_rejected_even_when_pdf_text_survives(self):
        import fitz
        dest = self.output / 'overlay-pdf'
        shutil.copytree(self.output / 'v01', dest)
        path = dest / 'figure.pdf'
        with fitz.open(path) as pdf:
            pdf[0].draw_rect(fitz.Rect(0, 0, 32, pdf[0].rect.height),
                             color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
            pdf.save(dest / 'overlay.pdf')
        shutil.copyfile(dest / 'overlay.pdf', path)
        reasons, render = audit(dest)
        self.assertFalse(render['pdf_label_missing'])
        self.assertGreater(render['export_only_pixel_mae'], 0.5)
        self.assertIn('pdf_glyphs', reasons)

    def test_holdout_has_distinct_numeric_inputs(self):
        rows = self.result['cases']
        self.assertEqual(sum(x['split'] == 'holdout' for x in rows), 3)
        self.assertEqual(len({x['input_sha256'] for x in rows}), len(rows))
