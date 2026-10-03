# Executed synthetic visualization evaluation

12 bounded cases: 9 development and 3 parameter/composition holdouts. Every case generates actual Matplotlib PNG and PDF, rasterizes the actual PDF with PyMuPDF, and records hashes. Final program audit has 0 false positives / 0 false negatives against the reviewed v3 rubric. This is an instrumented fixture audit, not proof of production semantic detection or host model success.

| Cases | Target | Final program result |
|---|---|---|
| v01, v08, v09, v10 | Good bars; valid log points; good Chinese PDF; holdout good data | Accepted |
| v02 | Nonzero bar baseline | Rejected with actual axis extent |
| v03 | ms label with seconds values | Rejected with actual artist/source mismatch |
| v04 | SD drawn but SEM caption | Rejected with actual segment/source mismatch |
| v05 | Incompatible batch protocol | Rejected with synthetic run receipt comparison |
| v06 | Method palette / legend changed | Rejected with actual artist/legend colors |
| v07, v12 | Chinese PNG correct but actual PDF corrupt | Rejected with actual PDF raster difference plus missing extracted label |
| v11 | Holdout unit + protocol + palette combination | All three identified |

Initial run/review found real flaws, corrected before final acceptance: text-only checks falsely rejected correctly rendered Type3 Chinese; changing to Type42 made text extractable but silently rendered the Chinese label blank; pixel inspection exposed that error. Final fixtures use Type3, and rejection requires measured pixel discrepancy against a PNG-stage same-renderer reference; text extraction is supporting evidence only. A good Chinese export was visually opened and verified. The original reference is generated independently before export-only corruption; this is a controlled test oracle, not general OCR. The v2 threshold (retained in v3) is recorded explicitly; do not describe v1 as passing. An independent review also caught removed-bar state being used for the log-point case and stale cached PDF evidence; the audit now observes live points and rerenders the current PDF at each audit. Regression tests replace an actual PDF without changing cached metadata.

Existing `validate_pdf_exports` is executed separately: it rejects a PNG proxy declaration but accepts falsely asserted PDF pass declarations. This is a documented production trust boundary, not counted as a successful semantic detector. Protocol checks compare synthetic fixture receipts; no benchmark program execution is claimed.

Reproduce: `MPLCONFIGDIR=/tmp/mpl-crossfeature XDG_CACHE_HOME=/tmp/cache-crossfeature python evals/crossfeature/viz_suite.py --output /tmp/crossfeature-viz` and `python -m unittest discover -s tests -p test_crossfeature_viz.py -v` (7 tests passed). Requires Matplotlib, NumPy, Pillow, PyMuPDF and the installed Noto Sans CJK font. Absent dependencies are skips/blockers, never model passes.

Host status in these program records is **not_run**. `viz_host_task.json` references sanitized input copies only (actual images/PDF/source/run receipts, no outcomes or observed artist report). Parent orchestration may execute and record an independent host role separately. Parameter holdouts use distinct numbers and one distinct defect composition; they do not hold out defect mechanisms, and 12 cases establish no generalization rate. Not covered: arbitrary fonts, OCR robustness, subtle clipping, PDF accessibility, alternate error-bar conventions, large multipanel plots, color-vision simulation or unknown chart generators.

Further independent review reproduced a white PDF overlay that hides the visible label while preserving extractable text. V3 removes the text conjunction from rejection and adds an actual PDF overlay regression. The 0.5 pixel threshold and already-started host input bytes remain unchanged. These repaired program results are regression checks after review, not pristine holdout validation. Host tests remain independent of these instrumented audits.
