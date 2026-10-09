# [MATH-59] 完成量、packetizer 与分块安全边界

Task-ID: MATH-59
Date: 2026-10-09

## Plan

授权持续知识建设，PROJECT_ROOT=agent；MATH-58 文档作为已发布前提资料，历史测量不复用。本轮 document-only candidate.completion-packetizer@1。只写 advice/results/TASK/learning_state 和生成快照，不修改 SGLang、生产、guide 或 Skill；预算 900 秒，最多两轮计划审核和两轮文档审核。先查真实历史结果，incomplete/scanned=53 不当完整无命中；知识入口按需 show PagedAttention，非 packetizer 定理来源。来源为 Le Boudec/Thiran §1.7.2、Theorem1.7.1 与 arXiv:2609.07883v1 §3.1–3.4。

模型：正工作长度 l_i≤L，累计边界 Q_n→∞，P(x)=max{Q_n≤x}；同序无丢弃 FIFO，packetized input A(t)∈{Q_n}，流体处理 D_f≤A 与完成输出 D_c=P(D_f)，空初始状态且边界完成立即可见。证明 0≤D_f−D_c<L，B_f≤B_c≤B_f+L，以及所有阈值 Q_n 上 D_c≥Q_n iff D_f≥Q_n，因此已 packetized A 下虚拟完成延迟不因末端 packetizer 增加。教材服务曲线弱化 [β−L]_+ 与 rate-latency T+L/R 只作保守曲线，不称延迟必然增加。多执行器、乱序完成、batch 向量、故障和 verifier 等待不默认满足该映射。

近期研究独立筛选：区分真实单调耗时的最大安全 chunk 与单边上包络的最大“可认证”chunk，安全不推出实际最大；显式检查 c=0 已不可行、负 slack、非单调上界、经验分位数非确定保证。手算正例、边界与反例；不执行新实验、符号/Lean/GPU/model，无实测 token 收益。公开开发题含无定理名、跨域和前提失败；未见模型题待未来冻结，next_topic 保留。不同 fresh-context 计划审核后写成稿，不同文档审核检查证明、源定位、所有例子及迁移前提；不冒充部署的 ReviewSession 或实验验收回执。审核通过后直接 CAS main，fresh fetch/远端树核对，收尾更新状态。

## Progress

- clean main 从 f24ce23 fast-forward 到 515efc5；读取 AGENTS、决策、角色、知识索引和状态，未见相同 active 登记。guide 仍只读。实际结果与知识检索保留。没有 GPU/真实 trace/监控后端，文档独立工作可继续。

- 独立新上下文计划审核 approve；完整七项检查存 plan_review.txt。成稿单独文档审核待验收，不使用部署运行时认证。

- git diff --check 无输出；generated-reference --check 失败于 main 已有 code-reading_execution.md stale，本轮未改该范围。文档审核发现准确耗时是最大性充分条件、不应写成必要条件，已纠正并重绑 manifest；完整审核反馈待 FINAL。

- 第二次实际文档 FINAL approve-with-document-scope，冻结 advice sha1bd362a11b0cc042372415442ee99b615540c8d3d5acb8555fa8b722face9485。一般证明、解析算例与源解释检查通过；无新实验与Agent效果结论。准备发布，远端核验后收尾。

- 文档发布4a1ec24b767ef1c181843a36d042708c1a24e305，远端fetch/ls-remote及tree694bd69e3a4c4596e236dbaa6b25e5ebe2dfa37f匹配。推送前发现并保留3bd1eb3硬件candidate，rebase后新鲜fetch+CAS；未强推，未修改其卡。收尾保留原next_topic。后续核查真实FIFO完成ID、verifier可见延迟和有效成本上包络；没有实际模型/GPU性能结论。
