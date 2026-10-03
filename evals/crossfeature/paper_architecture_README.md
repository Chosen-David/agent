# Executable delivery controls

The rubrics and architecture oracle were written before the first executions.
They are evaluator inputs; do not pass them, this README, the builder or tests to
workers. `architecture_inputs` contains executable data/code only. `paper_cases.py`
reuses the existing paper declaration fixture, replacing manuscript and exemplar
placeholders with generic original content, real PDFs and actual hashes. All
publication metadata and internal role receipts remain synthetic controls.

Reproduce (standard library only):

```sh
python evals/crossfeature/architecture_cases.py --out /tmp/architecture-outcomes.json
python evals/crossfeature/paper_cases.py --out /tmp/paper-controls
python -m unittest discover -s tests -p test_crossfeature_delivery.py -v
```

Architecture: seven cases execute default and optional routes, unknown extension,
invalid width, empty input, reordered held-out data and a float32 rounding/tie
boundary. Results include actual outputs, frozen expected outputs, input hashes
and AST-derived source anchors. These anchors describe program evidence, not
independent role analysis. Arrays have actual float32 storage; no tensor-library
runtime, accelerator, batching or complete call-graph claim follows.

Paper: ten cases run the existing validator against real artifacts. Two honest
positive controls pass; five negative controls are rejected; three semantic
negatives pass declaration checks: disguised audit, copied body and a queued
dispatch file supplied as a start receipt. Outcomes explicitly call those false
negatives against the broader artifact requirement. This is the validator's
published declaration-only boundary, not semantic certification. Tests assert
these known gaps to prevent falsely reporting complete semantic coverage. They
do not train a semantic checker or manufacture independent review output.

The provided catalogs support separate host execution through the existing eval
pipeline. For architecture use `--fixture-root evals/crossfeature/architecture_inputs`.
For paper use `--fixture-root /tmp/paper-controls/blind`; anonymous items are:
item-a good, item-b copied, item-c attributed quotation, item-d disguised audit.
That mapping is evaluator-only. A real independent reviewer must inspect actual
worker output and preserve hashes/commit/receipts. The model execution field in
program-control outcomes remains `not_run` regardless of later separate runs.

The ten synthetic exemplars are not legally published venue papers; they cannot
establish real exemplar-learning completion. The good manuscript is a bounded
synthetic research narrative, not a submission-ready scientific contribution.
Paper genre, copying, role provenance, actual PDF appearance, figure reading,
and source-to-blueprint transfer still require real role review. Supplied PDFs
were parse-checked using pdftotext, not visually certified. The holdout comprises
new numeric inputs and a new attribution/staleness variation; it is too small to
support generalization or model A/B claims. Existing code_reading_v2 retains
broader static GQA, model-layout and unresolved ops coverage without pretending
to execute those unavailable operators.
