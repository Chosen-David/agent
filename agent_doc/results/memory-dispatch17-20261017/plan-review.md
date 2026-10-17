# MEM-DISPATCH-17 独立计划审核

Decision: **approve，限计划 v1 的声明依赖派发前再校验修复**。

审核对象：`plan.md`；基线 `5a128d06cef7a985e52ff976c9ecb7d378f72457`，审核时 tracked 工作树干净。只读检查了 AGENTS、决策协议、项目文档治理、MEM-STORAGE-01 索引/详情、`task_manifest.py`、memory/knowledge gate 与既有专项测试；没有执行测试、修改生产代码或生成受管审核凭证。

源码支持该假设。`ReportingHandler.run` 在开头检查 memory/knowledge/results/reuse，然后执行真实 prior lookup、日志回调、候选审阅、deepcopy/保护计划分支以及 `context.current()`。到 `handler.run` 之前仅再次核查 documents，没有第二次 memory/knowledge gate。既有 memory 测试覆盖执行前、handler 内、验收后与 verify 内的修正，不覆盖这两个回调间隔。`check_task_memory` 的非空 refs 会读取实际账本；knowledge 的非空 refs 检查已发布内容和 prerequisites，足以构造明确旧引用失效。

建议最小实现：在 current 检查成功之后、handler 调用之前，增加独立 try 块调用现有 `check_task_memory` / `check_task_knowledge`，捕获与现有入口相同的 OSError/ValueError 并返回 actionable blocked。不删除原 gate、不替换报告/独立验收、不改 schema/缓存/权限。保持 current=False 原有阻塞路径。可顺手在该同一 final 块再调用现有 documents gate，以覆盖 current 回调后的文档变更，但这不是批准本次 memory/knowledge 修复的前提；如加入需新增对应回归。不要扩展为 transaction/lease/外部动作原子性改造。

必要验收细化：

- 真实 MemoryLedger.correct 在 prior lookup 与 current=True 回调中分别发生；回调真实执行且初始 refs 合法；断言 handler 调用次数为 0，而非仅 outcome blocked（旧实现可能在 handler 已执行后才阻塞）。
- 对 knowledge 用真实 corpus 内容变更/已发布引用失效，至少覆盖 lookup 之后的派发阻断；若 current 回调也测同样可行。不要把 mocked gate 抛错当作唯一复现。
- pending handler 适合观察调用，不让报告读取掩盖提前派发。保留正常 complete+verify 及空 memory/knowledge refs 的兼容路径；current=False 仍不运行 handler。
- 普通与 -O 使用 unittest 断言，保留修前确切失败，不提前改测试 oracle。独立数据审核须查真实源码/回调顺序/原始日志，完整回归与 Reader 串行执行。

资料查询有 partial/error，不能据此声明全历史无同类缺陷。父任务开放、候选16负结果保留、不声称可信 ReviewSession 或监控已安装，均与治理一致。本次增加读取开销可作为可靠性代价，不能写成性能提升；没有模型 KV/QA/TTFT 证据。

接受边界：这缩短并覆盖特定同步回调前后的陈旧引用窗口。最后校验与动作之间仍无原子锁定，不证明跨线程/跨进程 correction 与 action 无竞态，也不发现未声明的语义依赖。
