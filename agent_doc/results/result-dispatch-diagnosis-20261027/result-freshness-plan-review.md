# RESULT-DISPATCH-FRESHNESS-01 independent plan review

Decision: **revise**. Source supports the original result-freshness finding, but the exact minimal insertion is not approved for production implementation. No tests were executed and no production, tests, task, guide, historical results, or CI files were edited by this review. The only write is this private review.

## Scope and authority

Read root AGENTS.md, project_document_workflow.md, relevant dual_main_workflow.md, current canonical TASK and SYSTEM-99 stable plan, the candidate plan, actual source/fixtures and CI. GUIDE.md is empty; guide README explicitly preserves the human-only directory and does not create project requirements. This is the assigned result-consumer branch of still-open SYSTEM-99, not a restart or acceptance of blocked fullsuite/PID/ALIAS/role/Codex/wire work. This review is an actual independent host child review, not an authenticated repository ReviewSession receipt.

## Source findings

`ReportingHandler.run` currently checks result and reuse at entry. It then does a real prior-result lookup, candidate review/protected-plan handling, and `context.current()`. Its final pre-handler try checks only memory, knowledge and documents. The pending handler runs before the existing post-action result/reuse checks. Therefore a raw-data byte change in lookup/current can pass entry validation, allow handler work, and only then cause blocked reconciliation. A blocked outcome alone does not prove prevention of work.

`check_task_results` calls `inspect_result` for each required result and any result_validation contract. `check_task_reuse` calls `ResultStore.decide_run`, which also calls current independent validation. These are not passive hash checks: `inspect_result` invokes the trusted verifier, validates the review, then re-snapshots that individual contract and binds review evidence. That catches mutation of that contract during its own verifier. It does not establish a shared snapshot for multiple contracts, reuse registry state, claim state, memory, knowledge and documents. Later callbacks can invalidate earlier checked dependencies.

The proposed new checks would run after the sole current() check. Actual `core.Context.current` tests cancellation, node token, doing status and `lease_until > clock()`. A trusted, read-only verifier can take long enough for the lease to expire; a trusted host callback can also revoke/cancel the claim while returning a valid result review. With the proposed ordering the handler then runs without observing that changed claim. This adds potentially substantial verifier work after the claim gate; calling the verifier trusted does not establish that it is instantaneous or claim-preserving. The plan acknowledges overhead, but does not specify or test this ordering consequence.

Simply moving the existing current() below the new checks is insufficient for the proposed acceptance: a current callback can then change raw bytes after the last result check. Repeating callback checks in another finite order cannot guarantee arbitrary mutually invalidating callbacks are all current. An atomicity disclaimer does not resolve a deterministic synchronous callback gap while claiming all callback-induced invalidations prevent dispatch.

## Required revision / implementation blocker

Version the plan before editing production. Specify which post-verification boundary is promised and the trusted callback assumptions, including claim expiration. Do not approve an unqualified “declared inputs checked after lookup/current and claim current before handler” claim from the two-call insertion alone.

A bounded design to assess in v2 is: independent result/reuse verification, a final claim-current check, then callback-free freshness checks of already validated result/reuse artifact and registry bindings plus the existing memory/knowledge/document checks before dispatch. Reuse existing proof/ref binding mechanisms where possible; first establish exactly which bindings cover manifest, validation plan, raw/code/input/config/output/environment bytes, review evidence, and registry record. Do not treat a stored pass flag or a new passive hash as independent acceptance. This needs source review and a versioned plan; it is an alternative to assess, not authorization to invent a cache/schema/snapshot subsystem. It remains non-atomic with an external action and does not promise an unexpired lease after arbitrary subsequent I/O. If this cannot stay within the authorized minimal repair, preserve the confirmed finding and stop that production branch rather than claim an incomplete fix.

## Exact proposed regression oracles

Use a dedicated `tests/test_result_dispatch_freshness.py` unless the main explicitly chooses to extend the existing freshness module. Keep actual ReportingHandler and a pending handler with a calls counter; never mock the gate to return acceptance. Use `test_result_validation.make_fixture` and `independent_verify`, with its actual bounded CPU execution and formula/data/code validation. For centralized reuse fixtures adapt the actual existing `test_result_store.ResultStoreTests` prefix/evidence rebinding pattern. Construct registry and selection with actual public ResultStore.register/result_context/decide_run; do not handwrite reusable acceptance.

