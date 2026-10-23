# MEM-SCOPE-01：记忆复核检查全部scope

基线 `7e5c76835ef9a32194017316759318143f6a487f`；`agent_runtime/project_memory.py:600–601`。reconcile的newer_sibling_in_scope只从scope[0]取候选，尽管scope是无优先顺序的多个标签，且分组已覆盖全部标签。这使同一记录交换scope顺序就改变候选计数，也会漏掉仅共享后续scope的新条目。

两行修复：遍历全部scope，对较新条目收集ID集合，跨多个共享scope仅计一次。不改变时间比较、active筛选、输出字段、预算和只读契约；不把较新或共scope判作事实失效/科学矛盾，不自动correct/accept/删除。

## 复现与验证

新增tests/test_memory_reconcile_scopes.py使用临时真实SQLite：旧条目[first,shared]、新条目[shared]、另一个新条目[first,shared]、无关条目[other]；固定created_at以避免毫秒时间碰撞。预期唯一较新兄弟2，旧代码first在前计1、shared在前计2；修后两序均2。检查scope过滤结果以及所有条目读前读后一致。

```text
修前：Ran 1 test in 0.047s — FAILED(failures=1)
python -m unittest tests.test_memory_reconcile_scopes tests.test_project_memory tests.test_memory_context_closure tests.test_memory_index tests.test_handoff_basis
Ran 58 tests in 5.514s — OK
/root/.local/bin/python3.9 -m unittest [同上五模块]
Ran 58 tests in 5.440s — OK
python -O -m unittest tests.test_memory_reconcile_scopes
Ran 1 test in 0.031s — OK
```

环境Linux CPU，实际Python3.12.14／3.9.25；无GPU/模型/kernel。原日志reconcile-scope-{before,after,py39,optimized}-2100.log保留私有检查点。首版夹具用了默认candidate，原双failure已存fixture-failure日志；补evidence=verified才形成上述有效复现，未把夹具错误算生产缺陷。git diff --check通过。普通低风险只读诊断按轻量回归由主AI核对，未声称新增独立模型验收。

历史影响仅涉及多scope的reconcile候选提示，先前无提示不能推定这些条目无需复核；需重新运行当前诊断。单scope回归保持，Ledger correction/交接链回归通过，不代表模型实际采用更正或任务质量提升。reconcile仍可能跨连接观察并发更新，事务一致性尚待单独设计/验证；目录symlink复制边界亦保留检查点，未混入此补丁。无性能/总token主张，SYSTEM-99原协议冲突、真实后端/输入暴露/全部actor usage与质量缺口继续open，不计新轮完成。
