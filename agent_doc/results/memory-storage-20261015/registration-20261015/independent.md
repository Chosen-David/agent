# 历史记忆结果登记：独立复核

2026-10-15；基线 `14cee3ac6470a5c1bd327756ed500a2e142d907e`。独立执行上下文 `query_layout_review`；主执行者独占其他文件，本审查仅写本目录下的 independent.md / independent.json。采用既有 ResultStore API，无源码或旧证据修改。

结论：**usable-with-scope**，限于登记、可发现性和不越权复用的维护验证；不是重新验收旧性能或模型 KV 能力。

## 实际执行

1. 读取 `ResultStore.register_history/search/decide_run` 及既有测试；独立执行 `python -m unittest discover -s tests -p test_result_store.py -q`，21 项通过（0.927s）。
2. 核对新 record 的八项引用：manifest、raw-accepted、independent-raw、independent-review、report、research、measure、negative-v1。全部实际 SHA256 与引用一致，也逐项与基线 Git blob 一致。没有移动、覆盖或重新计算历史测量。
3. record SHA256=`880b5a21b87845b42f39eca0b924e1ee664b6d0400a3cce9300969c14e981b3d`。origin 为 historical-external-reference；contract=null；validation_at_registration 为 unknown/proof=null；measured_at=null。代码版本是旧结果发布版本，不假装当前部署/当前验收。
4. 读取主执行者保留的 before/after 原始查询，再独立运行相同三条查询，返回结构逐项等于保存的 after。limit=5/max_scan=200，三次均 scanned=200/partial=true。`MemoryLedger SQLite retrieval` 与精确 run ID 从无该候选变为 rank 1；命中仍为 stored_validation=unknown/applicability=unchecked。`memory scope retrieval` 在 top 5 仍无目标，负结果未隐藏。每次 errors 62→61，唯一消失的 error run ID 是本次补登记目标；未宣称其他缺失登记已解决或已搜全库。
5. 实际 `decide_run` 在空 context、record 自身部分 context 下均为 verify_delta/unknown/proof=null，automatic_skip_authorized=false；explicit_reproduction、new_claim 各自强制 rerun。
6. 在独立临时副本中，重复 register_history 被 immutable 守卫拒绝且原 record 字节不变；仅为副本 raw-accepted 追加换行后，decide_run 为 rerun/stale，不自动授权跳过。原仓库旧证据未变。

## 限制及发布边界

这是手动宿主历史引用登记，不伪造 ReviewSession、受管实验契约或原生通过证明。旧报告里的 scoped 独立审查仍是历史材料，不因索引出现获得当前科学验收。八项引用及其中 manifest 可供后续比对；字段未知保持未知，不补编精确测量完成时间或模型配置。

没有本轮新性能、问答质量、token 或 KV 推理结果；没有新增论文阅读数量声明。宽词查询的 lexical 排名问题仍存在，需要另作公平检索实验，不能把本次两条定向发现改善泛化为检索 recall 全面提升。下一步 scope-hydration 候选未实施，不列为完成。

本审查证据冻结后由主执行者负责核对远端、只暂存明确文件并发布；本文件不声称已经推送。
