# INGEST-PUBLICATION-DIAG-01: independent result review

Verdict: **usable-with-scope** for the two finite diagnostic observations below. Both phases intentionally fail the proposed safety assertions; this is not a passing regression or a repaired implementation. No production change or rollout is accepted. SYSTEM-99 and the system-level round remain open.

## Code, inputs, execution and evidence identity

I independently reviewed the full frozen probe, execution wrapper, source publication sequence, KnowledgeStore loading/link/snapshot rules and relevant current ingest tests during plan review. I then inspected the actual complete producer log, observations and summary, compared all plan bindings to actual bytes, executed exactly one independent phase, and inspected its complete log, observations and summary. All plan-v1 production, fixture and prior-search SHA-256 bindings matched before and after replay. The reviewed plan SHA is `dde1c539aa2981da7eef151cb8b26e53bc722f9332c0174943704416ea1ea147`; probe SHA is `ae5af95966bccef715c0eaf4859b3182256f654cefee20f906611d03c2808d81`; wrapper SHA is `26cbc11734933e0aa218ecdbe84070690cda71e3a5f26c58399e3683be9a2626`; six-domain validation-plan SHA is `45d94e9d5b20de5522878a3401fed793d2dfc783b6069e41c237ddd61b809164`.

Authorized independent command, run once from the project root: `python .agent-runs/ingest-publication-1600/run.py independent`. The wrapper's actual child command was `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python .agent-runs/ingest-publication-1600/probe.py`. Each phase used fresh temporary corpus/input directories. Environment in both summaries: Python 3.12.14, Linux-6.18.55-x86_64-with-glibc2.39. The independent tool call directly returned exit 1. The producer summary also records exit 1; a surrounding shell's later successful cat command cannot change that result. No other tests, suites, CLI/model/backend probes or retries were run by this reviewer.

| Frozen result artifact | SHA-256 |
| --- | --- |
| producer.log | `ee5e853d54431c6636369537a97cd2c3972aa4eee5cad5517607e98195ee492a` |
| producer-observations.json | `88a0e0d8b9235a7888594d3d53dfcbeaa15b8e6e609eca7517075a0d99027aa6` |
| producer-summary.json | `d06d6ed839110a74b69197f50582aff9bb21e41f0b337418db920369d0307cce` |
| independent.log | `ee5e853d54431c6636369537a97cd2c3972aa4eee5cad5517607e98195ee492a` |
| independent-observations.json | `01fc07fb1594b6d4c39d821a1acd91fa7c3a43e8c121a69b8f0bfc45ca2c9134` |
| independent-summary.json | `5cd5f4c3d4442afd8a6cba4ee98277f3441d14424559c170d5082f4e1b022761` |

## Observed outcomes and causal interpretation

| Frozen case | Producer | Independent | Supported interpretation |
| --- | --- | --- | --- |
| Unchanged corpus | pass; receipt matches fresh live ref | same | Minimal normal-path fixture and import work. |
| Dependency removal during final copy | hook=true; refusal=null; imported entry exists; fresh store rejects missing target | same | Ingest returns successfully and publishes the candidate after its sole prerequisite pair was removed after final live snapshot validation. |
| Empty target claimed immediately before real rename | hook=true; refusal=null; preserved=false; target contains entry.json, entry.md, provenance.txt | same | The empty directory created by the simulated other owner is replaced by the ready entry on this filesystem. |
| Nonempty claimed target | hook=true; ENOTEMPTY; preserved=true; owner.txt remains; test passes | same, with different temporary paths | Ordinary nonempty-directory refusal and original owner content/identity are preserved. |

Each phase ran four methods with two failures and two passing controls, with no skips. Full unittest logs are byte-identical; observation JSON differs in the expected fresh temporary paths embedded in the nonempty-target OSError. The two failed assertion messages correspond directly to refusal=null in emitted data, rather than setup errors, skipped hooks or a timeout. In each failing test, the first safety assertion stops later assertions; I therefore checked the emitted later-state observations directly instead of claiming every later assertion executed.

