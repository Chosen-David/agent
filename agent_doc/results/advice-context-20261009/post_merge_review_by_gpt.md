# Independent additive post-merge publication review

Publication verdict: **approve-with-scope** for the exact reviewed implementation and stable planning bytes. The original frozen experiment remains **usable-with-scope**; it is not rebound or reinterpreted. All six local review domains pass. No remaining blockers found.

Actual verifier `/root/advice_context_result_review`, independent from producer `root-advice-context-producer`; additive inspection in the same real child context, completed 2026-10-09T10:30:14.152171+00:00. Parent must authenticate this actual final child event. This local report/JSON is not a deployed runtime gate, self-authentication or evidence of a remote push. Approval permits the already authorized scoped publication preparation; actual CAS push and remote readback remain the parent's responsibility.

Scope: Local publication integration of frozen advice-context patch with incoming main 0498816 transactional communication ledger and ab6cc59 pending-inbox index; exact identity-only COMM task repairs, native document integrity and CPU regression compatibility. No new performance, model/token, deployment or remote-publication acceptance.

Reviewed source checkout HEAD `ba31494e40e84b586d5f0c2195aa17d5c1012aa9`, incorporating incoming main `ab6cc593e69b9361bac1b799a96e71e90287889a`. Receipt binds exact current implementation/tests/workflow/evidence bytes and normalized stable task-plan hashes. Mutable Progress and completion checkboxes are excluded from perpetual experiment acceptance. The task inventory signature binds ordered ID/title/detail/date fields, excluding checkbox state; the actual native snapshot observed **196 details, 2 guides, 7 advice** and exactly one CTX, COMM-PERF and COMM-INBOX entry. Any implementation, stable-plan, source inventory or bound-evidence change requires affected revalidation; ordinary truthful closure updates do not relabel old measurements.

## Incoming implementation and integration inspection

Read actual `bb5bf5b..0498816` and `0498816..ab6cc59` code/test/workflow deltas plus local advice-context changes. Incoming usage ledger creates/backfills counters and installs insert triggers inside its IMMEDIATE transaction, reads event/delivery-byte budget there, preserves idempotent retries and cumulative ACK semantics, and supports legacy append writers through triggers. Direct history edits/deletes/REPLACE or trigger removal remain unsupported. Independently replayed tests use UTF-8 body scans as their reference, including empty/two-run counts, retries, ACK/restart, precise event/byte caps, fan-out rollback, concurrent writers, first migration races and retry after failed migration.

Incoming pending-inbox change adds only an idempotent partial index `(recipient,seq) WHERE receipt IS NULL` in schema initialization. Inbox predicates, run isolation, seq ordering and limits remain unchanged. Its new test drops/recreates the index on populated history and checks ACK removal, other recipients, limits and cross-run isolation. Current communication.py and both communication test files match exact incoming `ab6cc59` blobs; local advice changes do not edit them. The project_docs implementation and original consumer paths remain at their already accepted hashes. The pending index and usage triggers target separate access/accounting paths; no overlap was found that weakens the advice/guide/stable-input gates.

This accepts compatibility and checked correctness boundaries, not either incoming communication benchmark's speedup. Upstream performance records remain historical; this review does not independently reproduce their timings or infer new gains.

## Two real native-inventory blockers, fixed without changing evidence

Passing fixture suites initially concealed a real current-project format blocker. Fresh `snapshot_project_docs(root)` after 0498816 rejected `COMM-PERF-20261009-01` because its incoming detail lacked Task-ID/Date. Its before SHA was `30b257ae7091a00c27f980f38c33dafaed58e572a702b47975fd4f0fb417694f`; fresh native snapshot became 195/2/7 only after the exact approved insertion. A later incoming ab6cc59 added COMM-INBOX-01 with the same missing metadata; final acceptance was held until its separately reviewed amendment and native success.

The parent reported actual independent approvals; locally inspected plan review files approve original amendment SHA `74347d38534f430f91ed197d0bcebbc2826512924bd61b67e16bf44ff789d987` and version 2 SHA `54806cead92cafd090caec02fc8603bd4d490dfde9f5fe8d8df6a72f5ccbc2bb`. They are local scope approvals, not model/experiment/publication receipts. I freshly read both before/current byte pairs and matched each before to its actual upstream Git blob. Each current detail equals exactly one replacement of the single `## Plan` marker by its matching `Task-ID`, `Date: 2026-10-09`, blank line and original `## Plan`. All other bytes, status, scientific narrative, original progress and historical publication claims remain unchanged. The canonical index date is 2026-10-09 for both.

```json
{
  "COMM-PERF-20261009-01": {
    "exact_metadata_only": true,
    "before_sha256": "30b257ae7091a00c27f980f38c33dafaed58e572a702b47975fd4f0fb417694f",
    "after_sha256": "ff6b9dc1fb8a2e5b868bc17b9a8a997d8f0835ccb42ef4b51638d825d9f1ec5f"
  },
  "COMM-INBOX-01": {
    "exact_metadata_only": true,
    "before_sha256": "2c7ab914954673bf943c1f472e7406a469d85b66aa0411e68ec88c2a22ce7701",
    "after_sha256": "f280f26b4a11bf057c7c6d398b32ec59a31d218da7d64f61f24d9e767a2761b7"
  }
}
```

Native final snapshot succeeds at 196/2/7; guide paths/content hashes equal startup inventory. CTX, COMM-PERF and COMM-INBOX IDs each appear once. Original four repairs remain at their accepted stable hashes. The new identity repairs are separate integration amendments; they do not silently refresh old frozen plans.

