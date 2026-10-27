# MIGRATE-FENCE-01 independent static plan review

Decision: **approve** for the bounded local migration-consumer plan below. No blocking findings. This is a source/plan review before execution, not result acceptance, runtime authentication, deployment evidence or permission to migrate a real project.

## Frozen review object

- Project: `/workspace/scratch/6416f20dc59b/agent-run-1303`
- HEAD: `56cb758a0a0116fec98e8d0f6fdcc079f1f9db7a`
- Plan: `.agent-runs/migrate-fence-1058/plan.md`, SHA256 `ebae1564de81e8cf8e21411c85e2efc8ca13ba588bf697e1ea08849a1edd7fc1`
- New test: `tests/test_migrate_fence.py`, SHA256 `0af0c2e25bbb291659487f6fb79571243df2b18b829464e4b7f544f51dd1749c`
- Runner: `.agent-runs/migrate-fence-1058/run_checks.py`, SHA256 `0f23ed34b8d046ec620a32b883342682b6aaf16bf734eb30a7ff36af549e1b97`
- Current production: `agent_runtime/project_docs.py`, SHA256 `c461724efbbe58692e9940dcfca466ba5f40f2a4101ef249037e2358310e24d6`
- Current unique TASK index: SHA256 `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`
- Current SYSTEM-99 detail: SHA256 `956622a5ec39e2042de778ecb9c5578440fbd2188b27c4fa1976874ade6d3beb`, stable Plan Version48, stages AC/AD and recent Progress read.
- Human guide inventory: empty `agent_doc/guide/GUIDE.md` SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; directory README SHA256 `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`. Both remain protected.

The initial plan hash `6028e7d6baa59671b934ed2e3c3f7f02a8cec723fe3d5208903c4baae58a497c` is superseded for this decision. I reread the current plan after its pre-execution clarification that existing trailing-whitespace trimming accompanies CRLF normalization. No test, runner or production change accompanied that clarification.

## Seven-domain verdict

| Domain | Verdict | Reason |
| --- | --- | --- |
| intent | pass | The actual consumer is explicit legacy `migrate` API and portable project_docs CLI. The targeted discrepancy is its independently implemented dates/blocks scan after the newly aligned requirement parser. Repairing that existing function in place fits the scoped correctness objective; it does not authorize real repository/user migration or broader architecture work. |
| guide | pass | AGENTS and project-document, dual-main, result-reuse and result-validation workflows were read. GUIDE is empty; the full directory and its README remain human-only. Root alone owns source/test/TASK edits; this reviewer writes only this assigned private review. SYSTEM-99 remains unfinished; Version49/stageAE must preserve earlier stages and evidence. |
| assumptions | pass | Static source confirms `parse_requirements` uses physical lines plus the shared helper while migrate still uses unrestricted lstrip and a more permissive closer. These paths can disagree about admitted IDs and derived blocks/dates. That is a justified test hypothesis, not an empirical reproduction. The proposed helper call strips only CR/LF from the scan line and retains original raw lines for appended blocks, preserving EOF policy. |
| prior_results | pass | The frozen query records 303 scanned directories, partial=true, 25 read errors and five metadata hits. The actual advice-fence report was read as grammar precedent; its consumer, test hash and evidence do not establish migration correctness. Other hits remain metadata-only and are not reused. The previous native checkpoint distinguishes old failure from later four-job success and explicitly leaves this third migration loop a static candidate. No historical absence or reused acceptance is claimed. |
| acceptance | pass | Six new methods use literal expected ID/date/block tuples, exact raw archive/SHA, canonical snapshot coverage/index SHA, root pointer, guide emptiness, normal/default dates, EOF, idempotent byte inventory and refusal controls. Three separate temporary CLI projects test the actual portable entry under cp936/UTF8=0. One unchanged baseline/fixed pair plus one independent run and source/raw-data review precede any scoped conclusion; native matrix outcomes remain separate. |
| risk | pass | Reusing one existing fence transition avoids a third grammar while leaving parsing, rebasing, guards, conflict preflight, archive generation, source rechecks and pointer-last publication untouched. No real project migration, model, DB or monitor is requested. Full Markdown/HTML/container support and filesystem transaction guarantees are outside scope. Unexpected failure blocks dependent acceptance and must be preserved. |
| resources | pass | Runner names seven relevant modules, reserves one baseline/fixed/independent label each, and uses one 900-second elapsed budget beginning at baseline with a 180-second subprocess bound; new CLI subprocesses each have 15 seconds. Root must retain serial ownership and enforce stage ordering and no retries/resets. This separate consumer does not reopen old TASK-FENCE/native/full-suite or other exhausted budgets. No performance or paid-resource claim is planned. |

