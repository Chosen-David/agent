# Figure delivery and QA

- Figure/run ID: FIG-timing / fig_timing_20261003.
- Route: data_visualization; role: result; owner: current independent execution agent.
- Status: ready-for-review. Submission specifications remain unverified.
- Primary skill: research-data-visualization, supplied local version. Read SKILL.md, execution.md, workflow.md, and figure_shared.md. Used installed local matplotlib directly; no web lookup, installations, external services, or additional statistical analysis.
- Purpose: compare supplied Baseline and Candidate elapsed times while distinguishing timing scopes.
- Evidence: supplied numerical timing table; actual acquisition and whether values represent single runs or summaries are unresolved. No measurement protocol was inferred from the filename.

## Sources and editable deliverables

Original: `../../inputs/measurements.csv`. Byte-identical snapshot: `measurements_snapshot.csv`.
SHA-256: `57201d75a6e7ea0b7581c2d94f4bf46c2b9a66e37b5df94c8e6b4c5ef3924248`.

`plot_timing.py` is the editable plotting source. `timing.svg` retains editable text and vector marks; `timing.png` is the 300 DPI export. `caption.md` supplies Chinese and English captions. `plotted_values.csv` records the eight rendered point values. `numerical_qa.json` and `technical_qa.json` record actual checks and software versions.

Reproduce from the frozen snapshot with:

```bash
python /tmp/agent-forward-figure-split/research-data-visualization/outputs/fig_timing_20261003/plot_timing.py
```

The script uses its own directory for output and font cache. It overwrites only this run's generated products. The source CSV in inputs is never modified.

## Design

Provisional figure size: 180 × 100 mm; no venue supplied. Two vertically aligned panels separate `end_to_end` and `kernel_only`; shared linear 0–250 ms scales preserve absolute positions. Workloads are categorical and retain their input order; points are not connected. The kernel panel intentionally retains blank horizontal space to keep the common scale explicit.

Baseline uses blue circles (#255c85); Candidate uses orange diamonds (#c66523). Series identity is also encoded by vertical offsets and the legend. Font: DejaVu Sans, 8 pt ticks and point values, 9 pt labels and legend, 10 pt panel headings. Direct value labels make all data inspectable. Light x-gridlines and sparse spines keep emphasis on points. Legend occupies reserved top whitespace.

## Executed checks

| Check | Status | Evidence / observation |
| --- | --- | --- |
| Scientific scope | pass within supplied evidence | Kernel-only data separated from end-to-end; caption discloses unknown acquisition, n and errors. |
| Completeness / numerical preservation | pass | Four rows, eight points; plotted scatter x-coordinates matched every source value exactly with no tolerance needed. No missing fields or duplicate workload/scope keys. |
| Transformations | pass | Numeric parsing and categorical placement only; no aggregation, normalization, fitting, smoothing, exclusion, or uncertainty estimates. |
| Unfavorable outcome retained | pass | Large workload includes Candidate 220 ms and Baseline 200 ms. |
| Hierarchy | pass | Two bold panel headings make scope separation clear; values and markers remain the central information. |
| Typography / clipping | pass | Actually opened final `timing.png` and 120 DPI `timing_final_size.png` using the image viewer. All values, workload labels, titles, ticks, and legend are visible without overlap or clipping. |
| Palette / accessibility | pass for inspected conditions | Actually opened `timing_grayscale.png`; circles and diamonds remain distinguishable and direct values remain readable. No color-vision-deficiency simulation performed. |
| Layout / whitespace | pass | Panels align and share tick positions. Legend does not cover data; kernel values remain distinct despite their closeness. |
| Page embedding | pass for preview | Actually opened `timing_page_preview.png`, with the 180 mm-wide figure placed at 1:1 intended size on a 210 × 297 mm blank page. No crop or loss of readability observed. This is a page-context preview, not a verified publication template or physical print test. |
| Technical export | pass | SVG parsed; IDs unique; internal href references resolve; no external href resources; editable text retained. PNG size and DPI recorded in technical_qa.json. Fonts referenced in SVG, not embedded; substitute fonts can change appearance in other environments. |
| Reproducibility | pass | Plotting script executed locally using frozen input. Actual runtime/library versions and input hash recorded. |
| Submission | unverified | No venue/template specifications supplied. |

Visual inspection round 1: inspected color export, final-size preview, grayscale preview, and whole-page preview. No concrete clipping, overlap, data omission, or incorrect labels were observed, so no cosmetic revision was necessary. The image tool's display does not establish physical monitor calibration or print appearance.

## Limits

Independent experimental units, repeat structure, sample sizes, hardware, timing protocol, and error definitions are absent. The plot communicates exactly the supplied values and supports no uncertainty or significance claim. The kernel-only improvement cannot establish an end-to-end improvement. No new measurements or statistical analyses were performed.
