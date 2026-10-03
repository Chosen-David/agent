# Cross-feature synthetic validation — 2026-10-03

Base: `15e633e07afbbffa1b5f6dea7984888bb3c8cabe`. Scope is agent repository only; no SGLang, private papers, paid APIs or external model service. Generic synthetic data only.

Decision: EXECUTE under explicit direct-main authorization. Pull before edits and fetch/reconcile before non-force push. Existing registry has 14 role tasks; reuse its organization case and host-driven `agent_eval_pipeline.py`, not a second receipt system.

| Feature | This task | Execution and evidence |
|---|---|---|
| Visualization | scale, units, uncertainty, protocol, legend/color; correct controls; Chinese PNG versus actual PDF pixels | actual figure generation + PDF render; declaration validator reported separately; blinded host inspection |
| Architecture reading | default/optional branches, consumers, dtype/shape, full/reduced, misleading docs | executable synthetic repo + anchored independent host reading |
| Paper delivery | research vs audit genre, ten abstracts, figure gaps, copying, nonexistent role execution, good control | actual file reads, validator behavior and separate semantic checks; blinded host evaluation |
| Runtime supervisor | repeats/restarts/idempotency/lease boundary/permissions/cancel/artifact gates | existing fault suites plus bounded additional executed cases |
| Coordination | consumer input-version mismatch | integrity validator versus semantic consumer check, explicitly distinct |
| Code organization | preserve scope and historical mapping, archive proposal, redundant comments | existing registry inputs, real role outputs, independent review |
| Noise / reviewer / experiment | OWNED BY parallel cloud task `01a10049` | not duplicated; remote integration later; not counted as this task's model passes |

Rubrics are frozen before execution. Each executable suite records individual observed outcomes and identifies false positives/negatives against its fixed expectations. Development and held-out cases have distinct parameters/content; no broad generalization from this small sample. No optimizing prompts on a holdout and still calling it held-out.

Host plan: prepare pinned snapshots → actual isolated collaboration worker dispatch → record real returned task identity/start → save model turn output and file hashes → collect → independent reviewer context reads artifacts and frozen rubric → grade/report. No worker sees oracle/rubric. Shared filesystem isolation is instructional, not security isolation. `model: unspecified` means host does not expose a verified model configuration; no paired model claims. If a role is not dispatched, record `not_run`.

Budget: roughly 8–16 cheap cases per program feature; one bounded host batch per feature, one independent review; at most one repair/retest for critical harness defects. Full repository, reader and offline reference checks at release. Runtime supervision core is under test; no cloud monitor installed or live autonomous service claimed. This controller continues work in the current host session.

Dependency DAG: pinned main → frozen fixtures/rubrics → program runs + host workers → independent acceptance → bounded repair/retest → full tests/offline refs/diff → fresh main integration → non-force push and remote SHA check.

Completion update: concurrent noise/reviewer/experiment main `e6711ad785f8d931c426041773ed64cb40357c54` integrated without conflicts; owner evidence linked in README. Five real host batches executed, with separate independent acceptance and explicit shared-filesystem limitations. Final results preserve declaration-layer false negatives and paper production coverage gap.
