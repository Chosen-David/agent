# SYSTEM-99 D/E 独立结果验收

2026-10-20，审查者`/root/system99_plan_review`。基线`9ab9becde217b74c50464155ab675dee9f422a60`。

**usable-with-scope，无本范围阻断项。** D只验历史引用登记，不接受旧结果复用；E接受审核撤销后的已完成作用围栏及显式恢复。本地CPU/程序契约，不是正式host认证、性能结论或SYSTEM-99结案。只新增本文，未改源/TASK/record或14旧文件。

## 精确绑定

| 对象 | SHA-256 |
| --- | --- |
| core.py | `1d4b4cb4565eb3afa49290129aa737de51679ea5c7f2993bf18f80a7e994f8b9` |
| test_completed_review_recovery.py | `0043ccf5606aad06ee18e72432864d00cc391e68062c2359b52053cde40b4875` |
| result-fd95/record.json | `74f8c5b361d8d95662bf61fdf5da7c9cf964b12597a8e472932ce8387f15e828` |
| system99/catalog_probe.py | `42564243ec13233abafc4786eccf2db59e6a071aebf9c500148595ede17a34a2` |
| review-restore-before-v3.log | `43366e5fe987b772bfc32021c8be9b08f0ef4cdbd55459d654b39edc72347a52` |
| de-focused.log | `7c2b417a9728607af5f9f884dca212a5f7c694527bb2ec6e889edc68e1e9676a` |
| de-full.log | `f869d829bee9ffc95d7a19b2990fbc0680825270d64ba170c6b18b68a06b94b7` |
| de-reader.log | `1005413ae4125cd5af3b5db4a40703adfb3726792cf862eea93c6e2de21c3c2e` |
| catalog-readback.json / catalog-readback-opt.json（相同） | `c4ce921ebc126bb30d8e2f79d5aa0deb85ec44a0ed5857b45038e3db7b61aad7` |

日志位于`.agent-runs/system99/`；哈希仅绑定实际字节，不授信。

## D：真实只读核验与负控

独立重算record的14 refs：151668 bytes、均为普通非链接文件，SHA匹配且逐字节等于`50c1ca1e`原提交。result_store.py与基线不变。目录只新增record；缺失私有full.log未补造，测量时间/完整执行树未伪造。

实际show保持historical-external-reference、contract=None、context={}、measured_at=None、unknown/proof=None。两种正式查询`RESULT-FD-95`/`result-fd95`各扫描252、partial=false、81错误，准确返回同一record一次、unknown/unchecked；登记前保存的查询为0命中且含该目录缺record错误。只补此目录，不把其余81错误冒称全是已完成结果损坏。

直接执行`decide_run(..., {}, verifier=spy)`：verify_delta/unknown、proof=None、automatic_skip_authorized=False、spy零调用。对**真实已登记目录**再次调用register_history，得到immutable/already registered拒绝；前后15文件SHA清单完全相等，无覆盖。坏SHA、大小写碰撞仅在自有临时fixture执行：不产生错误record、不覆盖原record；篡改临时原件后decide变rerun/stale。

独立重跑下列只读命令，普通/-O输出6367 bytes逐字节一致，SHA为上表readback值：

```text
python -B agent_doc/results/system99/catalog_probe.py --after
python -O -B agent_doc/results/system99/catalog_probe.py --after
```

## E：实际执行和兼容边界

已读core diff/调用者：只在顶层review拒绝事务内，把已done节点补为blocked/plan_review_after_effect/requires_reconciliation；未改通用_check_done、认证/预算、事件次序、worker或scheduler。新五项与原C/active/双主/managed断言保留。

```text
PYTHONPATH=tests PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_completed_review_recovery tests.test_terminal_revalidation tests.test_task_runtime tests.test_plan_review_independent tests.test_task_runtime_review tests.test_managed_supervisor tests.test_result_store -v
Ran 109 tests in 26.407s — OK (skipped=1)

PYTHONPATH=tests PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_reader tests.test_memory_check_reader -v
Ran 4 tests in 0.361s — OK

PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
exit 0
```

独立109项＝主控专项79＋managed9＋result-store21：108通过、1真实tmux/socket skip；自有短期子进程由fixture清理，不是持久服务/真实host。另从固定9ab旧core编译隔离内存模块重跑新五项：4预期assertion failure、0 errors，取消正控通过，与red-v3一致；v2的fixture错误不算生产缺陷。

额外独立负控均通过：

- **事务回滚**：已完成后审核撤销，注入plan_review_blocked日志异常；新围栏和state一起回滚。恢复日志器再次拒绝后围栏持久、证据/attempts/dispatches/next_at保留；恢复认证仍blocked，非幂等actor=1。
- **既有围栏**：混合三节点先因证据失效使父/子进入terminal_evidence，另一个节点仍done；再撤销审核，原两节点逐字段不变，另一个done补review围栏。恢复认证不自愈，依赖顺序显式reconcile后done，actor=3不重放。
- 新测试覆盖完成前缀/全完成、Store/Engine重建、独立未开始支线可继续而后继等待、权限/空证据拒绝及取消不可恢复。所有审核fixture是明确CPUHost测试替身，不是本项目生产回执。

## 数据核算与限制

主控全库短尾1377/100.097s OK skipped8；独立重数点进度为1369个`.`＋8个`s`＝1377，focused79/6.765s、Reader4/0.504s原件一致。未独立重跑全库；skip不算通过，不沿用前阶段Reader3。

六项验收：实现、参考边界、数据完整性、数值核算、可复现均pass；性能测量N/A（冻结范围无性能主张）。14旧字节、record、修前失败与本次代码分别绑定；登记不把旧Markdown通过升级为当前可信proof。

E补齐本次审核撤销恢复的程序路径，不认证snapshot/status、自动重arm、任意未声明作用或真实模型身份。D也不修复全库登记覆盖、旧受保护查询漂移或缺失私有证据；旧派发不能静默刷新搜索依据。真实消费者通信/意图更正恢复、模型质量/成本、tmux/跨机器仍未验，SYSTEM-99继续open。主控发布仍需最新远端及实际回读；本文不授予额外权限。
