# Evaluation-material coherence — in-progress batch

Batch: `2026-10-06-eval-coherence`. First wake-up: `2026-10-06-w1`.
Owner: root coordinator; paper readers own only their named research files.
Baseline: `e8ee3dca5dc8cd076fc031dd4510dabde214e046`, pulled ff-only and independently read through GitHub on 2026-10-06.
Status at w1: diagnosis/research only. At w2: unpublished runtime prototype and workflow reference updates; no release candidate or publication. See supervisor-followup.md and current checkpoint.json.

## Problem and scope fixed before changes

Primary queue item CO-020: the existing recorder freezes task/input/rubric bytes, but cannot establish that rubric facts agree with task inputs. In the preceding scaling batch, the frozen writer rubric demanded medium regression although actual producer output had medium parity and large regression. A main-AI rubric also contained an incorrect illustrative settlement; its alternative-correct-answer clause prevented an incorrect rejection, but the example itself remains wrong. The historical writer remains ungradable; neither historical rubric will be edited.

Related CO-016: repeated organization proposals omitted usable rollback. Keep pending; do not make a Skill change merely to combine this with scoring work. Shared bounded questioning is an applicable user requirement: check factual premises, consider a counterexample, run a discriminating check, retain corrections and correct-to-wrong counts. Do not add a long mandatory reflection procedure.

Current chain: `evals/* catalogs -> scripts/agent_eval_pipeline.py prepare -> isolated task/snapshot -> host receipts + actual artifacts -> independent rubric grading -> report`. `prepare_run` validates shape, exact case sets and immutable hashes; `validate_grade` checks independent actor and artifact bindings. Neither checks the factual truth of grading prose. Existing safeguards should remain.

Counterfactual: without an added factual-review boundary, both contradictory historical material and corrected material will prepare successfully and pass byte-integrity verification. That is preparation acceptance, not a model/task pass. The historical failures are already real model observations; this wake-up replays preparation only.

Hypothesis, not adoption: bind a small, explicit factual verification record to the exact task/input/rubric versions before dispatch. Numerical checks should compute from fixtures independently; semantic review should identify unsupported rubric facts. Avoid a natural-language keyword detector claiming general correctness. Prefer an extension of the existing prepare/record pipeline, not a second runner. Ten-paper synthesis will decide mechanism and whether the maintenance cost is justified.

## Preregistered decision criteria

Before any implementation changes, preserve the historical repro and exact source/input hashes. The targeted experiment must include both historical defects, independently constructed direction/parity/units variants, and valid equivalent answers. Development cases and final heldouts must be separately frozen; do not give grading answers to workers.

Minimum meaningful program improvement: reject both known contradictory factual contracts before any worker dispatch, accept their correct counterparts, and show zero false rejection of role-generic criteria or mathematically equivalent correct settlements in the declared suite. The mechanism must expose unsupported/unreviewed cases as such, rather than claim arbitrary prose verification. No stale verification may transfer to changed task/input/rubric hashes. Missing, malformed, duplicate, tampered and reviewer-equals-executor evidence must fail the proposed gate as applicable.

Non-regression: no mutation of old records; no scoring answers in worker snapshots; no drop in case denominator; ungradable is not semantic failure or wrong-to-correct recovery; no mock/preparation output labeled model execution; no new external runtime, paid services or private-data transfers. Existing pipeline tests must pass. All dynamic current roles and a relevant actual handoff must execute on a frozen final candidate before publication, with targeted research-write/main/routing cases in addition to smoke. Exact model identity/seed/cost currently unavailable; matching interface alone cannot establish fair model A/B.

Budget and stops: this wake-up performs baseline diagnosis plus at most two new full-paper readings and checkpointing; zero new task-worker dispatches and zero implementation/Skill changes. The complete batch retains ten-new-paper, synthesis, upstream source and final-candidate gates across wake-ups. Stop a probe on an unexpected mutation, ambiguous source, missing input or host restriction; preserve the failure and continue independent work. No release before all gates. Do not count an incomplete batch toward convergence.

