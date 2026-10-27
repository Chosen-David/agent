# Conflict-handling reading

2610.12360v1, Kaiser Sun et al., submitted2026-10-08T17:25:06UTC. Primary: https://arxiv.org/html/2610.12360v1

Read: main1–5/Limitations, appendicesA–E, Tables1–9 and Figure1–10 captions. References/images/author-code/raw replication excluded. Continues the uncounted0604 partial reading, one unique body only.

Method: controlled question-matched versus observational natural conflicts; four harnesses/five backbone configurations, fifty-iteration cap. Identify uses intermediate traces; Solve scores follow-up/termination, not correctness; Escalate conditions on incorrect conflict answers. Prompt intervention, judge-family agreement and small balanced human-label controls are reported.

Limits: backbone/harness confounding; answer mentions are not recognition; intervention significance compares conflict/control, not default/prompted. Empty denominators render zero. Human agreement does not certify real deployment.

Unresolved: main GPT-5 versus roster GPT-5.2; D.1 strictness conclusion reverses its reported negative-label counts; Table4 funnel counts are nonmonotone; Fig3 versus Table5 denominator scopes differ. Preserve unknown rather than repair author numbers.

## Repository applicability

采用/调整：既有评价边界继续分开“识别异议”“采取动作”“更正是否解决”“最终是否准确披露”；不把引用/ACK/工具调用或报告文件存在直接当模型已采纳、语义已验证。论文给出的指标可作未来诊断候选，尚不是本库实验批准/验收。

claim_graph已区分supported/candidate/rejected及satisfied/unsatisfied/unknown前提；basis_context保留异议和祖先，advice导航不授信，MaintenanceGate处理确认不代表模型实际保有，终态报告仍须当前验证。这里只读核对相应源码/契约，不声称真实调用质量或全链无缺陷。

暂缓：强制新增工具/“谦逊”提示、自动abstain接口、新全局聊天池/记忆架构；先需要本库真实任务、可观察最终回复及完整全角色成本/质量证据，避免以泛化保守措辞代替修复问题。维持MemoryLedger、定向交接、唯一TASK和人类guide只读；无生产修改、测试/模型/性能数据。旧耗尽门禁不重置，同一SYSTEM99继续未完成；独立复核及公开回读后才将23→24。
