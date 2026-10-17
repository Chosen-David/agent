# MEM-DISPATCH-17：派发前再次核验记忆与知识引用

基线 main：`5a128d06cef7a985e52ff976c9ecb7d378f72457`。问题位置：`agent_runtime/task_manifest.py:241–293` 的 `ReportingHandler.run`。代码和输入哈希见 environment.json；最终结果与独立审核在同目录归档。

## 触发、根因与修复

入口先校验声明的 memory_refs / knowledge_refs，随后执行真实历史结果检索、候选审阅和宿主 `context.current()` 回调。原先回调之后只保留先前的引用校验结果，直接调用 handler；期间已提交的记忆修正或知识内容变化，可能在实际工作开始之后才被报告验收发现。

新增派发前 gate：在 current 为真之后、handler 之前，调用原有记忆和知识核验；失效或不可读时返回 blocked 与 reconciliation 原因，不启动 handler。保留原入口校验、claim gate、报告及独立验收。仅声明引用受保护，空引用兼容，不自动识别自然语言隐含依赖。

这覆盖两个可定位的同步回调间隙，**不保证最后校验与外部动作原子化**。记忆、知识及文档不是一个共同事务快照；并发写者仍可在最后校验后改变状态，宿主真实动作仍需自己的授权、幂等和恢复协议。

## 实际验证与边界

`tests/test_dispatch_freshness.py` 在临时目录使用真实 SQLite `correct` 与实际知识内容修改，分别在历史检索和 current 回调中使引用失效。handler 返回 pending，使测试能区分“根本未执行”与“执行后才阻塞”。修前7项中4项失败，均为 handler 调用次数 `1 != 0`；修后7项在普通及 `-O` 下均通过。另3项保留 current=False、未变更记忆的 complete+verify、空引用不创建账本的兼容行为。原始 before/after 日志保留。

本轮不测速。最终 gate 对非空引用增加读取和校验成本，未测其延迟、峰值内存或IO；不宣称模型KV、QA或完整TTFT改善。历史证据与已执行任务不自动撤销或重跑；需要检查依赖在检索/宿主回调期间变化的运行，尤其有外部作用的handler，不能因事后blocked就断言没有作用发生。

研究来源及限定阅读见 research.md：TRACE 的恢复准入启发复查回调前后的有效性，但本修复是现有显式引用契约的缺口修补，不是完整TRACE实现。父任务MEM-STORAGE-01仍开放。

## 独立复核与完整回归

实际独立新上下文核对计划、源码与原始日志，独立在隔离进程加载git基线重放同样4项失败；修后7项通过。另4项普通/-O检查覆盖知识正常complete+verify、缓存重复派发时重新校验、账本删除、current=False优先级，均通过。手工审核为限定usable-with-scope，不是已部署ReviewSession回执。

完整串行回归：tests运行1253项，8项可选依赖跳过，其余通过；Reader运行3项通过。final-regression.json绑定运行前后相同生产源码hash；日志保留。测试时长不作为性能数据。独立脚本公开归档路径适配另保留原版和补验记录，不改变业务测试逻辑。
