# MEM-DISPATCH-17 公开证据可移植性补验与发布前复核

Decision: **approve / usable-with-scope**，保留 independent-review.md 的全部边界。

主执行者发现私有额外检查的根目录固定 parents[2] 不适合 `agent_doc/results/<run>/`。已原样保留执行过的脚本为 `independent_checks_original.py`（SHA256 `4c179ba0f798097ca9349491a57fd546638e18e079c5efe2a00fc7848869c483`），普通/-O原日志不重写。最终脚本只将根目录定位改为寻找含 `agent_runtime/task_manifest.py` 的祖先，不改测试逻辑；最终 SHA256 `b484e8bbadeeaf8119def23ef96ff7c5289c886e119e827945b11f53f53adbed`。

修订脚本已复制到 `agent_doc/results/memory-dispatch17-20261017/independent_checks.py`，从该公开路径实际串行执行普通与-O，各4项全部通过，见 `portability.log` / `portability-O.log`。原始运行证明私有路径结果；本次补验单独证明公开归档路径可运行，不用原日志替代新路径验证。全库回归已结束后才开始，未与主执行者测试重叠。

发布前核对生产 SHA256 仍为 `02cb0b66ddebeaba39b15257be1e179506bfa6ac54f06a1d1fa7ce88a57a95ed`，永久测试仍为 `b5b9c3fd2b084b8a3b25c0e4eafb1606a162255fd6c680277aacce7bfbf8bae8`。没有生产编辑。读了公开报告、任务追加 diff、guarded regression_runner.py、final-regression.json及完整回归短日志结尾：tests实际1253项、8skip、无失败；Reader实际3项通过，运行前后生产hash一致。该全库回归由主执行者执行，我做代码/原始日志复核，没有另跑同一全库。

报告正确区分确定性派发前阻断、最终check/action非原子、空refs兼容、未知读取成本、无模型KV/QA/TTFT收益及父任务开放。任务仅在Progress追加，与事实一致。可按当前限定可靠性修复继续发布；仍需主执行者fresh fetch、明确文件暂存、最新main并发核对、普通原子发布与远端SHA/文件实际读回。此批准不替代那些尚未发生的动作。