## Continuation

Read `checkpoint.json` before resuming, refresh main without overwriting these uncommitted records, verify no active executor, and retain prior readings. Complete the remaining complementary papers and pinned upstream Skill/interface review. Choose the smallest supported preflight mechanism, freeze holdouts and refine its exact acceptance schema before implementing. CO-016 remains pending until an actual controlled organization test is justified.

The existing three-hour task was read back enabled with this user's revised batch/wake-up/candidate contract. Only the malformed opening repository link was normalized; schedule and timezone were unchanged. This is task configuration, not evidence of a deployed tmux supervisor. No other repository or user-project TASK was modified.


## w3 — actual conference architecture acceptance and research completion

User immediate T25 task executed on unchanged pinned baseline Skills: three diagrams passed18/18 frozen criteria; actual writer/reader handoff passed4/4, four pages viewed and isolated rebuild matched. Sources were real NIPS2017 Transformer, CVPR2016 ResNet and MICCAI2015 U-Net original architecture. Preparation isolation mistake and intra-attempt layout repairs retained; no unsupported first-shot or A/B improvement. See evidence/architecture/report.md and archived runs. No new Skill/runtime changes this wake.

Eight new original fulltext readings plus retained two complete10/10 research synthesis; source Skill and dependency review extended without re-downloading prior material. See research/synthesis.md for allten and explicit decisions. This completes T20 and scoped T25 only. Fullwriting T24, final-candidate all-role T21 and task/publication T23 remain open. Do not publish existing dirty prototype based on diagram acceptance; no convergence increment.

## w4 — implementation, full manuscripts, contemporary diagrams and final gates

This is the **same batch**, not a new completed round. Original baseline e8ee3dc was preserved. Concurrent knowledge and communication work was fetched and fast-forward integrated three times, through 03b83a533aa60f3bb6024979750df7719c062a53. No other work was overwritten. Latest source evaluation candidate is 263958510f78789e33dd29676d510a672900ce26; v2/v3 attempts remain immutable. Latest registry contains **15 roles**, not the original 14. TASK identity collisions were resolved by explicit COH-T19–COH-T27 names; prior frozen records retain their original IDs with a mapping.

### Adopted bounded program changes

- **CO-021:** pending observations consume explicit finite wait budgets rather than failed-attempt budgets; persisted round-robin scheduling services independent ready work; diagnosis facts and budget-blocked/cancel boundaries remain distinct. The original 11-test counterfactual failed; candidate passed. Later adversarial review added boundary corrections. This does not implement or prove autonomous runtime acceleration and is not a deployed server/tmux supervisor.
- **CO-020:** optional protected material review in the existing eval pipeline, verified before actual host dispatch and rechecked through collection/grading. Exact task/input/rubric and external independent-review bindings prevent stale or missing approval. Two known bad contracts reject and two valid counterparts accept; ten heldout coherence cases and identity/tamper controls retained. This is an integrity/independent-review boundary, **not a truth oracle**: root's own unsupported CNY rubric approval still led to an ungradable historical travel case, openly retained and corrected in a new run.
- **CO-022:** a publication observer binds every changed file to existing TASK IDs and exact staged bytes, independent acceptance, original parent and actual remote readback. It records tested/committed/pushed/remote_verified separately and preserves failed-push pending state. It does not stage/commit/push on its own. Initial 24 passing tests missed Git replacement/graft false-verification; independent adversarial review reproduced and fixed it, with 26 focused tests passing. Trusted controller and filesystem boundaries are explicit.

### Scientific writing and figures

Three complete CPU research working papers cover a systems study, algorithmic empirical study and a heldout negative/boundary study. They passed **24/24** independent scientific checks; root and independent readers inspected **19/19 physical PDF pages**. All six result CSVs were actually recomputed and matched. Input scientific brief, argument, evidence, negative findings and interpretation are separated from audit records. Private sample diagnosis stays private. Existing writing guidance passed these finite tasks; no redundant prompt or new role was added to manufacture an upgrade. The no-edit decision was frozen before the third heldout was revealed. This is not submission readiness or fair model-quality A/B. See [writing/report.md](evidence/writing/report.md).