1. required_result_refs × lookup/current boundaries: start valid, freeze refs, modify actual bound raw-data bytes in the real lookup wrapper or current callback returning True. Assert the mutation happened, handler calls == 0, outcome blocked, and reason identifies reconciliation. First preserve old-source failures with handler calls == 1, not merely differing reason text.
2. result_reuse × the same boundaries: actual valid selected registry result, then raw bytes change. Same zero-call/blocked oracles. Include a frozen registry-record change case without manufacturing acceptance.
3. Unchanged required refs and unchanged reuse selection each permit exactly one pending handler. Missing independent verifier blocks before work. current False keeps its original claim-block reason and zero calls. Empty result/reuse refs do not create result registry/memory stores; distinguish the wrapper's real retrieval behavior from gate-induced initialization.
4. Exercise cached lookup on a second invocation: do not rerun the cached lookup; current mutation must still block with zero additional handler calls.
5. **Ordering acceptance required in v2:** a result verifier independently validates correctly on its added pre-dispatch invocation, then advances a controllable clock past a real Context lease (or deterministically invalidates its token/cancel state). Handler calls must remain zero and claim blocking must be observed. Make the mutation occur after the earlier current check, so an entry-only test cannot pass accidentally. Separately preserve the current-callback raw-data mutation cases. A final source design that cannot pass both is not accepted for the broader claim.
6. If v2 supports more than one independently checked contract/reuse input, a later verifier invalidating an earlier bound input needs zero-call blocking, or explicit exclusion from the promised scope with rationale. Tests must not imply a shared transactional snapshot exists.

Relevant bounded existing modules are `tests/test_dispatch_freshness.py`, `tests/test_result_validation.py`, `tests/test_result_store.py`, `tests/test_result_reuse_acceptance.py`, and `tests/test_result_gate_acceptance.py`; `tests/test_result_store_fd.py` is relevant if result-record/passive artifact reads change. Use discovery with exact file patterns or PYTHONPATH=tests for these modules because the existing fixture imports use top-level test_result_validation/test_result_gate_acceptance. Do not interpret this list as authorization to rerun blocked full-suite work. Main owns bounded baseline/fixed execution and one fresh independent result review. Only after a production candidate is accepted add the chosen regression module to `.github/workflows/portable-install.yml` with the existing Ubuntu/Windows × Python 3.10/3.12 matrix unchanged.

## Prior evidence and seven review dimensions

The actual saved search is 293 scanned, partial true, 25 errors, five hits. Read the actual `agent_doc/results/memory-dispatch17-20261017/report.md` and `independent-review.md`: they support motivation and the pending-handler oracle for memory/knowledge, but do not validate this result-consumer branch, its new verifier ordering, present code, performance or current acceptance. Preserve their historical full-suite counts and failures as historical only.

- intent: pass for investigating this bounded result-consumer defect; no batch-complete claim.
- guide: pass; empty GUIDE and whole human-only guide directory remain untouched.
- assumptions: fail; verifier trust does not prove preservation of claim freshness or earlier result bindings.
- prior_results: pass for correct non-reuse of old acceptance and preservation of partial/error status.
- acceptance: fail pending v2 callback/claim ordering design and required zero-handler-call oracles.
- risk: fail for implementation approval until added verifier work after current() is resolved; retain non-atomic external-action and finite-fixture limitations.
- resources: pass for read-only audit; execution remains main-owned and bounded, without model overrides/providers, new service or performance/quality claims.

## Reviewed bytes

- `.agent-runs/context-coherence-0105/result-freshness-plan.md`: `e2ed8a0771f385e96b21b4e93d981f95caf73714004053d8e9a530d3901fc548`
- `agent_runtime/task_manifest.py`: `076a1c4458ad9a88c627721f37fabb1132cbddc6261bfc11be024bac0eba6012`
- `agent_runtime/result_validation.py`: `1def3a2265ff7b9ecd3878fa99e1b88742d231231ad0766bdb661266f7679169`
- `agent_runtime/result_store.py`: `5de45de97b97d8ef3ae75b3404e3c6166606829c997b9b27d67a44bd678d915d`
- `agent_runtime/core.py`: `a567a48f765aa0e14f5f60c63a601f3ecdf57f9d2b09157bbde9b4660dae8712`
- `tests/test_dispatch_freshness.py`: `620eb4fda1dec3385112d1f521ee2fad028b98ccfea17f342163281a8e23d33d`
- `tests/test_result_validation.py`: `d4689b3bd11f18603cb34f1f6cff939de58e472483c8f987afb038f11ec9c77a`
- `tests/test_result_store.py`: `3055f1aca440fd8401599dedbda967ba0472ee7ae5a25f214522be8338ded53d`
- `tests/test_result_reuse_acceptance.py`: `284db551902da570dca1b90a4adbd72ec2dfdd6cedfb1cd85e2420a54c3f28e8`
- `agent_doc/guide/GUIDE.md`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `agent_doc/guide/README.md`: `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`
- `.agent-runs/context-coherence-0105/prior-results.json`: `3130cd937c3904bad55ee1f171d7ef55ef304750415d63659d2ed97ccd718660`

