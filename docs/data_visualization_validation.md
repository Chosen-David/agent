# Data visualization learning extension — 2026-10-03

Baseline pulled before edits: `ccaba02`, preserving supervisor/runtime, experiment and prior exemplar work. Scope is the existing research-data-visualization role; no SGLang changes or private manuscript/data committed.

## Evidence and repair

The existing data_visualization_workflow already requires traceable values, uncertainty boundaries, final-size visual inspection and style fidelity. The actual missing links were: research-data-visualization/SKILL.md had no exemplar-learning link; the exemplar bundle omitted that role; paper delivery only had architecture visual-design fields and checks. No claim is made that the previous role permitted invented data.

Added `workflows/data_visualization_learning.md`, locally bundled to data visualization, figure coordinator, orchestrator, writer, reviewer, PDF reader and diagram role (for cross-branch link closure). `workflows/paper_exemplar_learning.md` routes data charts separately from architecture figures. The existing data visualization workflow calls learning before full design/code. Current paper task reuses its required ten-paper corpus; ordinary standalone plots use task-appropriate examples and are not forced through the full-paper CLI.

Data-specific reading covers comparison/chart type, axes/scales/baselines, error/uncertainty, encoding/accessibility, palette/legend, typography, layout/density and panels. It requires real original pixels, a data-visual-design-brief and actual reader→research-data-visualization results. The final language variants have implementation maps and distinct data_scientific_fidelity/data_visual_design judgments. Captions and plotted labels preserve EN/ZH numeric/semantic parity.

`validate_paper_delivery.py` calls `data_visualization_checks.py`; distribute it alongside the existing scripts. Records add data_visualization_requested and exemplar_learning.data_visual_design. The check validates source type, zero baseline declarations for bars, uncertainty source/n/replication information, exclusions provenance and requested final evidence. It does not inspect numerical arrays or certify honesty from booleans. Real data, full figure inventory, receipt truth and semantic quality remain reviewer responsibilities. A generic style adjective cannot replace eight structured observations and source positions, but the program cannot detect empty-quality prose disguised as those fields.

## Open-source selection and adoption

Exact commits/file hashes are in `data_visualization_sources.lock.json`; both sources' MIT licenses were read. No third-party code, templates or figures copied into this repo, and no new dependency/runtime installed.

- K-Dense-AI/claude-scientific-skills: `skills/scientific-visualization/SKILL.md`, `scripts/palette_audit.py`, `assets/publication.mplstyle`. Adopted principles of faithful encoding, interval definition, redundant color encoding and final-file inspection. Ran the actual network-free palette audit on its bundled okabe_ito_on_white palette: background screening had 0 review flags, heuristic grayscale screening had 4 pairs requiring review. Saved unmodified output in `data_visualization_palette_smoke.json`. This is a tool smoke test, not a manuscript chart or accessibility certification. Did not inherit dated publisher profiles, package-version claims, promotional citation instructions or treat a palette as a guarantee.
- tvhahn/matplotlib-skill: `skills/matplotlib/SKILL.md` and actual `patterns/P8-multi-panel.md` code. Useful: inspect rendered elements before judgment, match comparison task, align panels. Rejected blanket `.dropna()`, top-N/aggregation for appearance, fixed column counts/spacing and forced insight annotation. Those can remove scientific information or impose unrelated personal style. Matplotlib remains an optional existing-tool route; no external persona replaces local evidence constraints.

Current candidate entry links and applicability are also bundled in the new workflow for plugin users. Sources are guidance for design, not scientific evidence for the user's paper.

## Validation and independent review

```bash
python scripts/sync_plugin_references.py --check
python -m unittest discover -s tests -p test_paper_delivery.py -v
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

Focused 31 tests; full repository 227 tests; reader 3 tests passed at this snapshot. Tests are synthetic declarations, not ten actual readings or measured figure improvements. New cases reject absent pixels/role response/skill selection, abstract-only sources, palette-only pseudo-analysis, truncated bars, reported→measured relabeling, placeholder final results, invented uncertainty, missing exclusion records and absent per-language implementation. A traceable reported SD with actual replication definition can pass without inventing raw samples. Staged partial remains honest; completion requires independent collaboration.

Independent reviewer additionally tried 100 malformed field combinations without crashes, rejected sources outside the ten-paper corpus and missing analysis, and confirmed honest staged partial handling. Final host runs and remote readback are reported in the release handoff. Actual corpus learning, real data-figure redesign and user acceptance remain in the main task; this repository change is not proof that those have occurred.

Task DAG was validated privately against agent_runtime.core. The host coding-action adapter and persistent scheduler are not bound, so no background monitor was claimed or started; authorized work continued in this active session.

Latest user steering pauses manuscript work and prioritizes agents. Added a small-difference/noise handoff to research-review with location, delta, units, replication/noise gaps and a minimal discriminatory remeasurement plan. No experiment/reviewer core was modified, leaving the concurrent statistics upgrade independent. Empirical superiority declarations require traceable uncertainty plus reviewer statistical evidence; the program does not certify the test or estimate noise.
