# INGEST-PUBLISH-01 independent result review

Verdict: **usable-with-scope** for the bounded Linux repair and frozen regressions. No blocking finding within the approved scope. Native Windows/macOS and hosted Linux CI remain pending; SYSTEM-99 remains unfinished. This is actual delegated offline code/raw review plus one independent execution, not a host-authenticated repository result-verifier proof or runtime deployment acceptance.

## Exact code and evidence reviewed

I compared the actual production diff against the complete previously reviewed source and proposal, inspected complete baseline and fixed logs/summaries, verified their raw log hashes, checked current frozen bindings, and executed exactly once from the project root:

`python .agent-runs/ingest-publish-1702/run_checks.py independent`

The frozen wrapper executed exactly the five approved commands: nine new publication methods, seven existing ingest-scope methods, five existing byte/read-boundary methods, fourteen existing index methods, then the reference synchronization check. I inspected all five complete independent logs and the returned summary, verified each log hash and all ten post-run source hashes. No other tests, diagnostic replay, backend/model probes or retry were run by me.

The actual source and existing Skill path both resolve to SHA-256 `5349e9c44f3be03d1a7dbc291562dfe98a71f1c532d302c49a8ffd5aa381e039`, identical to the approved proposal. The Skill path is an unchanged tracked mode-120000 symlink (`../../../../../agent_runtime/knowledge_ingest.py`), not an independently edited implementation. Its resolved bytes match automatically; the isolated copied-Skill execution and sync checks pass. This corrects any interpretation of the earlier term “mirror” as a second independently maintained file. No alias change is required.

Actual CI bytes equal the approved proposal SHA `e19d35fee3a6122c6ad1db3b870a3245a5fc2b6b5a7530277a954511b00dae44`. Installed safety tests equal the frozen SHA `5414b964d3892b83cc07424a4ce0583bb5d1cd0522cc6469a13f8864ecb641a6`; wrapper remains `70a2c39e0517db76632c91294e1810109ab1e55fe4b23e30b696d51411a1b5c4`. Existing tests, KnowledgeStore, index, project-doc guard and sync script match their plan bindings. All other 19 plan inputs remain exact after substituting the approved new source hash for the two resolved production-source paths.

## Actual outcomes

| Phase | New safety suite | Existing suites | Sync | Overall |
| --- | --- | --- | --- | --- |
| baseline | 9 methods: 4 failed, 3 explicitly skipped, 2 passed | 7 + 5 + 14 passed | pass | 35 discovered, 28 passed, 4 failed, 3 skipped |
| fixed | 9 passed, no skips | 7 + 5 + 14 passed | pass | 35 passed, no skips |
| independent | 9 passed, no skips | 7 + 5 + 14 passed | pass | 35 passed, no skips |

Baseline raw traces show two late-copy methods failed because KnowledgeError was not raised, the native existing-target method failed specifically for its empty-directory subcase, and the integrated after-final-guard claim method failed because no refusal occurred. Three new ABI/capability dispatch methods explicitly skipped because the baseline helper did not exist. These were intended failures, not setup errors. The dangling-target and complete-pair controls passed. Existing tests and sync passed before repair. Preserve this negative baseline intact.

Both fixed executions passed every new assertion, including the assertions reached only after successful refusal: the late mutation hook fired, the imported target stayed absent, private staging was cleaned, and the externally edited body remained present. The direct publisher collision checks preserve target device/inode identity and owner bytes while retaining the ready payload for empty/nonempty directories and files; dangling symlink identity/type and the ready directory remain. The integrated hook reaches the second destination guard and retains the claimed empty target. Success checks verify the exact three-file entry, candidate status and equality between returned reference and a fresh live store reference.

The POSIX ABI methods verify native symbol selection, argument/result declarations, success, EEXIST, ENOSYS and EPERM propagation, and absence of unsafe os.rename fallback. Missing-symbol and unsupported-platform cases fail closed; Windows dispatch propagates the mocked collision. The unmocked Linux normal/collision tests exercise the real libc/native operation in this environment. Mocked Darwin/Windows branches do not establish native behavior on those systems.

## Six validity criteria

