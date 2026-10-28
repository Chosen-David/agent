# Independent source review — SYSTEM-99 / Plan54 / WTB reading

Decision: **accept, usable with the stated reading/source-review scope**. No blocking correction to the frozen reading record was found. This does not approve a new experiment, runtime dispatch, implementation, publication, budget reset, or SYSTEM-99 completion. Trusted runtime acceptance remains **blocked/unknown** because this manual review is not an authenticated ReviewSession.

## Frozen object and independence

Repository: Chosen-David/agent, HEAD `cabd8ba9d15a82c192975459553a0b5e1dc696f8`.

Reviewed only the assigned reading record and its stated source/code relationships:

- `agent_doc/results/wtb-authority-reading-20261029/reading.md`: SHA-256 `b3b7dffc8013c1ad443549a1609a262e4e3da1d38f4341f286ede95abc45728a`.
- `agent_doc/results/wtb-authority-reading-20261029/inputs.json`: SHA-256 `aa86178e61bb40b2936e2bce1255a9959081d7fe9f05531531e0d3bd06c7eaa8`.
- `.agent-runs/continuation-0002/paper.txt`: SHA-256 `f695265d11546f431f51b37f00374da763f6e52661838852eb4906b2a4523324`, 103697 Unicode characters / 104128 bytes.
- Cached `paper.html`: `58de7494f8b2b39f70a2327a21cec19ab78b18c29ed83c4dff42c2f90fc3a57c`; cached `abstract.html`: `5bc6216c6994c1ec0eefeee70404fba0101801b6be1a4ed93d4b1a7279c639f9`.

All listed primary hashes, all seven repo/document refs, the saved knowledge-query hash and saved prior-result-search hash in inputs.json were recomputed against actual files and matched. The frozen reading/inputs hashes and HEAD also matched. HTML hashes establish cached-byte identity; no independent live-network authenticity or PDF rendering verification is claimed.

This is the one dispatched independent invocation `/root/wtb_reading_review_0100`. Primary scientific findings were formed before opening reading.md/inputs.json; an interim message to the parent recorded that ordering. There was no retry, replacement, delegation, test, model/backend experiment, monitor operation or lock operation. Only this assigned review file was written. Parent-owned lock/session 32350 was not touched. Total role tokens and cost are **unknown**, not zero. Host-authenticated fresh-context/budget proof is not exposed by this review file.

## Actual read scope and primary findings

Independently read cached normalized primary text covering scientific main §§1–11 before character 36892 and appendices A–L in [41734,103697), including Tables1–22 and Figures1–4 captions/text. Reads were overlapping bounded slices; the final slice includes the HTML footer, which receives no scientific credit. References [36892,41734) were not independently audited. No PDF pages, rendered figure geometry, author implementation, full companion package, raw per-item traces, regenerated tables/statistics or end-to-end experiments were reviewed. Cached HTML and abstract were hash-checked, not fully visually inspected. Author submission timestamps are cached-provenance statements, not independently authenticated live facts.

The independent primary conclusions, then compared with the frozen record, are:

