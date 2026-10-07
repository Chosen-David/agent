# 执行与验收补充

这些步骤细化已有职责；不改变用户目标、权限或外部 API。按本次任务需要应用，不要求简单问答生成全套文件。

1. 错误修复先保存最小复现、预期行为、实际输出和调用路径，再形成单一根因假设；必要时补能在修复前失败的回归。连续尝试无效时回到数据流，不继续叠加猜测性补丁。

2. 优化先通过独立 reference 的正确性，固定工作负载和计时边界，保留基线与候选的原始样本。明确 speedup=baseline/candidate、延迟降幅=(baseline-candidate)/baseline；两者不能混写。零值/缺测不得产生无限加速。

3. 异步 GPU 需要同步或事件；没有 GPU 则只做 CPU/静态检查并说明未测。先验算微基准可影响的端到端上限，不能把局部提升直接写成系统收益。每轮只接受有测量和正确性证据的变更，最后再核对实际 diff。

复杂交接附实际输入版本、产物路径、已执行检查、限制与下一负责人。外部后端发现不等于可运行或已授权；没有后端时用当前工具完成有界任务。

实验脚本、资源准入、准确率并行或断点恢复任务按需读 [实验执行补充契约](experiment_execution_contract.md)。本 skill 的 `scripts/experiment.py` 提供 probe/plan 和 CPU 合成 run；GPU 仅只读探测与阻塞计划，不代表可运行真实实验。

可选 GPU／模型 runner 通过同契约的适配层接入：`scripts/gpu_adapter.py` 可生成默认阻塞的 scaffold、规划可用设备分片，并由可信宿主显式执行；真实 GPU 验证与 mock 分开，协作锁不代表独占。

涉及微小差值、性能/准确率提升或噪声疑点时，按 [共享测量证据契约](measurement_evidence_contract.md) 检查原始配对数据、独立单位、效应/区间与预设界限，再生成可验收的补实验任务。可调用同 skill 的 `scripts/measurement_review.py`；不能把门禁声明或合成通过当真实模型证据。

知识需求与交接按 [知识接入契约](knowledge_access_workflow.md) 执行；保留实际查询/前提核对证据及完整 knowledge_refs，无需求时注明原因。

测试/实验数据依赖按 [结果验证闭环](result_validation_workflow.md)：生产后 pending，独立 verify_experiment_result 完成代码和数据核验后才可 usable-with-scope；消费者传 required_result_refs 并依赖验证节点。失败/缺证据/版本变化先阻塞、修复、重测和复验，保留旧原始数据，不保证绝对无 bug。

项目新指令先按 [既有结果检索与复用](result_reuse_workflow.md) 查 `doc/results/` 的数据与当前验证，比较任务/代码/输入/配置/环境/指标单位后再安排新实验；复用保留独立代码/数据门禁，明确复现与新主张必做验收不能跳过。