## Independent executions and exact log coverage

Fresh independent final-main command:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_communication_usage tests.test_communication tests.test_advice_context_scope tests.test_handoff_basis tests.test_project_docs_acceptance -v
Ran 83 tests in 10.468s

OK
```

This **83/83** subset includes the new pending-index case and both document/communication boundaries. Temporary log SHA-256 `a8f1039ba31d7d30f46dae3696aa50fe511c2e51898af6c5ba66ca9d70083003`. Earlier 0498816 combined subset was 82/82; an additional post-COMM-PERF document subset was 40/40. Fresh final native snapshot, original `_snapshot`/`_review`, generated-reference check and staged/worktree `git diff --check` passed. Mirror output was empty. No source changes were made by this reviewer.

Freshly inspected every verdict line in the completed parent final-main full log:

```text
python -m unittest discover -s tests -v
Ran 869 tests in 87.034s

OK (skipped=8)
```

**869 total = 861 ok + 8 skipped**, SHA-256 `9e6a78f1210d97189ab50a605975732ef1a9a02f3b5def6bf86e11060f19ab75`. Parent's actual tool exit was 0. This final suite ran ab6cc59 communication code plus the advice patch; it began before identity-only COMM-INBOX insertion. Runtime and test bytes did not change during that suite; native final snapshot independently verifies the subsequent metadata bytes. Seven optional plotting/PDF/font cases and the opt-in real tmux/socket case remain unexercised. I inspected the full log and independently replayed the targeted subset; I do not claim a second independent full869 execution.

The prior `post-merge-tests.log` is **0498816-era historical regression evidence**, 868/860/8 in108.142s, not the final ab6cc59 suite. Original `full-tests.log` remains the initial frozen 859/851/8 log. These distinct denominators and revisions are preserved; none was overwritten as a later result. No original measurement script/raw/log/review/manifest bytes were edited.

## Frozen experiment remains historical and valid within its scope

Original manifest SHA `bb188636b0bc3f4ddf4811d77bc5b4793df8e3f2e85df42285a9676672502f48`, all **63** original binding hashes, original review SHA `1ea986fb1a697415cc985a5fb6bd5aaa76291d34991349916ba2ea2c76bddfa2` and original receipt SHA `fbd12937154313b18bdabf0c64d01c0afd5237388d7948ec88ba4f40b85fc26c` are unchanged. Actual `_snapshot` and original receipt `_review` still pass all six domains. New JSON uses a separate local `post-merge-publication-review/v1` schema; it does not expand the original experiment-contract scope or invoke `_review` to pretend the expanded integration is that original experiment.

The original repository-shape row describes **194** task details at measurement time. It does **not** describe either the 195-detail intermediate state or final 196-detail state. No replacement shape experiment was performed, and no new representation/performance improvement is asserted. Original synthetic and shape rows remain non-runnable object diagnostics; no tokenizer, model-quality, fees, latency, KV-cache, GPU or multi-machine effect was measured.

## Stable planning bindings and limits

Stable planning SHA-256 uses the same split_detail contract: normalize CRLF to LF, take bytes before the one `## Progress` boundary and hash UTF-8. Paths and hashes:

```json
{
  "agent_doc/task/task_details/COMM-PERF-20261009-01.md": "0595c121dc2cf1081f1434e74a58186df0d011b0c3a32b9b4f7d7153759dbc0d",
  "agent_doc/task/task_details/COMM-INBOX-01.md": "112dbf53643d17f362c3be64c72c0eb9e7452b678663d0ae0d48ccf2a0669571",
  "agent_doc/task/task_details/CTX-20261009-01.md": "a127840ab51c5ff03268fffa020c38a2caa9e4e84a1c8c950fa4c861d9005f54",
  "agent_doc/task/task_details/WRITE-EVIDENCE-20261009-01.md": "754b9ac2a0778ae2b185ce5b11ec836ab96ab4de9d1baf51ff2767fee1968248",
  "agent_doc/task/task_details/MATH-55.md": "49d486a16f6c79076b4c3569a14118808972c9e8e18c40d76fdf87f57979d5a5",
  "agent_doc/task/task_details/MATH-56.md": "8a516978a081c8448868f1169a57ac4c0b81a81af7c4eed4627efd7136de6983",
  "agent_doc/task/task_details/MATH-57.md": "4b3818b5a13af5d978dc75b29d4fd572df7ea3fbe63bb30bb09630f7a2262b14"
}
```

Current inventory signature (ordered ID/title/detail/date JSON with sorted keys, minimal separators and ensure_ascii=False): `b9690a4240755692febf71cb91dca6b44bf7b2c1871c0ba89c73dcc486188b6d`. Completion states and Progress may receive truthful closeout/publication updates; they are not incorporated into a revised claim about frozen data.

All six local domains pass: actual implementation/interaction inspection; reference/boundary migration and scoped-source tests; unchanged frozen hashes plus exact two upstream metadata transforms and native completeness; exact counts/units without token conversion; truthful separation of historical performance and current regression evidence; fresh targeted replay, final full-log inspection and mirror/native checks. Receipt binds this report and applicable files. Finite local CPU checks do not guarantee bug-free code or semantic advice quality. Actual deployment, real tmux, model/token/latency experiments and remote publication are outside this approval. The parent must still verify final intended commit/remote CAS and any new incoming conflict; this receipt cannot authorize or certify unknown future changes.