1. **Intent/problem alignment: pass.** The retained baseline demonstrates the precise final-copy invalidation and empty-target ownership hazards. Moving the comparison beyond the final private copy makes the same frozen late hooks refuse; native no-replace publication makes the same ownership conditions refuse. The exact approved implementation was tested, rather than a substitute design.
2. **Code/input/raw correctness: pass.** The actual source diff contains only the approved imports/helper and final comparison/publication sequence changes. The final-copy hooks match candidate-folder to private `entry` copying; they do not intercept an earlier whole-corpus validation step. The integrated empty directory is ignored by record-based corpus snapshots, so its passing preservation test depends on publication refusing the occupied target. Actual verbose method outcomes, baseline exception traces, five exit codes per phase, frozen hashes and post-run checks agree. Correctness is not inferred from summary status alone.
3. **Statistics and uncertainty: pass for deterministic finite assertions.** These tests exercise defined boundaries by interposition and native filesystem calls. There is no random timing sample, performance comparison, speedup, failure-frequency estimate or evidence of universal concurrency safety. One fixed execution and one independent replay are corroboration, not a statistical reliability measurement.
4. **Comparison and context: pass with explicit baseline skips.** Baseline source SHA is `29a1b5e75232bfc2d5badf103f102ae045cec61ff24948abb626ab5412309c44`; fixed/independent source SHA is the approved `5349...` above. All four test modules and wrapper are unchanged between phases. All phases record Python 3.12.14 on Linux-6.18.55-x86_64-with-glibc2.39. Baseline ABI methods are inapplicable and explicitly skipped rather than claimed tested; fixed and independent have zero skips. Prior diagnostic evidence remains historical, with no old gate replay or automatic catalog trust upgrade.
5. **Resources and execution: pass.** The exclusive wrapper phase claims were consumed once each. Baseline elapsed 7.493246 seconds, fixed 8.402518 seconds, independent 8.151420 seconds, all below the 300-second phase limit; each command used the frozen remaining timeout capped at 90 seconds and none timed out. Independent summary records shared elapsed 74.846010 seconds; the post-log/hash review clock read was 82.053814 seconds from the original shared-start epoch, below 1200 seconds. No phase budget or exhausted older diagnostic/full-suite/PID/role/backend allowance was reset. Wall-clock accounting assumes no host clock jump and is not a hard real-time/process-tree guarantee.
6. **Applicability and remaining limits: pass within scope.** The evidence accepts a moving best-effort final live comparison plus native no-replace destination publication in this Linux environment. KnowledgeStore still reads multiple files without a transaction; arbitrary edits during the final read or after comparison, parent substitution and cleanup identity races remain open. Staging is created beside the corpus to attempt same-filesystem publication, but a corpus mount point can still make the sibling source cross-device; EXDEV is propagated and import fails rather than providing a global same-device guarantee. The inherited staging comment must not be quoted as proof that every possible root has atomic publication available. Missing native capability also deliberately fails closed. Crash durability, hostile filesystem actors, all corpus concurrency, model quality/cost and whole-round acceptance are untested.

## Bound result artifacts

| Artifact | SHA-256 |
| --- | --- |
| approved plan-v1.json | `b0a5335a53190f00c5f0d624b4e56897fddacd504c87318ce09cb8b8458fb049` |
| plan-review-v1.md | `8a87c552596e0fd53fb55be28bde209db757887d6f7750032907e2ee782ae002` |
| baseline-summary.json | `3886c2c4a4bbe9e764af939499447cfec14ba10defd333edc01086cd789f02ff` |
| fixed-summary.json | `41acdbf543ab221f19a51affc3e46ef782e3f1fec47870af5773e59ffbfbc582` |
| independent-summary.json | `79c92078d1c4e0dda31fba3549b8fc28a812c1608d2800423751623628aea861` |
| baseline safety log | `973b4b310bc8a207f77081523d972a565230669fc1daf74bf2e080919388d615` |
| fixed safety log | `50a04759c8782cd311c2148be1a383d4766422b3016ca3d4059f025b20c8be58` |
| independent safety log | `d358e605c4674e008f0f01c367f0ef1df2e9768ae932d196e4bca035c06916b7` |
| independent scope log | `4afe91a1b2b44f90b481e182d35da5f71c03cf70d88a69439cef79a3d902a65c` |
| independent read-boundary log | `50a7cacfd29c1c9276db2a0e1d7397814a6783e12c86572db77e185f9954888d` |
| independent index log | `508b4dc2066e26f4af8a467f55e77f9346433bb874b7cbb0b359ce313d48ec08` |
| each empty sync log | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

The five native jobs are a future publication check: four existing Linux/Windows Python combinations gaining these tests and one targeted macOS 3.12 job. Report their individual actual outcomes after the single authorized normal push; preserve any failure or explicit symlink privilege skip and do not rerun. This review supports the scoped checkpoint subject to root-owned publication checks, while retaining native coverage as pending and all prior SYSTEM-99 unresolved work.

## CI configuration qualification after Linux result review

Source inspection identifies a macOS fixture risk: tempfile follows TMPDIR, while KnowledgeStore rejects symlink ancestors. A default temporary path through `/var` can therefore fail before publication when `/var` resolves through `/private/var`. No current hosted runner path or CI failure was observed here. Before native dispatch, require the proposed CI-only v2 adjustment to give the new macOS job `TMPDIR: ${{ runner.temp }}`, relying on the runner's allocated work-temporary directory rather than a system temporary alias. This is a fixture-configuration precaution, not relaxed root validation or new platform evidence. Linux acceptance and all frozen v1 results remain valid; unchanged production/test/wrapper bytes require no additional local execution. The exact revised plan/CI must receive the remaining second source review before application.
