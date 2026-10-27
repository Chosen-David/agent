# MANIFEST-SHAPE-01 independent result review

Decision: **ACCEPT — usable-with-scope for local offline correctness**. No blocking finding in reviewed local implementation or evidence. Frozen full acceptance remains pending the five native CI jobs and publication readback. This is independent source/data acceptance, not an authenticated ReviewSession/backend receipt or SYSTEM-99 completion.

## Bound implementation and actual execution

Reviewed final plan-v2 SHA256 `60d3565b35bde5bd5c4d8bf6a920695dbd284dfacd1747ce283d314ad5520bfa`, complete frozen draft and actual tests/test_setup_manifest.py (byte-identical SHA256 `8cd95ed58dfd09e95026248bbdd6e2094d7973ca2d2e02b1713f5864bbddf611`), actual setup.py SHA256 `266695381405f094c502658d17cdea7791d240cf9fa398db9f13a306064f0082`, source diff, complete fixture, runner, baseline/fixed/independent metadata and raw test records. Reviewed actual caller and strong preflight code, not only helper/report labels.

Independently invoked exactly once `python .agent-runs/manifest-shape-2259/run.py independent`. Its exact eight-module subprocess argv matches approved baseline/fixed argv, Python3.12.14/Linux, gateway/TMUX removed. Independent raw record contains all105 test methods and final OK, no failures/errors/skips. Start1793113644.1898973 and finish1793113656.7031138 precede original deadline1793114533.8707707; no timeout/retry. Metadata hashes remain unchanged. Timings are execution bookkeeping, not performance evidence.

| Phase | Actual evidence | Interpretation |
| --- | --- | --- |
| baseline | 105 methods,46 assertion failures,0 unittest errors/skips; exit1 | 36 mapping cases,6 invalid-inventory cases,4 nonobject cases fail. Legacy control and remaining existing methods pass. |
| fixed | 105 methods,OK,0 skips; exit0 | Producer runs the unchanged frozen acceptance against repaired source. |
| independent | 105 methods,OK,0 skips; exit0 | Separate verifier runs the same exact suite once against the same source/test hashes. |

Baseline failures are genuine malformed-metadata handling defects:36 child commands return0/configured where refusal was required;10 child commands return1 with embedded AttributeError/TypeError instead of controlled exit2. The embedded child traceback is asserted failure evidence, not a unittest harness error. Top-level null/list/int/string install dereferences .get; skill_copies null/int membership raises TypeError; files/links and some skill_copies malformed containers are ignored or silently replaced. Three invalid present inventories are silently replaced during ordinary/explicit-inventory reinstall. Baseline contains105 method records and46 complete failure sections; counts are subtest failures, not46 independent root causes. Old top-level check/doctor refusal and uninstall preflight already pass and are retained.

## Implementation and fixture assessment

The sole helper requires a manifest object, rejects present files/links/skill_copies unless dict, and validates any present model_inventory through existing validate_inventory. Four manifest loads immediately apply it. install refuses before previous.get, discovery or writes. Missing-file first install still uses {}; optional absent fields remain supported. check catches validation as existing ValueError, resets diagnostic manifest={} and returns needs_setup without persisting fallback. No ownership is inferred from fallback.

Uninstall still requires files/links dicts and string values and retains path/link/resource checks before its first removal. The updater still rereads actual metadata and enforces schema, checkout/project identity, ownership fingerprint syntax, selected safe paths and complete preflight before writes. Helper validation adds constraints; it removes none of these stronger guards. No migration, duplicate schema, repair write or alternate production copy was introduced.

The actual test has per-command malformed JSON restoration and fresh snapshot INSIDE each command subTest. Thus baseline unexpected success cannot repair the next case's manifest. All approved commands/cases/assertions are retained. Fixed/independent success means every covered refusal produces required exit/status/error framing without traceback, then compares complete target file bytes, directory entries and link text to that command's snapshot. Owned target canonicalization, separate cwd, strict UTF-8, -B and20sec child timeout remain. Explicit empty inventory initializes fixtures deterministically; gateway/TMUX removal prevents real provider/tmux actions.

Valid legacy control removes optional inventory/hash before reinstall; reinstall/check/doctor/uninstall pass, note bytes survive and manifest is removed. Existing legacy migration, inventory reset/routing, conflict, managed block, symlink, copy snapshot/resource, discovery cleanup and updater ownership regressions all pass among105 methods. This proves the stated lifecycle control and impacted regressions; it is not direct exhaustive testing of all absent-field combinations.

## Governance, CI and limits

Actual diff only adds shared validation/call sites and proposed native test steps; tests retain the frozen oracle. Actual workflow adds test_setup_manifest to existing Ubuntu/Windows×3.10/3.12 matrix and macOS3.12 step with step.env TMPDIR=${{ runner.temp }}. Existing matrix, permissions, pinned actions and other commands remain. These are static findings; native runs are not yet observed and cannot be reported passed. Publication remains main-owned, with fresh fetch/nonforce integration and remote exact-tree readback.

Intent/guide/assumptions/prior_results/acceptance/risk/resources remain consistent with final approved Version53/stageAI: human guide untouched, single TASK writer, prior recovery design constraints preserved, no old empirical count reused, two plan cycles and baseline/fixed/independent once each consumed. No old scripts, full-suite/backend/model phases were replayed. Authenticity, deep metadata semantics, live discovery refusal ordering, hostile filesystem races and multi-file transactionality remain outside acceptance. No native deployment, real model quality, performance/token/cost improvement, new paper credit or whole SYSTEM-99 completion is established.

Reviewer wrote only this review plus runner-owned independent artifacts. No production/tests/task/guide changes, extra tests/probes or git publication were performed.

## Raw evidence integrity

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| baseline.stdout | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| baseline.stderr | 529593 | `f774d811f885afe33b530942f22452b4634637af8ebaa4b1336cc79ca905dba6` |
| baseline.json | 1224 | `9d1a0ce628f9eb627cf2e76959f796e63cb6b9225db6b90af701ca8ba9e55551` |
| fixed.stdout | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| fixed.stderr | 16454 | `4e004cdfbe4eb50bb6404bdd7af9a33a0168456f1b9dc6792d561c4b6ec694a7` |
| fixed.json | 1220 | `950cb7b50371233597b8a956cb53bc107dab6e4c81f0db18bf83f30d29c76939` |
| independent.stdout | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| independent.stderr | 16454 | `c2202396aa856331999ee88c12f612aed2ea9c1f58844b55dd9eeb2c9295ad99` |
| independent.json | 1227 | `fc86678b10f6b2b742b3649ca80bbab32a561453336710289b6eda3a69478e79` |
