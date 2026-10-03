# Writing exemplar preflight — 2026-10-03

Scope: reusable workflow and declaration checks, not the actual ten-paper reading or manuscript rewrite. No user manuscript, private data, third-party paper PDF or figure copied into this public repository. SGLang remains untouched.

## Rationale and sources

The previous paper-delivery repair distinguished papers from audits but did not require learning from published examples before drafting. This extension makes the user's ten-paper requirement an explicit preflight for complete new manuscripts/full rewrites. It does not turn local copy edits into ten-paper studies.

Inspected the already locked Orchestra systems-paper-writing SKILL and two writing references (full writing-patterns; first 100 lines of section-blueprints), plus the prior MIT license. Source hashes/read scope are updated in `paper_delivery_sources.lock.json`. Useful principles: gaps→design→evaluation correspondence, reader-facing organization and explicit alternatives. Did not copy fixed paragraph/page counts, claims that a pattern makes evidence irrefutable, or unverified descriptions of named sample papers. The real ten originals must be inspected by the execution pipeline.

Also inspected the available paper-reading-companion SKILL (user cloud package `c8/6abe4dfc555c819180586d3e55bf8964/paper-reading-companion`) for capability selection: original page/hash anchoring and explicit warning that generated reader pages do not prove reading. No personal skill text was copied into this repo. Existing repository research-read-pdf supplies all-page visual discipline; research-diagrams and research-figures supply diagram execution. This is reuse of current roles, not a new external runtime installation.

## Actual routing and record interface

`workflows/paper_exemplar_learning.md` is canonical and bundled locally into research-assistant, research-write, research-review, research-read-pdf, research-diagrams and research-figures. Four paper roles load it from their SKILL and paper_delivery_contract before drafting; the writing workflow also explicitly links it. Figure roles link section 7 for diagram collaboration.

Order: verify adopted venue/template → select ten distinct published, relevant full texts → read all pages and all figures/tables → locate five-dimensional observations → synthesize → prepare manuscript blueprint (and visual-design-brief when needed) → obtain actual reader/diagram collaboration results → preflight receipt → draft → implement map → independently evaluate actual transfer in each language's final manuscript.

Future venues without proceedings use prior actual years of the target venue, plus justified comparable venues. Unknown current author rules remain provisional and block submission completion, while a verified provisional adopted template can support an honestly labeled draft. Access failures do not count as completed reading.

`validate_paper_delivery.py` now calls `paper_exemplar_checks.py`; both files are required for CLI distribution. No automatic host hook exists. The schema's new required fields are documented in the workflow; historical records missing them are incomplete, not silently migrated into success. Scripts validate declarations/hashes/coverage only. Metadata, reading receipts, claim support and actual visual quality still require source inspection and host execution evidence.

Architecture learning includes pixel-read source figure IDs/pages, actual reader and diagram-role receipts, seven design dimensions, an original visual brief and selection evidence. Scientific correctness and visual design are distinct final criteria. Correct nodes do not prove a compelling figure; attractive layout cannot cure incorrect mechanisms. No source-image/icon copying is authorized.

## Reproduce and evidence limits

```bash
python scripts/sync_plugin_references.py --check
python -m unittest discover -s tests -p test_paper_delivery.py -v
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

Focused tests: 25. Full suite at this extension snapshot: 130; reader: 3. All passed before final remote integration. Rejections cover nine papers, duplicate identity/PDF, abstract-only/access-blocked, unread pages, missing figures, missing reading receipts, unverified/provisional template, late learning, missing five-dimensional analysis or blueprint, exemplar IDs posing as own evidence, absent implementation, failed blueprint judgment, missing pixel coverage/diagram response, and independently failed visual quality. Honest blocked preflight with drafting not started remains a valid partial declaration.

The `example.invalid` corpus and placeholder bytes in tests are explicitly synthetic, not ten actual published papers or a false live evaluation. A test cannot recognize a dishonest all-pass receipt or a weak semantic observation. Tests check that recorded missing/failed work cannot satisfy completion, while independent review checks reasoning about the interface. Actual ten-paper learning and EN/ZH manuscript/figure improvement remain for the main task and user acceptance.

Independent reviewer found and fixed a staged-partial mismatch: visual_design.mode now permits honest staged work with reason while only independent collaboration can support submission completion. The reviewer also exercised 40 malformed visual/source field combinations without crashes.
