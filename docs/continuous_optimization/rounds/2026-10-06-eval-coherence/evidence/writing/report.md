Publication transport note: the complete immutable archive is distributed as [two checked parts](split-archive.md); reassemble before the commands below. Original hash and scientific evidence are unchanged.

# T24: three complete working-paper executions

All three first **collected** manuscripts pass the eight frozen working-paper criteria: 24/24 judgments, no hard evidence violation or actionable independent reader finding. This is targeted execution evidence on unchanged baseline `e8ee3dca5dc8cd076fc031dd4510dabde214e046`, not a demonstrated writing-model improvement or final repository release.

| Paper | Complete PDF | Independent science | Independent page reading | PDF SHA256 |
|---|---|---|---|---|
| Pending observation and local dispatch semantics | [systems-paper.pdf](systems-paper.pdf), 7 pages | 8/8; actual frozen-core replay, all84 CSV rows and test-results bytes agree; copied source compiles | 7/7 | `0a57d3dfb82b0aa28032c80503ca2507a6ee20e65219e406b938e708c79baed6` |
| Exact blockwise attention and operator boundaries | [attention-paper.pdf](attention-paper.pdf), 6 pages | 8/8; independent CSV aggregation and numerical replay, copied source compiles | 6/6 | `322b63a0b43550840626b95c46405dbf3a057ae440b09c0d189bf555d8403e74` |
| U-Net padding, alignment and boundary contract | [unet-paper.pdf](unet-paper.pdf), 6 pages | 8/8; four core result files and48 output arrays replay exactly, independent reverse2D support check; source compiles | 6/6 | `6785f8faa4ff2852aee255ad71efad9ee97a96c48135caaadc9abfff02f15551` |

Each author loaded the pinned research-write entry/dependencies in a fresh context, received only its task and scientific inputs, and produced editable LaTeX, complete PDF/text, evidence/citation records, source/figure material and a blueprint implementation map. Ten distinct published exemplars (182 selected physical pages, including three duplicated reference pages) and root-approved preflight/template/blueprints preceded drafting. Scientific evidence came from actual controlled CPU experiments, not the exemplar results. The actual data-visualization role supplied five original figures before writing; author, independent reader and scientific reviewer inspected the resulting pages.

The independent scientist read each whole manuscript before its companions, then checked actual primary-source passages, mechanisms, raw data, code and replays. Separate independent reader coverage is19/19 physical pages. The root separately read all19 pages. The U-Net scientific review and reader findings were released only after the root froze the no-writing-prompt-edit decision following the first two papers. Details: [systems](systems-scientific-review.md), [attention](attention-scientific-review.md), [U-Net](unet-scientific-review.md), plus root-owned acceptance records.

The writing Skill was not changed to manufacture an upgrade: the three bounded tests, with substantive evidence and completed blueprints, already produced acceptable scientific argument and prose. The systems paper's broader scheduler related work is still insufficient for a novelty-oriented venue submission; its actual predecessor comparison and limited scope are explicit. All papers retain negative outcomes and avoid GPU/training/latency/quality extrapolation. This does not establish success on an arbitrary complex user manuscript, formal submission readiness, or a causal benefit of any new prompt. Exact model snapshot, random seed, aggregate tokens/tool count and cost are unknown. Authors made permitted within-attempt build/layout revisions; 3/3 first-collected passes is not a raw-generation success rate.

## Reproducible evidence

`full-paper-evidence.tar.xz` contains the original pipeline, pinned instruction snapshot, three frozen catalogs/input packages, actual normalized host receipts, every collected output byte, exact independent grades and compact reading/review records. Identical byte sequences use internal archive hardlinks;178 duplicate files are stored once. Third-party original PDFs/page pixels and the private user sample are excluded. Generated review builds/replays/page renders remain reproducible and hash-indexed; no collected author file is omitted.

The16,379,932-byte archive was extracted into a fresh directory using `tarfile` with `filter='data'`: all637 indexed files matched, then the existing pipeline reproduced3/3 accepted tasks with no integrity error. See `archive.json`, `archive-replay.json`, `report.json` and `summary.json`. After extraction:

```bash
python controller/pipeline.py report --run run --require-complete
```

This replays evidence validation, not model inference. Full sources and case reproduction commands are inside each `run/cases/full-paper-*/attempts/0001/outputs/paper/` directory. Host receipts record observed execution; shared filesystem isolation is instructional, not cryptographic attestation. No external backend integration, production deployment or repository publication is established by this evidence. Final-candidate all-role acceptance remains a separate gate.
