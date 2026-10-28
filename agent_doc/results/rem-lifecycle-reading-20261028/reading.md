# REM lifecycle reading

2610.27377v1, Xinyi Lisa Chen et al., submitted2026-10-19T22:59:56UTC. Primary: https://arxiv.org/html/2610.27377v1

Read: main1–7/Limitations, appendicesA–G/Algorithm1/Tables1–14/Figure1–3 captions. References/images/code/raw replication excluded.1202partial and1259completion count as one body.

Method: phased document at start; richer record after failed validation, withdrawn after one exposure. Embedding/top-five/LLM rerank; schema-discovery loop. Identifier references measure presence, not causal use; withdrawal leaves generated responses.

Experiments: 99coding tasks/300fixed trajectories; core policies three replicates, model sweep/most alternatives one. Retrieval baselines copied with differing settings; discovered pool loses33extractions. Main resolution contrast and policy ablations are nonsignificant; strong recipients regress. Four-characters-per-token estimates describe stored sizes; cache-weighted run usage is distinct, not complete extraction/reranking/build cost.

Preserve uncertainties: within-repository trajectory similarity/aging unmeasured; oracle missing2tasks; repeated-task/repository dependence; Table7 precision entries for document-only27/99 and REM27/96 do not reconcile with their printed percentages. Do not repair author data. Pooled significance is not independent-task replication. Learned schema improves retrieval only, not a demonstrated resolution comparison. No repository benefit follows.

## Repository applicability

采用/调整：评价经验复用时分别固定写入结构、检索、何时注入、持续多久，并检查最终真实任务结果、负迁移与完整生命周期实际成本。引用命中/标识符出现不代表模型理解或因果采用。摘要/旧方案只是候选依据，仍须当前源码和独立验收；本次不批准新实验。

本库已有MemoryLedger不可变修订与更正后代失效，basis_context保留声明的异议和依赖、只在真实当前上下文的宿主提示下省略；其payload计数不包含全部工具/输出。fresh/current用量解析只覆盖明确的单次无工具turn，不能冒充多工具编码任务或全部角色成本。这里仅核对源码，没有调用模型或重跑旧探针。

暂缓：自动提炼新共享经验、按一次验证失败强制注入、自动撤出证据或删旧账本。先需可观察实际宿主输入/缓存行为、失败类别、模型/仓库留出及完整成本质量对照；撤出上下文也不能删除指南、更正、异议或原始证据。维持唯一TASK、人类guide只读及原地维护。独立复核和公开回读后同批可恢复记录25→26；旧额度不重置，无生产修改、测试/模型或性能结果，SYSTEM99未完成；历史登记unknown，手工独审不冒充受信运行时认证。
