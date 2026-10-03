# Figure record

Run: forward-figure-split. Route: mixed. One executing agent owns the full figure and sequentially applies the bundled diagram and data-visualization workflows. No independent agents, network, installations, or outside research inputs were used. Input SHA-256 hashes and software versions are in manifest.json.

Panel A uses architecture.json; primary editable source panel_a.py. Evidence: proposed synthetic specification, explicitly not implemented. Semantic contract: six supplied nodes; directed data-flow edges a→sum, b→sum, sum→softmax, softmax→output, v→output. A and B are parallel; V bypasses softmax. No extra edges, feedback, or experimental claims. The pale fill highlights the merge-to-output sequence, not performance or implementation status.

Panel B uses measurements.csv; primary editable source panel_b.py. Evidence: supplied timing table, with acquisition provenance unspecified. All four records and eight numeric values are displayed unchanged. No missing fields, aggregation, normalization, connecting categorical lines, uncertainty imputation, significance testing, or hidden exclusions. Units derive from column suffix _ms. End-to-end and kernel-only scopes occupy separately titled axes with explicit different ranges. Large candidate 220 ms versus baseline 200 ms remains visible.

Composition source: compose.py. Both panels are drawn into one Matplotlib figure, preserving vectors and editable SVG text. Separate panel SVG/PNG exports accompany the assembly. No raster screenshot is used for SVG composition.

## Design

Provisional final size: 180 × 112 mm, with A above B. DejaVu Sans, 10-point panel headings, 8–8.5-point labels, 7.2–7.5-point secondary text. Gray squares and blue circles redundantly distinguish baseline/candidate. Category identity in B does not claim identity with path A or B in the diagram. Diagram arrows are neutral. Alignment, direct numeric labels, restrained grids, and dedicated legend space support reading. Unknown venue requirements prevent any submission-compliance claim.

## Actual execution and checks

Executed `python compose.py` successfully from the outputs directory using Python 3.12.14 and Matplotlib 3.10.8. Matplotlib and Pillow provide local plotting and preview generation. A capability probe found CairoSVG unavailable; it was not used or installed. Programmatic checks verify all eight timing values, all six nodes, exact five edges, parseable SVG and unique IDs; see programmatic_qa.txt. There are no external image resources. Source SVG text depends on a compatible DejaVu Sans font environment and is intentionally editable, not outlined.

Actually opened and inspected with the image-view tool: figure.png, final_size_preview.png (180 mm represented at 110 dpi), figure_gray.png, and page_preview.png (A4 page embedding). This is a screen-based final-size approximation, not a calibrated physical print or publisher upload check. One render-and-inspection round was sufficient; no revision was required.

| QA dimension | Status | Actual observation / limitation |
| --- | --- | --- |
| Scientific preservation | pass within supplied evidence | Proposed status is prominent; supplied timings are not described as validated measurements of this architecture. External validity is unverified. |
| Numerical preservation | pass | All values labeled; the unfavorable large workload is retained; kernel-only is separated. |
| Semantic preservation | pass | Both logits enter sum; sum enters softmax; V enters output only; arrows point to correct boxes; no added connection. |
| Hierarchy and reading order | pass | Bold A/B labels and concise headings; clear left-to-right method flow before timing panel. |
| Typography/final size | pass for inspected preview | Formula, node labels, tick values and caption note are readable; no cropping or overlap at 110-dpi final-size preview. |
| Palette/accessibility | pass for grayscale inspection | Circle/square shapes preserve identities when color is removed. Color-vision simulation was not performed. |
| Whitespace/layout | pass | Node boxes align; legend stays above plots; direct labels and axis titles do not overlap. |
| Legend and annotations | pass | Baseline/candidate markers match displayed values; scope titles are distinct and units appear on both axes. |
| Technical | pass locally | Valid SVG, unique IDs, no external resources; PNG exported at 220 dpi. Cross-application font substitution not tested. |
| Reproducibility | pass locally | Successful execution, editable sources, input hashes and versions recorded. Original inputs remain unchanged. |
| Submission specifications | unverified | No journal, template, physical proof, or output specification supplied. |

Status: ready-for-review as an evidence-bounded figure draft. Missing research information remains timing provenance, repeat counts, uncertainty and evidence connecting the timing table to the proposed architecture; these were not invented. No separate model-based aesthetic review was performed.

Rebuild from the outputs directory: `python compose.py`. It reads the supplied sibling `../inputs` directory and recreates all SVG/PNG exports and the manifest/technical checks.