1. §§2/A give a state/request-domain factorization criterion, not a model guarantee. Lossless raw/typed representations preserve the admitted-information partition while actual policies can differ. The balanced-pair binary 1/2 result does not predict completion when abstention is allowed. Appendix E explicitly separates C0 safe BLOCK from resolved semantic success: correct retained bytes can still score zero completion, and zero unsafe adoption is a different outcome. The frozen reading preserves these distinctions.
2. §§3/B bind current exact attempts, matching terminal evidence, actor/scope generation, exact material admission version/contribution chain, and approval snapshot. Same bytes do not erase version identity; revoke/regrant does not preserve generation; an old successful attempt does not authorize its replacement. Local serial check/consume/commit and receiver atomic token-check/deduplication have separate preconditions and commit predicates. No global policy/remote-write ordering follows from a local pre-send check. The record states this correctly.
3. External recovery requires the immutable reservation and common effect key. Applied lookup returns an existing receipt; authoritative absence permits a fresh snapshot-checked resend without checking Unconsumed again, because reservation already consumed approval. Unknown remains pending. Availability additionally needs reliable eventual lookup, stable admissibility and reachable sink. These are cooperating-receiver assumptions shared by complete controls, not a unique WTB proof of arbitrary remote effects.
4. Appendix C distinguishes DSH durable receipt lookup from unavailable checkpoint rewind; process-local LangGraph provider identity cannot establish continuity merely from the same checkpoint path; Ray disables native retries and does not establish driver-restart reconciliation. JSONL/SQLite closed-store same-backend moves are narrower than uniform adapter/process restart or cross-backend portability. The record does not overgeneralize them.
5. R0/W0 both score 32/32 semantic successes. Planning raw-to-typed unsafe proposals improve for DeepSeek (8/8 to 0/8) and worsen for GPT Nano (1/8 to 6/8); all eleven W0 unknowns are DeepSeek, including seven unauthorized rows. Fixed saved W0 intents yield six unsafe proposals blocked, 0/16 unauthorized effects and 12/12 eligible authorized intents executed; four authorized rows lack valid intent. Enhanced Git/Auth/CONTINUITY/MasDrift and WTB all pass56/56. The record correctly avoids a universal typed-planning or architecture-capability advantage.
6. The 960 ablation cases reuse six captures, rather than being 960 fresh native executions; 24 live executions cover two runtimes. Exact-attempt/generation/consumption removals yield12/6/12 unsafe effects; conservative unknown handling loses availability without adding unsafe effects. Legal-correct includes effect count, not just completion flags. Neither named schedules nor aggregate counts establish production fault prevalence.
7. Paid adoption compares documented unequal native packages and arm-specific supplied predecessors. Stages are independent starts; E0–E2/full bundles do not prove a persistent candidate survived them. Three benchmark-source tasks yield176/210 WTB accepted stages and19/30 publication slots, with competitors better at some stages. Construction effort is outside the estimand. Prospective SWE uses qualified reference-patch governance integration, not autonomous issue solving; later code can repair earlier failure. Core5/8→recovery8/8 and handoff4/8, with Holm .09375/.375, do not establish familywise significance.
8. Continuous E3–E6 consumes preceding accepted candidates, unlike independent adoption.117 complete observed trajectories/468 outcomes include method failures and predecessor-blocked stages but exclude unresolved operational interruptions; denominator9/10 and selection effects remain material. No selective replacement is allowed by the reported protocol. All nine adjusted comparisons exceed .05 (minimum .28125). The8067 completed-response records/$27.615736318 are conditional analyzed spending, not the full scheduled-call bill. Joint-success costs and accepted-code means are selected subsets; cheaper comparator examples remain. Compact reconstruction omits the complete fresh-execution stack.

No numerical discrepancy or missing qualification material enough to block this reading record was found. These findings validate accurate reporting of author claims within the read scope, not the authors' underlying empirical truth.

## Selected actual repository source comparison

Read actual source excerpts rather than trusting the report's source labels:

- `agent_runtime/core.py` Context.current, Engine._authorized/_review_plan/_check_done/reconcile/_summary and tick through claim, expiry and returned-outcome handling (approximately lines235–565). Context.current checks local run/token/status/lease. Done evidence is verified anew and invalid dependency closure propagates. Terminal invalidation/review-after-effect carries reconciliation fences; expired non-idempotent work is ambiguous. Explicit reconciliation requires current review, authorization, dependencies and verifier. None authenticates a third-party receiver or makes a remote write atomic.
- `agent_runtime/task_supervisor.py` submit-review/backend references and publish/ManagedEngine.tick/worker completion excerpts (approximately151–255). Managed dispatch revalidates document contract; derived reporting is refreshed, and terminal completion paths recheck evidence. No live worker was invoked or deployment inferred.
- `agent_runtime/task_manifest.py` ReportingHandler.run/verify and review (approximately360–559). The wrapper checks documents, knowledge, memory and result/reuse dependencies, repeats checks around callbacks, requires current claim before dispatch, and binds the report proof plus actual handler verification. The report view is derived; checkboxes cannot manufacture SQLite completion.
- `agent_runtime/publication.py` controller/callback contract and state save (approximately201–237), freeze tail and current/evidence/plan-review/acceptance/commit/gate/remote observation (approximately380–538). It freezes exact candidate/task/document identities, requires independent acceptance and tested-tree/original-parent commit, and brackets fresh remote readback with gates. Accurate remote_url/branch/commit is required. The helper observes rather than executing stage/commit/push. A trusted serialized controller and callbacks remain required; private JSON is not a tamper-resistant ledger against same-permission writers. These excerpts support the limited relationships stated in reading.md, not the paper's receiver transaction guarantees for this repo.