Classic Transformer/ResNet/U-Net diagram tasks remain only baseline regressions: 3/3 diagrams,18/18 criteria and4/4 real writing/reading handoff. Contemporary tests add **AutoGaze (CVPR2026), DOUBT (ICML2026), DiTFuse (TPAMI2026)**, with publication status, CCF classification and exact original version/figure positions recorded. The CCF2026 directory PDF was actually read from a university mirror; direct CCF access returned405, so no successful direct official-directory fetch is claimed. First pass2/3; final3/3 after a missing DiTFuse legend was repaired. Semantic24/24 and visual12/12 remain separate. DOUBT maker was not shown the original figure; this does not exclude pretraining contact. DiTFuse uses the author arXiv version and explicitly retains the observed paper/code LoRA discrepancy rather than silently calling it the final journal PDF. See [modern diagram results](evidence/w4-modern-architecture/diagram-results.md).

Actual three accepted vector figures→writer→independent reader passed6/6. All six final pages were viewed; embedded vector streams match the accepted diagrams and an isolated rebuild matches rendered pixels/text. PDF metadata bytes differ on rebuild, disclosed. These three complex contemporary examples do not cover all CCF A venues/papers or reproduce source models' performance. Future venue/topology rotation is retained. See [handoff results](evidence/w4-modern-architecture/handoff-results.md).

### Five evidence layers and remaining gates

| Layer | Observed result / boundary |
|---|---|
| Program tests | Latest integrated source:472 total,464 passed,8 skipped; reader3/3. Seven skipped checks require a specific Chinese font environment, one requires opt-in tmux Unix socket integration. Separate actual scientific PDFs were rendered/viewed. |
| Actual role tasks | Dynamic15-role applicable final matrix accepted15/15 plus five main/handoff cases; two roles required explicit feedback-assisted repair, and150 artifact hashes were rechecked against final dependencies. Historical v2:16/19 cases,57/60 criteria (one semantic failure,two ungradable). v3:8/10 collected cases,29/31 criteria, with original12-case denominator and2 superseded unexecuted cases retained. |
| Real handoffs | Three full manuscripts and classic/contemporary figure-writer-reader chains completed. Latest-main knowledge producer→consumer executes actual copies, pinned retrieval, derivation and CPU tests. Actual mailbox review→repair→re-review is preregistered COH-T27; ACK alone cannot close the finding. |
| Old/new comparisons | Program counterfactuals demonstrate bounded correctness changes. Model interface/snapshot/seed and costs are unknown, grouped contexts share a filesystem; model-quality A/B remains inconclusive. Repairs are feedback-assisted recovery, not clean first-pass rates. |
| External integration | Actual host independent contexts/tool calls available; no live Claude/GPU/backend, target-server tmux deployment or persistent model-action daemon claimed. GitHub main publication/readback remains a separate gate. |

Repeated code-organization rollback omissions remain evidence for future CO-016 controlled guidance tests; they are not hidden by a successful repair. Historical reviewer mistakes and original failures remain immutable. Complete public evidence archives omit private/source-paper copies; modern archive source-text omissions are hash-indexed and prevent claiming a byte-complete replay of its original private trace.

**Publication is pending until final applicable role and actual communication gates are accepted, final content is frozen, remote main is refreshed, and ordinary push/readback completes.** The later publication receipt is authoritative. The existing task is now hourly by the user's later explicit change, remains enabled, and no duplicate scheduler was created. No convergence increment is justified.

### Final wake checkpoint: communication budget failure blocks release

All15 applicable roles and five main/handoff cases have accepted actual evidence. Source equality covers338 critical files against v5; prior-version runs are reused only with explicit unchanged dependency proof, not relabeled as new. The assistant budget grading contradiction was independently adjudicated against the frozen task: original v3 and v4 plans lacked a finite stopping budget and fail at the gate; original grades remain unchanged. A new explicit-feedback repair passed. V4 raw6/7 becomes effective5/7 under that adjudication, distinct from the final applicable matrix.