The dependency hook calls the real final copytree before deleting the canonical dependency JSON and Markdown. It matches the candidate-folder to private `entry` copy, not the earlier whole-entries copy. At this point the combined staged corpus and final live snapshot have already been checked. Successful return is evidenced by no caught exception and subsequent observations; a fresh KnowledgeStore then reports `missing or self-linked target: math.publication-probe`. For a candidate, missing prerequisite target is still invalid even though published-only version/status rules do not apply. The injected deletion is external test action, not a claim that ingest deleted the dependency itself. The precise concern is successful candidate publication into a live corpus whose declared dependency closure is invalid; downstream readers cannot load that corpus.

The target hook creates a distinct destination directory just before the production call to the real os.rename. Production's prior existence check and final write guard have already run. It computes preservation by comparing device/inode before and after that rename. Empty-target preservation=false plus installed candidate files and no refusal supports replacement of that freshly claimed empty directory. The control adds owner.txt and confirms ENOTEMPTY, identical target identity and intact owner bytes. Numeric inode values are not separately persisted, so identity is an observation calculated by the reviewed probe, with its exact comparator frozen in code; no cross-filesystem inode claim is made.

KnowledgeStore explicitly disclaims an atomic filesystem snapshot. These results establish the described finite outcomes and why they can invalidate dependency/ownership expectations; they do not establish breach of a universal advertised transaction. No portable repair is proposed or validated.

## Six frozen validity criteria

1. **Problem alignment: pass.** Both intended late windows were reached in both phases, and both controls remain visible. The original intended-safety assertions failed as allowed by this diagnosis-only contract.
2. **Experimental/code correctness: pass with stated instrumentation scope.** Exact frozen sources/inputs were checked; actual hooks are on the production calls, and actual observations, assertion traces and exit codes agree. Minimal fixture is self-contained before injection. Full logs and original failures are retained. The independent phase used the same frozen source once and fresh temporary paths.
3. **Statistics/uncertainty: pass for existence witnesses only.** These are deterministic interposition examples, not random trials. Two phase observations do not estimate concurrency frequency, reliability, timing significance, scheduler coverage or a speedup.
4. **Comparison/context: pass.** No fixed implementation exists in this exercise. Prior search remains partial with 25 errors, so absence of matching retrieved results is not exhaustive history proof. Existing earlier-copy rejection/newline tests and U3 documents-specific Linux no-replace evidence do not replace these observations or authorize a portable ingest change.
5. **Resources/execution: pass.** Producer and independent were each run once. The exclusive phase claims exist, neither phase timed out, and both normal summaries/raw observations were written. Child runtimes are metadata only. Budget accounting below is within the original 600-second shared limit. No older exhausted gate was restarted.
6. **Applicability/limitations: pass with narrow scope.** Conclusions apply to the recorded Linux/Python/filesystem environment and these exact same-process interleavings. No multiprocess stress, hostile parent replacement, complete TOCTOU closure, cleanup identity guarantee, Windows/macOS behavior, model quality, performance, cost or whole-round acceptance is established. This is actual independent offline code/raw-data review and replay, not a host-authenticated runtime verifier proof.

## Budget and permitted consumption

Producer claim epoch: `1793088687.081697`. Independent claim epoch: `1793088711.9825644`; replay began approximately `24.901` seconds after producer claim, with more than 180 seconds remaining in the 600-second shared budget. Producer wrapper elapsed: `0.1149579269995229` seconds; independent wrapper elapsed: `0.11456724500021664` seconds. Derived producer-claim to independent child completion: approximately `25.015` seconds. At final report construction, wall-clock elapsed from producer claim is `101.929` seconds (epoch `1793088789.0106404`), still below 600. Wall differences assume the host clock did not jump; wrapper phase durations use monotonic time. No retry or budget reset occurred.


The results may support a scoped diagnostic checkpoint after the root's remaining publication checks, with both negative observations and passing controls preserved. They do not accept a production fix, authorize runtime reuse, or close SYSTEM-99. If registered as unknown historical references, retain that trust state and link this actual scoped review separately; do not substitute it for a trusted runtime result-verifier receipt. A future repair needs its own versioned plan, independent review, targeted evidence and applicable authorization/budget.
