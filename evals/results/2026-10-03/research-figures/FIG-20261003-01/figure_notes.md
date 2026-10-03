# FIG-20261003-01 — execution record

Status: **ready-for-review**. Dimensions are provisional: 180 × 85 mm, 8–10 pt text, 300 dpi PNG, text-editable vector SVG. No venue compliance is claimed.

## Scope and source

Mode: results + single-figure. Question: how does candidate latency compare with baseline at each workload and timing scope? Source: `../../inputs/measurements.csv` (4 data rows). Exact input SHA-256 and actual Python/Matplotlib versions are in `metadata.json`. The CSV's timing values are accepted as supplied; hardware, timing protocol, measurement provenance, independent experimental units, pairing, replication and whether values are summaries are unknown. Each row supplies one reported timing per method; this is not evidence that experimental n = 1.

Data audit: no missing cells, no duplicate workload/scope keys, all timings positive, units `ms` from column names. No data excluded, no aggregation, no fitting, no smoothing. Workload labels are categories; no lines imply continuous trends. All four rows are retained. No overall pooled speedup is computed across workloads or scopes. No new experiments were run.

## Figure specification and tool choice

Role: results comparison. Evidence: user-supplied numeric timing table, provenance beyond the CSV unverified. Panel (a) end_to_end small/medium/large; panel (b) kernel_only kernel. Grouped bars start at zero. Baseline is solid slate, candidate teal plus hatching. Explicit percentage labels expose the large regression; scopes are separated with titled panels. Different y-axis scales are explicitly disclosed in the figure and caption.

The provided research-figures SKILL.md, execution supplement, workflow section 1 and task-relevant sections including the complete section 6 prompt were read. Existing local Python 3.12.14 and Matplotlib 3.10.8 covered deterministic data plotting, editable SVG export and PNG rendering; actual imports and rendering succeeded. The supplied skill entry allows direct execution when existing capabilities suffice, so no external skill search, installation or claim about latest available tools was made. No other skills, repositories or sibling task directories were inspected. The initial Matplotlib import reported a read-only default configuration directory; the delivered source sets MPLCONFIGDIR to its own writable output subdirectory and the build succeeded without that warning.

Main editable source: `plot_results.py`; SVG also retains text elements. Data transforms are separate from style settings. `derived_values.csv` retains raw numerical values and records percent latency change plus speedup = baseline / candidate, with no display rounding in that snapshot. `caption.md` gives the scientific wording and limitations.

## Actual visual inspection and revision

Two render/view rounds were performed using the image viewing tool, opening both the 300 dpi final PNG and a 120 dpi size preview. The first round revealed overlapping percentage/value labels above large and kernel, and unnecessarily long precision for the medium percentage. The source was revised to add vertical annotation space and round the displayed percentage to one decimal where needed. Both PNGs were regenerated and opened again.

On final visual reading: all bars and numerical labels are visible; percentage labels no longer overlap bar labels; legend, panel headings, axes, units and both footnotes fit within the canvas; hatching distinguishes candidate independently of color; the large regression remains prominent. The preview preserves the intended 180 × 85 mm proportions and the figure uses the stated physical dimensions. Actual on-paper print appearance and external SVG editor font substitution were not checked. SVG structure was programmatically inspected, not separately rendered by an independent SVG engine.

## Reproduction

Run from any working directory:

```bash
python /tmp/agent-forward-v1/research-figures/outputs/FIG-20261003-01/plot_results.py
```

The script locates the original input relative to itself. Keep the provided inputs/outputs directory relationship when moving the project. Dependencies: Python standard library and Matplotlib 3.10.8. The script generates both exports, the preview, derived values and metadata. No post-export manual graphical edits are required. Data assertions fail rather than silently treating missing values as zero.