## Fixture and implementation review

I read the full new test and runner, `parse_requirements`, `physical_lines`, `_fence_transition`, `outside_fences`, all of `migrate`, its CLI main/output setup and `scripts/project_docs.py`. Literal fixture slices are specified from source rows rather than computed with the fence helper or migrate implementation. Both marker types, 0–3-space opening indentation, longer valid closers, invalid indentation/tail/type/length closers, backtick-info refusal, Unicode prefixes/tails, real versus example date/ID lines, unclosed EOF and all three physical newline conventions are covered within the stated scope.

The oracle matches existing derived-block semantics: migration performs `rstrip()` on the joined raw block, rebases relative links and replaces CRLF with LF. Fixture blocks have no meaningful trailing whitespace or relative links requiring rebasing. LF and CRLF expectations therefore use LF; CR-only fixture interiors deliberately retain CR. The new wording correctly avoids promising byte-exact derived blocks for arbitrary sources; byte-exactness belongs to the archived original. Source line endings are removed only when scanning the helper, never from raw archive bytes. The marker branch must still append original marker-shaped lines to a current block and continue even when an invalid opener leaves state unchanged.

Idempotence compares complete file byte inventories before/after a second migrate with a different supplied default date. Conflicting preexisting detail, duplicate ID and unidentified checkbox controls assert refusal and unchanged existing file bytes. These checks do not establish hostile concurrent filesystem atomicity, universal migration correctness or all directory metadata invariants.

The new test imports only project_docs and standard-library modules. Its CLI script imports project_docs directly; neither path imports or invokes the POSIX supervisor. The existing adjacent acceptance module does import ManagedEngine, but that is an existing Linux local-regression dependency, not a newly advertised Windows CLI capability. The plan adds only the new portable module to the existing Ubuntu/Windows × Python3.10/3.12 CI matrix. Prior Windows supervisor failures must remain visible; approval does not predict native job outcomes.

The runner is orchestration evidence, not an authority boundary: it does not itself authenticate reviewers, enforce label ordering beyond baseline-budget creation, or protect against an arbitrary same-permission writer. Root's stated serial lock/ownership and exact one-invocation rules supply that control. Result review must independently inspect actual executed source, input/reference cases, hashes, complete logs and environment, and then use the single remaining independent label under the same budget. Passing JSON or exit code alone is insufficient.

## Execution boundary

This review ran only read commands and hash/status inspection. No tests, probes, model calls, migration, runner invocation, native CI or production edits were executed. The foreign zip was neither opened nor modified. The only write is this review file. The parent must verify its current frozen inputs and source scope before baseline and after the proposed replacement. Any substantive change to plan/test/runner, acceptance scope, guide or stable task inputs requires versioned reconciliation; ordinary Progress updates do not retroactively alter this review object.

Approval is a real separately delegated static review of the exact supplied object. It does not assert that a runtime ReviewSession, trusted authentication callback, installed supervisor or publication adapter exists. Current runtime/result/publication gates and SYSTEM-99's real-host, quality, all-actor usage/cost and cross-store limitations remain open.
