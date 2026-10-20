# SYSTEM-99 阶段 C 独立结果验收

日期：2026-10-20。Verifier：`/root/system99_plan_review`，与实现/日志生产者分离。

结论：**usable-with-scope**，无本范围阻断项。当前审核有效、整体done收到新可信event后，失效证据及依赖闭包持久为blocked/requires_reconciliation，不自动重放副作用。限本地CPU行为，不是正式host/provider、发布授权或SYSTEM-99结案。

## 固定实现和原件

基线 `68e883e986c97ffbfc96602e96baafef46880e4d`；Python3.12、本地CPU/临时SQLite。已读实际diff、tick/复核/恢复/事务、CLI与managed调用者、新六项及原兼容测试。

| 对象 | SHA-256 |
| --- | --- |
| 修前core.py（固定Git原字节） | `ebb82f1b5f2529f7ebf89ba64a2e61dc3938ef437b9ce9d20c7cb49dc677b158` |
| 修后core.py | `a0796fc805336f2044b94ccbd69ff1ce0e5706788d8defc9d35cfa3fd5e1f8ca` |
| tests/test_terminal_revalidation.py | `0e5a62242ef9600db8ee64bb5b35381d3a19062af199a524a684e7518cf55c21` |
| terminal-before-v3.log | `2d7a4f29c651264b8ad1cbddf3aa2be598b18cda290eb873a3deaf3b095e6222` |
| terminal-focused.log | `ad73b17aa48ce5a4e33d76243948cf6c97afd19965b030201e705f42fd2c069e` |
| terminal-full.log | `9ca46e68670bd74c248959b1c59e3e08d31762f8696d3c0412a60cc55824a2a4` |
| terminal-reader.log | `38c7aa2a8f61d5222cd8f630856507b82934968dbd8f2f45597cefd17291a624` |
| stage-c.md（本次读取版本） | `45c407d907c27c9ebaa86c552f1f8d07841eb6ad47a204b3275cf26dccb15651` |

日志原件位于 `.agent-runs/system99/`；哈希只绑定字节，不授信。

## 实现与兼容范围

固定Git AST对照仅Engine.tick改变；task_supervisor、scheduler及原runtime/双主/managed测试逐字节不变。新分支符合Version4：去重/取消后，事件登记、复核、终态转换与保存同事务，并在claim前返回。通用active失效语义、plan_review_after_effect、显式恢复权限不改；原evidence、attempts、dispatches、next_at、claim_cursor及失效reason保留。

## 实际独立执行

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_terminal_revalidation tests.test_task_runtime tests.test_plan_review_independent tests.test_task_runtime_review tests.test_managed_supervisor -v
Ran 83 tests in 23.457s — OK (skipped=1)

PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.605s — OK

PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
exit 0，无输出
```

83项＝新6＋runtime30＋双主31＋runtime-review7＋managed9：82通过、1真实tmux/socket skip。模拟marker/短期子进程由fixture清理，不证明真实tmux/SSH。原active failed/后继blocked、取消/lease/并发、缺认证/撤销、managed最终报告均保持原断言。

### 固定修前对照

独立加载Git原core到隔离内存模块，重跑5个API方法：**7个预期assertion failure、0 errors**；排除了会执行当前磁盘源码的CLI方法。生产者修前-v3为6方法/8失败，额外含旧CLI，原件保留。当前六项均独立通过，含真实CLI init/tick/status、文件篡改与Store/Engine重开。legacy仅限CLI合成fixture，不是生产降级。

### 超出作者六项的独立负控

1. **有效保护fixture**：CPUHost程序检查通过后，verify失效→持久blocked；重复event不再verify；重建Store/Engine及proof恢复不解除围栏。未授权reconcile拒绝，显式授权恢复done；actor=1、events=3、terminal审计=1且invalidated=['R1']。仅程序fixture，不是真实模型/生产回执。
2. **事务回滚**：非幂等actor完成后注入terminal审计异常，event和state一起回滚；恢复日志器后同event仅观察一次并blocked。evidence/attempts/dispatches/next_at/cursor均不变，actor=1。
3. **独立双根**：逆序五节点DAG两独立根同时失效，精确围栏两根/子节点/join，无关支线仍done。proof恢复仍blocked，按依赖显式恢复后done，非幂等actor=5。此为额外独立案例；作者root/right案例是同一祖先闭包，不混称多根。

## 原始数据核对与六项验收

逐条重数生产者全库：1372＝1364 ok＋8 skipped，96.927s；比上阶段新增6方法，不把子例当方法。focused74/5.855s、Reader3/1.588s原件相符。未独立重跑全库；7个绘图/PDF/字体依赖和1真实tmux skip未验，不算通过。

| 验收维度 | 判断 | 依据 |
| --- | --- | --- |
| implementation | pass | 实际diff/AST与调用者核对，只有tick终态分支改变；active/managed共用helper与权限不改。 |
| reference_boundary | pass | 固定Git旧Engine独立失败、新真实API/CLI通过；去重/取消/异常缺handler/逆拓扑闭包/双根/保护fixture与恢复负控。 |
| data_integrity | pass | 固定source/test/red/专项/全库日志哈希；事务失败不留下半状态，原证据/计数及旧失败保留。 |
| numerical_sanity | pass | 方法/子例/skip分母分别核算；83=82+1，1372=1364+8；事件/actor次数从SQLite与计数器核对。 |
| measurement_validity | not_applicable（性能部分） | 冻结方案允许无性能验收；本阶段只主张确定性状态/拒绝/不重放。测试运行时间不是性能改善证据。 |
| reproducibility | pass | 独立83项/Reader3/同步、旧Engine重放、当前保护/事务/双根额外复验一致，外部资源限制明确。 |

## 保留边界与后续

新可信tick才复核；重复event不复核，snapshot/status只是回读，停止的monitor不自动重arm。顶层审核先撤销再恢复仍未验；保护fixture不能覆盖该分支或证明真实host。

本次只新增本文，未改源/TASK/测试/guide或旧raw/manifest/审核。无外部模型、付费或持久部署；后续登记/查询漂移/真实消费者恢复/模型质量成本/跨机继续open，SYSTEM-99不结案。发布仍由主控按授权、最新远端和实际回读办理。
