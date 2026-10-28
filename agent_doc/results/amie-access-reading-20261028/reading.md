# AMIE access-state reading

2610.34977v1, Yuntong Hu et al., submitted2026-10-26T07:50:16UTC. Primary: https://arxiv.org/html/2610.34977v1

Read: main1–6; appendicesA–C/E–H, including their tables, proofs and captions. D/I, references/images/code/raw replication excluded.1405partial and1500completion are one body.

Method: teacher-mask distillation, per-ID suppression counts, bounded multiplicative weights; updates follow sealed current context. Keep does not reverse accumulated penalties. Fixed-pool rank monotonicity protects only an unchanged target, not future utility. State bounds concern penalty magnitude, not storage.

Experiments: five hosts/three benchmarks; count/frozen/trained, state/direction/reset/decay/depth/strength/observation controls. LoCoMo supplied fitting/selection; transfer uses fixed policies. Only selected aligned pairs have intervals. Count can damage useful evidence; label-assisted replay is not deployable policy.

Limits: unspecified Mem0/Memory-R2 evidence projection; expanded-pool no-op and acquisition-cost matching not established by disabled-state checks. GroupMem recurrence unmeasured. Policy latency has unmatched serving, unknown student GPU and excludes fitting/loading/retrieval/answering. Serialized state is not RAM. MemBench history retrieval is adapter-generated. No independent LoCoMo generalization or hardware-normalized/full-cost claim. No repository performance transfer.

## Repository applicability

采用/调整：未来对照须分别固定保留内容、原生候选池、当前上下文、更新顺序和跨查询访问状态；新状态的价值在后续查询评价，同时记录有用旧证据受损、未入池证据无法恢复、依赖/异议保留和完整流程成本。频率/被检索过不等于有害，不据此自动抑制更正或指南。

只读源码关系：KnowledgeStore搜索是可发现候选，context保留完整先决闭包、预算跳过显式partial，check_refs只验身份与已发布先决条件；不能把导航未命中当证据不存在或语义无效。MemoryLedger保留不可变修订和失效历史，basis_context保留候选/反对项及祖先。任何未来重排都不得绕过消费者必需引用、当前依据/授权和独立验收；本次没有实现访问状态。

暂缓：新增长期抑制计数、学习选择器、默认按曝光降权、删除旧记忆或agent_doc迁移。恢复条件为本库真实宿主和留出任务的更正/异议/依赖保留、实际完整输入、全角色成本与最终任务质量对照；不是新实验批准。仅阅读/源码复核，无生产修改、测试或实验模型/后端调用、性能结果；独立AI角色1次且全部角色费用未知。公开回读后同批可恢复精读26→27，旧额度不重置，SYSTEM99未完成；历史登记unknown，手工独审不是受信运行时认证。
