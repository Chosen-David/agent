# MEM-DISPATCH-17 独立结果审核

Decision: **usable-with-scope**，限定为已声明 memory/knowledge 在 prior-result lookup 或 `current()` 回调期间失效时，阻止随后 handler 派发。最终全库回归与发布读回由主执行者继续；本审核不提前认证其结果。

审核绑定：base `5a128d06cef7a985e52ff976c9ecb7d378f72457`；plan v1 SHA256 `af5e904ddc3ec0feb69cdbc59317c6fe24f9ae33a1ce4a766bcd1e0b11231c77`；`agent_runtime/task_manifest.py` SHA256 `02cb0b66ddebeaba39b15257be1e179506bfa6ac54f06a1d1fa7ce88a57a95ed`；`tests/test_dispatch_freshness.py` SHA256 `b5b9c3fd2b084b8a3b25c0e4eafb1606a162255fd6c680277aacce7bfbf8bae8`。

实际实现仅在 `current()` 返回真后、原有 handler 调用前新增8行，复用原 memory/knowledge gate，OSError/ValueError 返回明确 pre-dispatch reconciliation blocked。原始 precheck、current=False、prior lookup、报告和验收调用保留。MemoryError/KnowledgeError 均属于既有 ValueError 契约。没有新缓存/权限/后端或并发锁。

已读生产者 before/after/after-O 短日志及全部7个测试源码。四个修前失败都精确为 `base.calls == 1`，断言期望0；不是仅用后续 blocked 冒充未执行。Memory 用真实 SQLite correction，knowledge 用实际 corpus 文件字节变更；lookup 包装先执行原检索，再失效，current 回调返回真。pending handler 避免报告验收掩盖派发错误。其余3项覆盖 claim取消、空refs、完整成功/verify。生产者修后普通/-O 各7项通过。

独立实际复验（与主执行者串行，无同时测试）：

- `independent-before-replay.log`：从 git show 读取基线 task_manifest.py，在新 Python 进程的原模块 namespace 编译执行，运行相同7项 permanent tests，得到同样4 fail/3 pass；四项仍全部 `1 != 0`。磁盘生产源码未回退/改写。
- `independent-replay.log`：当前补丁7项全通过。
- `independent_checks.py` 是独立额外4项，`independent-extra.log` / `independent-extra-O.log` 各4项全通过。覆盖未修改知识的 complete+verify 连续两次；相同 idempotency key 的 prior lookup 缓存命中后 current correction 仍在第二次阻断（lookup仅调用1次，handler总调用1次）；current 回调删除 SQLite 文件时阻断且 handler0次；current=False 即使同时 correction 仍返回原 claim 原因且 handler0次。

原始短日志：baseline `Ran 7 tests ... FAILED (failures=4)`；patched `Ran 7 tests ... OK`；extras普通与-O `Ran 4 tests ... OK`。测试运行时长仅为日志，不作为基准或加速指标。新增私有检查不加入生产测试目录，未修改生产文件。

边界：新增读可能增加开销，未测延迟/内存/模型质量/KV/TTFT。仅验证同步确定性失效窗口，不证明最后 check 与动作原子、跨进程无竞态、未声明依赖正确或语义使用。未扩展 documents 的 current 回调间隔校验；既有文档与结果门禁继续负责原范围。不把本次手工审核当可信受管 ReviewSession 回执，不宣布 MEM-STORAGE-01 完成。
