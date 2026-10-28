# USAGE-SHAPE-01 plan review v1

Decision: **revise**. One blocking finding. This is plan review 1 of the maximum 2 already reserved by the caller. No baseline, fixed or independent test command was executed; those stage counters remain 0. No network, model, CLI backend, old script, production, TASK or guide mutation occurred.

This is a manual independent review in a separate delegated context. It is not a native ReviewSession receipt, provider authentication, deployed verifier or authorization grant.

## Blocking finding B1: valid native preservation assertion observes the wrong object

Location: `tests/test_usage_shapes.py`, `UsageShapeTests.test_native_complete_outputs_and_scope_preserved`.

The method creates `before = copy.deepcopy(data)` but passes `json.loads(json.dumps(data))` directly into the parser and then compares `data` to `before`. The compared object was never supplied to the parser. Consequently this assertion always passes even if the parser mutates its actual input in the newly added zero-count, omitted-items or unrelated-event cases. The complete-output equality remains useful, but does not establish the separately required input-preservation property. Existing identity tests check real input preservation for their own fixtures and do not repair this specific oracle.

Required correction before baseline: retain the round-tripped object in a variable, deep-copy that same object, pass it to the parser and compare that object to its saved copy (preferably in `finally` so mutation is visible even on failure). Preserve the four method identities and full expected-output assertions. Update the frozen test SHA-256 and plan SHA-256 in a versioned plan; submit the second bounded plan review. Do not run baseline under v1 approval because v1 is not approved. This correction does not require a backend, broader suite, old probe, budget reset or production change.

Reverification: read the exact revised assertion and refreshed immutable bindings during review 2. Following approval, use only the already planned single baseline/fixed/independent commands and raw evidence. No extra execution is required to identify this oracle defect.

## Seven-domain verdict

| Domain | Verdict | Reason |
| --- | --- | --- |
| intent | pass | Controlled `ValueError` for malformed consumed JSON containers is a bounded reliability repair. It does not change token arithmetic or claim model/cost benefits. |
| guide | pass | Actual GUIDE is empty; README explicitly does not supply concrete requirements or permit later guide edits. Version54 stage AJ and existing human-only directory boundary align with the plan. SYSTEM-99 remains unfinished. |
| assumptions | pass | Native JSON object/array scope supports dict/list container validation; customized Python tuple items are explicitly excluded. Rejection of malformed earlier usage containers is an intentional behavior change, not a hidden claim of snapshot compatibility. Unknown unrelated methods and omitted optional terminal items must retain stated compatibility. |
| prior_results | pass | The pinned search note explicitly records partial scanning and 11 errors, unrelated lexical hits and no reuse of old pass labels. It does not assert comprehensive absence. Existing identity, counter/order/no-tool tests are directly relevant regression controls. |
| acceptance | fail | B1 makes one explicit preservation oracle ineffective. Other new malformed-container paths reject acceptance and non-ValueError exceptions; JSON round trips preserve the claimed JSON-only boundary. Complete dictionaries and genuine integer-zero controls avoid truthiness fallback. |
| risk | pass | Sole helper implementations in token_usage imported by turn_usage avoid duplicated validation. Validate event/params/turn/item/usage objects before consumed `.get`, and validate the entire terminal list and each member before iteration-based semantic checks. Preserve fresh equality versus current cumulative-history behavior, strict integer counters, order, identities and no-tool rejection. Do not replace malformed containers with defaults or hide earlier malformed usage behind a valid final snapshot. |
| resources | pass | Four frozen modules/four new method identities, one baseline/fixed/independent command each, 60 seconds per command, shared deadline 1793150566.9051683, maximum two reviews and one CI publication are finite. Current CI structure is four install matrix jobs plus one macOS job; add the new module once per job without altering other steps, permissions or actions. Pending CI remains pending. Earlier consumed budgets, stage failures and raw evidence persist across run IDs. |

No further blocking issue was identified by this source review. Fixed acceptance still requires independent source/raw-output/hash review and the planned offline execution; this review is not that acceptance. The exact full-output fixture checks remain scoped examples, not universal correctness proof. Native CI evidence must show all four new methods on all five jobs before claiming those platform results.

## Actual immutable inputs read

HEAD: `3f3f9f6810574541718936352a4ee23ece73d737`.

Stable SYSTEM-99 Plan Version54 is the exact byte prefix before `## Progress` (38029 bytes), SHA-256 `f6acab0acab813d56ea379700221747fbfd354262bd7223290527a208161bbee`.

| Path | Actual SHA-256 |
| --- | --- |
| `.agent-runs/usage-shape-0858/plan-v1.json` | `084817ee7409db234e6e4f0854f9287b8365578962eca0d5a4e61762c82c3d2b` |
| `AGENTS.md` | `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed` |
| `agent_doc/task/TASK.md` | `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f` |
| `agent_doc/guide/GUIDE.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `agent_doc/guide/README.md` | `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261` |
| `agent_runtime/token_usage.py` | `10d04dac588d04a915180b8f2b57b890a336e0aaa1865a0d9e34253eefa778e1` |
| `agent_runtime/turn_usage.py` | `6f32b515ec80f430698ec5304b80fb77dad229bed3cef227e363c81945c2adfc` |
| `tests/test_usage_shapes.py` | `c481588431cca0af6775a284698bc16ccd61b7bdac18e1c211e634b62dc7e1ae` |
| `tests/test_turn_usage.py` | `dd6456ab0bebaf8ae5c70ffa76ad7de997d3e39f5bbae9d0f220d20c56897955` |
| `tests/test_usage_identity.py` | `1935a2277f2f2e6dfef26af368bee7cc161843161d848581520af43337af16f9` |
| `tests/test_prompt_context.py` | `53e0e26fe1cd9fd21a99ef1b50e66ae07688227792c84e30c9ac633bfac47fcc` |
| `.github/workflows/portable-install.yml` | `98baf01d6a9f29a56557ed47404f91954593e99cee6f4f7e1190ca5de0862533` |
| `.agent-runs/usage-shape-0858/prior-search-note.json` | `1d6dac4a702efb0fa607b1c110f06b10810b070572ee003a495ab135c8a7f6cd` |

Relevant workflow reading: `workflows/dual_main_workflow.md`, `workflows/project_document_workflow.md`, `workflows/result_reuse_workflow.md`, `workflows/result_validation_workflow.md`, and `prompts/decision_review.md`. These distinguish bounded source regression from empirical model/performance claims and preserve independent acceptance, actual host permissions and guide ownership.
