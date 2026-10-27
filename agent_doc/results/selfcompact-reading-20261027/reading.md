# SYSTEM-99: self-compaction and host ownership

Primary [Self-Compacting Language Model Agents](https://arxiv.org/html/2606.23525v2), Tianjian Li et al., **2606.23525v2**, revised2026-07-10T18:13:00Z (v1 June22). The [Apple page](https://machinelearning.apple.com/research/self-compacting-language-agents) is dated October2026; that page date is not a new arXiv version. Checked2026-10-27. Actual HTML main§§1–7/Algorithm1/Tables1–10/captions1–3/AppendicesA–D read; references incidentally displayed, AppendixE not read. No PDF pixels, author-code execution or raw-run reproduction.

## Method, experiments, ablations and limits

Append-only same-model rubric probes gate summarize-and-replace; continuing removes probe messages. Prefix reuse is assumed. Math uses16samples/question, four models/three benchmarks; single-round uncompacted baseline has less compute. Search uses150questions/benchmark, three models; Table5 reports five-run variability; rubric ablations cover only selected models. A gold-answer oracle is unavailable operationally. Quoted evidence is not independent factual verification.

AppendixB adds minimum-round/token gates, summary cap and forced threshold; this is not unconstrained adaptive timing. Search summarizer discards uncertainty, conflicting with this repository's preservation needs. Costs include assistant/probe/summary calls but use cached-rate approximation; AppendixD lifecycle splits are not provider cache-hit receipts. Search/tool infrastructure cost and end-to-end latency remain unestablished. Several fixed-summary comparisons cost less than SelfCompact. No coding-task or multi-agent correction-propagation evaluation is demonstrated.

Unresolved source contrasts require code/raw-data adjudication:

| Location | Contrast |
| --- | --- |
| Table1 / §4.1 results | thinking-disabled / thinking-enabled wording |
| AppendixC / Table10 | ±3k budget match /47.9k−44.1k=3.8k |
| AppendixB / Table7 | rubric minimum40k /GLM forced threshold38.4k |

They do not establish a repository defect. Defer policy adoption.

## Current entry/source audit

Static at332ffb9b, no CLI execution, tests, inference, model discovery, installation or old probe retry:

- `model_routing.py` accepts explicit host-declared availability/capabilities, resolves once, and dispatches exactly one selected handler. Fallback means host default with availability unverified; provider/model differences do not certify independent review. Handler owns authentication, loop, permission and budget.
- `run_role.py` loads installed role/Skill definitions and checks installation before dispatch. It budgets the canonical local request, including definition/route/task, but excludes host-added context/provider sessions. Native runner passes one prompt to the host CLI; adapter receives one JSON request. Neither source implements the paper's rolling-context replacement, KV ownership or delayed/hard reset semantics. Changing these requires a separately evidenced host interface, not another shared memory/chat pool.
- Adapter inventory failure falls back before task launch; execution failures/timeouts do not retry. Its unbounded temporary stdout capture is the previously paused branch, not a new discovery, and was not executed/rebuilt/reset here. Timeout status alone still does not prove descendant/provider cleanup.
- `discover_backends.py` reports module/executable/metadata presence with readiness not_verified and authorized false. Top-level find_spec avoids parent-package initialization for dotted names; this is not an arbitrary-import-hook sandbox or actual backend call. `setup.py` check excerpt verifies installed artifacts/managed links/block and inventory metadata; it does not prove current host session loaded them.

No new confirmed production defect or performance result. Preserve exact guidance/corrections/negative evidence and default routing; defer self-compaction until a trusted host can bind actual input/session ownership, safe replacement boundaries, required dependency preservation and all-call/cache/latency observations. Existing nineteen-body chain gains this one distinct body:20. Old frozen/exhausted branches and SYSTEM99 Plan50 remain unchanged; no optimization round completed.

## Discovery and evidence

Prior query `self compact role model ownership`:306scanned, partial=true,25errors. Five run IDs/hashes are in inputs.json; metadata only, no matched empirical reuse or exhaustive-absence claim. Current tracked agent_doc had no2606.23525 match before reading; lost/private history is not reconstructed. Author repository metadata only: https://github.com/tianjianl/selfcompact main, pushed2026-06-26T03:34:49Z; no author-code version/behavior inferred. Cached body/abs hashes, actual text ranges and source pins are in inputs.json. Independent report review is required before publication; catalog history remains unknown without trusted runtime acceptance.