COH-T27 actual mailbox semantic review passes4/4, but delivery is incomplete:5 events,9 deliveries,7 receipts,2 pending for repair recipient seq4/5. The first transport envelope failed the completion contract and was corrected in separate metadata without rewriting outputs. A reviewer phase exceeded its declared180-second window; a distinct bounded receipt recovery retained that negative. Its reviewer and main-controller phases completed within their own fixed windows, but the repair recipient attempted two ACKs about33 seconds late. The guard refused both without calling the underlying mutation. Root independently read the actual guard logs and status rows. No reset, impersonated ACK, or retroactive budget extension is allowed. See evidence/root-communication-gate.json and controller communication summary.

This batch therefore **has not been committed or pushed**, and is not a completed round or effective convergence batch. Continue the same task with a latency diagnosis and separately preregistered, materially different bounded consumer recovery. Do not repeat unchanged paper, manuscript or diagram work. Keep the existing hourly task enabled. All semantic/program passes remain scoped evidence, not proof of complete protocol acceptance or model-quality gains.

## W5: actual compact receipt recovery closes the remaining protocol gate

Fresh Git fetch and GitHub read agreed main remained03b83a533aa60f3bb6024979750df7719c062a53; all prior workers were observed completed. The same unfinished batch retained its10/10 papers and all accepted role/manuscript/diagram evidence. A distinct preregistered one-attempt experiment kept the same actor, immutable messages and180-second deadline, and batched inbox/full SHA-verified reads into one worker tool turn followed by actor-authored ACKs in a second. The unchanged guard refused any late action; no old deadline or record was reset. Actual ACKs4/5 completed at16:03:50UTC,111.030seconds from the new exclusive start.

Root directly checked full read payloads, actor-authored receipts, invocation/finish times and actual mailbox status:5events,9deliveries,9receipts,0pending (8consumed,1historical bad-transport rejection). All22 pinned source/ref files and16 prior public files remain byte-identical. The original schema defect, reviewer overrun and recipient deadline failure remain historical negatives. Unknown model snapshot/context/scheduling means this recovery is not a fair causal speed/qualityA/B. No Skill/runtime change was added merely to claim the recovery. See evidence/root-w5-communication-gate.json and new W5archive.

Full declared acceptance is now supported; publication is still pending until the exact staged final content passes its ownership/acceptance binding, remote main is refreshed, and non-force main update plus remote SHA/content readback completes.

Publication preparation: W5 actually used3toolturns vs2planned, due to an extra read-only guard-interface inspection. Two functional read/ACK batches and all original180-second/actor/fullread/receipt gates passed; deviation retained, no causal speedclaim. GitHub rejected original full-writing-archive base64 request above its16MiB MCP limit. Published archive parts reconstruct the exact16,379,932-byte archive with original SHA and evidence; source/scientific validation remains unchanged. See evidence/writing/split-archive.md.

## Publication and completion

Main implementation/evidence commit [69cb8f22d751d8196ae80555f0127cf2e7976395](https://github.com/Chosen-David/agent/commit/69cb8f22d751d8196ae80555f0127cf2e7976395), exact tree b651fd40844c6baa7aea862dfc5dc96e465b354e, was independently read back via GitHub and fresh Git remote reads. Actual publication observer reached tested→committed→pushed→remote_verified;191changedfiles have stableTASKownership. Final closure only records this already verified publication and preserves all runtime/Skill/evidence bytes. Once that metadata-only update is read back, this same batch is complete. Continuous task remains enabled, convergencecount0.

Next batch: controlled CO-016 organization guidance/rollback heldouts and communication recipient-cost/quality experiments with independent findings, source/version rejection and finite budgets. Unknown model/token/cost telemetry and persistent Engine/tmux adapter remain explicit boundaries. Preserve negative cases rather than treat the successful feedback recovery as general improvement.
