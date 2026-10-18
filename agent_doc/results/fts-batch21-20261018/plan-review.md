# FTS-BATCH-21 独立计划审核

实际宿主调用：collaboration.spawn_agent，fresh context /root/fts21_plan_current；
不是原生 ReviewSession 认证回执。主控仅在该调用批准后修改实现。
批准对象：Plan v2，SHA256 39a08bb5ba837232706118dd9d20aed6150ea6e9a198bcc807b4e88a50bd013d，
及测量前明确的一对warmup、7对AB/BA、两组中位数比。该细节已写入Plan。

Verdict: APPROVE bounded manual implementation and measurement preparation.

Scope: Plan v2 plus the planner's premeasurement clarification: one untimed warm pair per scenario,
seven alternating AB/BA pairs, and ratio of medians. This is not a native ReviewSession receipt,
result acceptance, or publication approval.

| Check | Verdict | Basis |
| --- | --- | --- |
| intent | pass | Exact index-maintenance optimization; preserves public interface, retrieval semantics, schema, and knowledge content. Publication requires measured gains and validation. |
| guide | pass | GUIDE.md is empty; guide README supplies directory governance, not substantive project requirements. Neither may be modified. Root TASK.md is navigation, not a competing active index. |
| assumptions | pass | Existing code performs separate UNINDEXED-id deletes before insertions. Bounded IN deletion is plausible; keeping all deletions before original-order insertions is essential for rowid equivalence. Performance remains a hypothesis. |
| prior_results | pass | Search reports 229 scanned directories, partial coverage, and missing records. Retrieved corpus results do not establish build performance. Plan v2 correctly limits its negative-search claim. |
| acceptance | pass | Prespecified bulk improvements, small-case nonregression limits, logical-table/rowid equality, query equality, rollback/migration checks, six validation domains, and independent replay are suitable for the scoped claim. |
| risk | pass | Local reversible change; baseline retained, plugin mirrored, negatives preserved, no SGLang/TwoLevel changes. No new schema or engine migration introduced. |
| resources | pass | Existing CPU, 45-minute bound, at most two candidates. Budget exhaustion must leave unfinished checks pending—not relax acceptance or publish. No paid/external compute is authorized here. |

Scientific and fairness findings:

- The 12-paper matrix is real and contains distinct entries with explicit adoption/defer boundaries.
  It supports general engineering principles, not a theorem or empirical claim that this SQLite change
  is faster. Do not claim 12 newly read papers in this round.
- Freeze executable harness, source hashes, actual corpus hashes, exact five queries, timing policy,
  and validation criteria before the first measured sample.
- Every pair must start from equivalent baseline-built database bytes. Preserve all seven pairs,
  failures, warmup policy, and execution order.
- Report per-scenario samples and dispersion alongside medians. Seven pairs support a bounded local
  observation, not broad workload-general or statistical-significance claims.
- Synthetic 400/1600 documents must also record chunk counts/content sizes; document count alone does
  not characterize FTS work.
- The three English queries exercise synthetic content; 量纲 and the nonexistent query may be empty
  there. Use real-corpus results to substantiate nonempty multilingual retrieval equivalence.
- Useful boundaries: empty published corpus, one ID, 127/128/129 IDs, final short batch,
  mixed add/update/remove, published→unpublished, varying section counts, rollback after an earlier
  batch has deleted rows, migration rollback, highest-rowid behavior.
- Never interpolate IDs into SQL. Only generate placeholder counts; bind values.
- Keep original insertion order. Comparing only row counts or IDs is insufficient; include rowids,
  full contents, return values, metadata, search output.

Protected-workflow boundary: no evidence reviewed establishes an existing protected Engine/ManagedEngine
lineage for FTS-BATCH-21. Missing native ReviewSession authentication/tmux adapter blocks native managed
execution claims, not this bounded manual review. No manufactured host receipts/runtime certification.

Reviewer knowledge query: SQLite FTS incremental deletion batching transaction, limit3.
Snapshot 767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18.
DSU connectivity, convex projection, Fano message-budget cards did not support this optimization;
rejected as implementation justification.

Bindings:

- TASK: 6a11b8b042a88e31f15734384a9497ee6ea6afc5867acf41d6efefb7391bd987
- AGENTS: 694def45658b5b95b27913ee46173c7bb3575836d4585e5a08eceb7c93260e82
- GUIDE: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- guide README: f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261
- prior-current.json: 946edfad881a3b5d410f1539b68400b07316424ae138336efcaba7b85c8bf4d3
- memory-storage research.md: 58b505a0847363c5e79ce33c90537fe3058467794a9034eb2afe2b9f2bde6315
- both baseline index modules: 44d5bb19eaa1bb9f7527348d60eae2b3a13c2feb445d0bb35680949da4678058
- existing test_knowledge_index.py: 49f58cd38e0979313e9ccc15bf8f493eed72ca41c7b0c1c80256430d6e490bcd
- project_document_workflow: 40fb8145f6553526e589ab26c5922fe9de8883e68d878e7e0ca82ba2390b25fe
- dual_main_workflow: 639f19cf9de42d65935b3a42b8e9f6e8aa6e4a2145254ad59202642974eb9644
- result_validation_workflow: 3eea8448561134b51ee75469a99f30ec31b344b86d9789d98d236f1e787672d1
- task_supervision_workflow: 18ce8ca9f1f58db836d832ec2ab6816e1f7b9b1028d22726a18c06905e3534d8

Reviewer observed HEAD/origin main8cf78b709f49e4ecaa3030b57a341940c3f780a1.
Reviewer made no file edits, implementation or timing during plan review.