No complete-module security audit or absence-of-defects certification is implied. No new production defect was confirmed; no code repair is authorized by this review.

## Independent knowledge use and saved result provenance

Actually ran `python -m agent_runtime.knowledge --root knowledge search 'evidence authority action commit retry contract sufficiency' --limit 3` against the project's real file-backed corpus, snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18` (files-lexical-v1). Read each returned full `show` result and assumptions:

- math.betting-test-martingale v1, SHA `a082de859efe25ad7cef832d8c8433aaf0f72cd92399d6601c24eebe37cb5ca9`: rejected; conditional-mean/predictable betting theorem is not authority freshness, receiver atomicity, or this fixed paired-testing analysis.
- math.symmetry-quotient v1, SHA `b6f49f38838a976fdf42589d923d818119438b749049a6a69104449afabf2e57`: rejected; no proved action preserving feasibility/objective/transitions maps the permission-changing worlds into symmetric duplicates.
- ai.speculative-sampling-residual-exactness v1, SHA `3014215db96bf6ed7a00d522bf68663e58c4d1e98bdc2b88efe85ccd1a012331`: rejected; token proposal/target probability and residual correction assumptions have no mapping to commit authorization or effect identity.

Independent adopted knowledge_refs: `[]`. Relevantness/hashes do not certify applicability. This independent query differs from the producer's saved identity-word query; its two rejected segment-monoid/avian-pallium candidates and snapshot/hash were inspected and accurately summarized in the frozen record. No replacement corpus or theorem guarantee was invented.

Inspected the saved `.agent-runs/wtb-reading-0100/prior-result-search.json`: query2609.08472,326 scanned,0 hits,25 missing-record errors,status incomplete,partial false. Its hash matches inputs.json. This is a bounded no-hit with errors, not proof of no historical reading or empirical result. No empirical result was reused; no catalog or old tests were rerun.

## Seven checks, blockers and next owner

| Check | Outcome within this manual review | Reason |
|---|---|---|
| intent | pass | Same SYSTEM-99/Plan54 reading checkpoint, not a new optimization experiment or completed system batch. |
| guide | pass | Actual GUIDE.md is empty and hash-matched; read directory README and preserved the entire guide directory read-only. No invented guide authorization. |
| assumptions | pass | Scope, trusted state, mediation, receiver cooperation, packaging and missing full-bill assumptions are explicit. |
| prior_results | pass with retrieval limit | Saved no-hit/error provenance is preserved; no result acceptance inferred. |
| acceptance | pass for reading; runtime unknown | Primary-first comparison and selected code checks support this record; no trusted runtime receipt/public readback was produced here. |
| risk | pass within scope | No production/task edits, migrations, competing lists, tests or consumed-gate restart. |
| resources | unknown for full accounting | One assigned invocation, no retries; all-role token/cost and authenticated budget proof unavailable. |

Blocking issues for the frozen manual reading record: **none found**. Blocking limits for stronger conclusions: trusted real-host integration and ReviewSession authentication; complete model-input trace; real task quality; all-actor token/cost/full billing; receiver cooperation/authority coordination; broader concurrency/recovery/ownership guarantees; and ordinary public publication readback. These remain open, not silently waived by seven check labels.

Parent owns final publication/readback and any canonical TASK/Progress updates. Previous0002 partial plus0100 completion is one paper2609.08472v4 only. Count31→32 is eligible only after this accepted review **and** actual public readback; this file does not itself grant the count or claim readback. All old full-suite/PID/alias/role/Codex/model/backend/budget gates remain consumed or paused; no retry/reset/rebuild is permitted. System remains unfinished. Future implementation/measurement needs its own existing-authority-compatible versioned plan and independent validation, not this literature acceptance.