## Diagnosis-only v2 direction (subsequent parent scope)

Decision for this bounded direction: **approve**. This supersedes no production decision: the naive production insertion remains revise/unapproved. Source locations for the conflict are task_manifest.py:374-375 (entry result checks), :390-425 (lookup/review), :426-427 (sole claim-current gate), :431-437 (memory/knowledge/documents then handler), and :439-440 (post-work result checks); result_validation.py:352 and :360-364 invoke the verifier then validate that individual snapshot/evidence; result_store.py:548 invokes independent inspection for reuse. Actual lease/cancel/token predicate is core.py:251-255.

Approved scope is one diagnosis execution using current unchanged production and actual make_fixture/independent_verify/ReportingHandler. Keep the diagnostic script outside tests/ discovery, for example `.agent-runs/context-coherence-0105/result-freshness-diagnosis.py`. Four isolated fixture cases: raw.json changes once during wrapped real lookup; raw.json changes once during current callback returning True; unchanged fixture permits one pending handler; current False blocks with zero calls and original claim reason. The two mutation cases assert expected zero calls, so current-source behavior is expected to produce two assertion failures with actual calls one. Do not mark these expected failures as a repaired/passing regression or suppress them with expectedFailure. Assert/record each mutation happened once and the post-action blocked reason, so setup failure cannot masquerade as the intended defect. Use fresh temporary directories per case and frozen contract hashes; do not update manifest hashes after mutation.

Record exact executed argv/cwd/interpreter and fixture/production hashes, one complete raw stdout/stderr log and exit code; preserve all failure text, not a summary-only pass flag. A single test process may execute the four cases; no retries, additional full-suite work, models/providers or production/test-discovery/CI modifications. Archiving immutable diagnosis script, log and scoped report is approved; prior evidence remains unchanged. Main owns execution and result collection. Independent code/raw-evidence audit is required; one separate independent replay is permissible only if later explicitly chosen/approved, and is not required by this plan approval. This reviewer has executed no diagnostic or test invocation.

The only prospective acceptance is confirmation or nonconfirmation of the two deterministic required_result_refs callback windows on current source, with unchanged/currentFalse controls. Reuse behavior, actual claim-expiry reproduction, any production fix, generalized correctness, model quality and performance remain unverified. A new architecture or host-contract resolution proposal remains unimplemented pending evidence and alignment. Preserve all prior unresolved gates and SYSTEM-99 open status. The diagnosis may fail to confirm its hypothesis; report that result honestly and do not retry to force confirmation.

## Exact v2/script pre-execution review

Plan v2 SHA256 `2552665c282f6622213870be39d87c9c3c06c87c4cbba8f54cb6db838ca013cc`; first script SHA256 `d0178e03bd86600cabf90e620c81bcb4693f5207a7278e172e47034165c454dc`. HEAD is `45a717e605e3be07ca4925db1bfbe8b5a123f061`; task_manifest.py and result_validation.py still match reviewed hashes.

Exact script decision: **revise before its one execution**, for two small evidence/setup repairs only. The four-case mechanism, independent initial inspection, actual pending handler, single newline byte mutation after actual lookup/current, and false/unchanged controls fit approved diagnosis scope. However tests/__init__.py is absent, so importing tests.test_result_validation depends on namespace-package resolution and can be shadowed by an installed regular tests package. Insert both explicit repository and repository/tests paths and import top-level test_result_validation, matching existing fixture consumers. Print/record actual outcome status/reason and handler call count before the failing assertion, so the unmodified full log proves post-action reconciliation rather than only an observed call-count mismatch. Neither repair changes production or broadens cases. Preserve this original script/hash and have the revised exact bytes approved before running once. No test or import probe was executed by this review.

## Revised exact script approval

**Approve the single diagnosis execution** of `diagnose_result_dispatch.py` SHA256 `dc68502124bc886b58126177b11165e95856d1bc5b689cd9150dd31dc0bdb68a`, bound to diagnosis-plan-v2.md SHA256 `2552665c282f6622213870be39d87c9c3c06c87c4cbba8f54cb6db838ca013cc` and unchanged HEAD `45a717e605e3be07ca4925db1bfbe8b5a123f061`. Re-read the full revised script: it fixes fixture import resolution, prints status/reason/calls before the zero-call assertion, asserts the post-action reconciliation reason for both mutation cases, and preserves both controls. The two mutation cases intentionally remain ordinary failing assertions if current-source handler calls are one. Scope is one outer-90-second invocation with explicit repository argument, complete raw log/exit/command and source hashes, no retry or production edits. No actual lease-expiry reproduction is approved or claimed; that concern remains static source analysis of core.Context.current. No tests executed by reviewer. Independent source/raw-evidence audit remains required after this one execution.
