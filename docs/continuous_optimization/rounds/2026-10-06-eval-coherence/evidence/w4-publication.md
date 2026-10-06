# T23 publication evidence helper

## Preregistered acceptance (2026-10-06, before implementation)

Baseline observation: `importlib.util.find_spec('agent_runtime.publication')` returned
`None`. TASK coverage exists, but no executable persisted publication state binds a
staged candidate to TASK ownership, independent acceptance, commit and remote readback.

Minimum acceptance, fixed before implementation:

1. Every staged changed/deleted/added file maps to existing stable root TASK IDs;
   missing/unknown mappings and unstaged/untracked candidate differences fail closed.
2. Persist the exact staged tree and SHA256 file bytes, TASK source and evidence
   hashes. Changed content, TASK, evidence or stale memory cannot advance state.
3. Explicit controller authorization binds this repository, remote URL and branch;
   independent controller acceptance must validate the specific candidate and
   evidence. Neither an allowlist nor a report's own `pass` is acceptance.
4. Reopen state across tested → committed → pushed → remote_verified. Commit must
   match the tested tree and original base. Push success requires actual fresh
   remote readback; failed push leaves committed work pending and resumable.
5. No staging, committing, pushing, network calls or credential reads by the helper.
   Tests use real temporary Git repositories and a local bare remote, and are
   program tests, not external-backend or model-effect tests.

Ownership: only `agent_runtime/publication.py`, `tests/test_publication.py`, and this
evidence note. Root controller owns root TASK updates and actual publication.

## Implementation and controller handoff

`PublicationLedger(root, state_path, authorize=..., accept=..., remote_reader=...)`
is a callable Python helper, not a scheduler, publisher or installed host adapter.
Its Git subprocesses only inspect local metadata. The bundled `local_remote_reader`
reads a local repository ref directly; it cannot contact a network or invoke a
credential helper. A real host must supply its own trusted remote observation API.

The root controller first refreshes the remote under existing authorization, finishes
the candidate and stages it. `freeze(file_task_refs, remote=..., branch=...,
authorization_reference=...)` requires every changed path (including additions,
deletions and mode changes) to map to existing root TASK IDs. It binds every staged
file's Git blob ID, mode and SHA256; the canonical full-tree manifest has its own
SHA256, available before commit. It rejects untracked and unstaged differences.
The state path must be outside the repository or under ignored, untracked
`.agent-runs/`; state cannot become part of its own candidate.

`mark_tested(evidence)` accepts records with absolute `path`, file `sha256`,
`candidate_sha256`, and `task_refs` (plus optional `memory_refs`). Evidence must
cover every changed requirement. The trusted controller's `accept(candidate,
evidence)` independently verifies the actual acceptance for this candidate. A
report containing `pass: true`, a matching hash or a list of permitted task names
cannot replace this verifier. Callback parameters are copies; callback-time changes
to candidate/evidence are rechecked. Evidence and memory validity are rechecked at
every later transition.

After the host makes the actual authorized commit, `observe_commit()` requires its
exact tree and sole parent to match the tested candidate and frozen base. The host
must still refresh before push, reconcile concurrent changes and rerun acceptance
on a new frozen candidate if the base or tree changes. This helper does not fetch,
pull, merge or supply permission to publish.

After the host's push, `observe_pushed()` invokes the trusted `remote_reader(scope)`
and requires the exact authorized URL, branch and tested commit. `verify_remote()`
requires another fresh readback. Thus `pushed` means publication was observed at
that remote ref, not that this helper ran or witnessed a transport command.
`record_push_failure(reason)` records failure while preserving `committed`, pending
publication and acceptance evidence; reopening the same ledger supports recovery.

`authorize(scope, action)` must check current explicit approval for the exact local
repository, remote URL, branch and authorization reference, including revocation.
Missing callbacks fail closed. These functions are trusted controller code, never
loaded from TASK, a plan or a report. `status()` is explicitly historical audit data,
not an independent current proof or authority: the local file is not tamper-proof
against its owner. A host must invoke the gated observation APIs before a new
publication claim. Saved fields cannot bypass current authorization, independent
acceptance, candidate checks or fresh remote readback in those APIs.

Boundaries: single controller serializes writes; no concurrent hostile filesystem
writer guarantee, signatures, credential management, live backend integration,
automatic task-meaning inference or implicit discovery of undeclared memory refs.
The bounded first implementation supports regular-file Git trees, rejecting
symlinks, submodules and merge commits rather than silently under-verifying them.
Repository content filters whose working bytes differ from indexed bytes require
an explicitly adapted observer; no filter execution is attempted here.

## Program validation

Command: `python -m unittest discover -s tests -p test_publication.py -v`.
Final targeted result: **26 passed, zero skipped**. Real temporary local Git and
bare repositories cover persistence across all four phases; independent execution
of a fixture Python program; missing TASK mapping and evidence coverage; stale
candidate/TASK/evidence/memory; authorization revocation, wrong URL/branch;
uncommitted/mismatched commits; absent and mismatched remote readback; a real failed
local push followed by recovery; remote movement before the second readback;
symlink/FIFO/unsafe state paths; verifier-time mutation; and unchanged index/HEAD/
remote during observer-only operations.

Independent review reproduced a genuine initial defect: local `refs/replace`
could make the tested tree appear attached to a different commit OID, allowing a
local remote to receive the untested original object while the ledger advanced.
The fix disables replacement objects and legacy grafts in every Git observation.
Two regression tests construct real commit objects and misleading replacement/
graft metadata, then require rejection. The independent review owns the retained
baseline probe and report; the initial defect is not counted as a passing result.

The first implementation run found a test-discovery issue: helper `tested()` was
counted as a test and returned a value. It was renamed `_tested`; the reported
final count excludes that helper. No product regression was hidden by that cleanup.
These are program tests only, not proof of external deployment, model quality,
actual main publication or completion of the remaining T21 gates. Full repository
regression, independent review and publication remain root-controller gates.
