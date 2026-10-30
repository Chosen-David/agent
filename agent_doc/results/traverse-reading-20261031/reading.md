# Traverse 2609.37082v2：主动边界、最终段训练与本库适用边界

精确版本为HTML实际页眉的2609.37082v2，2026-09-30；显式版本URL与先前默认URL下载逐字节相同。实际阅读主文1–6及全部子节、参考文献、附录A–F/F.1.1–F.3、Tables1–6、Eq1–20、四图图注和Figure4可提取机制/匿名案例文字。图2/3的独立SVG另核，不把图注当像素审读。没有作者实验复现，也没有本库性能测量。

## 方法与训练：读到的机制

§2.1–2.3/Figure1/Eq1–2：同一策略先产生忠实于原问题的Rubric，再Answer检索，最后切换Verify角色，以问题、候选和rubric检查；失败携带未满足条件、旧答案与反馈回到Answer。此处作者称independent verification，但属于策略自验证，并非本库可信独立调用、固定用户验收或消费者授信。

Seal由模型选择触发与内容，m(k+1)依赖问题、当前历史、旧memory；下一上下文q⊕m(k+1)，不是保留全部原历史。每次工具返回附token/turn预算，Seal刷新段token预算但保留累计turn预算。F.2中只有next_step_plan/task_progress必填；knowledge_graph/nav/meta等可选，事实source_url也非必填。顶层additionalProperties=false不证明嵌套对象同样关闭或证据真实。Read默认只开放最近一次checkpoint ID，返回紧凑state，可选会话尾部10messages/8000chars、structured6000chars；字符界限不是token，尾部不保证更正/异议/依赖闭包。文中有知识图字段，不等于实体去重/真值认证或任意旧记忆检索。

§3.1/Eq3：知识图合成任务与强teacher轨迹，过滤非法调用、过早/答案已知后的Seal，对坏assistant回合mask0而保留其余轨迹；system/user/tool回合均不作目标token。坏回合仍可能存在于后继条件历史，不能说已删除所有污染。teacher身份、训练总数据量/过滤留存比例在已读正文未充分量化。

§3.2/Eq4–5：同终局reward广播给所有段，既混淆早期探索的信用，又使多Seal轨迹按段数过重。1/K加权只纠正总权重，不解决信用；最终段训练每轨迹只优化最后段、GRPO式组内z-score、GSPO序列平均log-ratio。上下文溢出成为失败末段可间接激励及时Seal，但并非对每次早期Seal/摘要内容直接监督，也非证明唯一稳定方案。§4.1：SFT覆盖三状态，RL仅Answer；35B-A3B，256K/512turn/temp1，96GPU中32优化/64异步rollout。BrowseComp额外允许耗尽后Discard-All，不能把所有恢复收益归给Seal。

附录C/Eq14–20：终局正确性外还有临近turn/context上限的线性罚、格式罚、虚构工具/同搜索重复/答案已知Seal的动作cap和并行工具bonus；turn罚最后5%，context预算按问题group共同抽样，Seal后同预算。答案已知Seal可被拒绝并留在当前段。效率cost=rounds+λcalls，在正确轨迹内排名，再给发并行调用的turn奖励；不是实测墙钟/账单或全部角色成本。参数λ/罚阈值、预算集合具体值和bonus转换没有全部数值公开，不能声称仅最终段这一个因素完成效果归因。

## 实验与消融：分母、负结果和成本

§4.2/Table1：本方法BC72.8（正文72.83）、BC-ZH70.7、xbench57.0、DSQA MacroF1 82.8、Wide ItemF1 72.1；base分别61.0/69.5/50.3/68.5/57.1。并非全榜领先：FORT的中文75.0/xbench57.2更高，多个更大通用/闭源模型优于它。跨系统backend、judge与训练配方不能由排行榜视为全部同条件。

Table2：GAIA61.81→80.26，金融38.36→58.06，Shopping VPR .666→.668、SoP .2245→.3576。F.3明确金融排除244时敏题，使用635中的391时稳题，非随机子样本；不得称全金融原集结果。购物有效响应率几乎不变；SoP不证明产品可买/用户最终满意或本库旅行/通用任务质量。

§4.3/Fig2–3：答案验证关闭，SFT BC185 Avg@3 60.4→最终段65.2；全段51.7，1/K57.8。Wide全段46.3/66.2、加权40.1/59.5、最终段49.7/71.1（Row/ItemF1）；SFT→RL正文+6/+7.9。全段后期Seal延迟/几乎零与context硬终止上升；加权约20step退化、25–30step Seal激增/提前与重复搜索。是当前训练动态与终局消融证据，不是理论证明所有骨干/任务都会collapse。没有单独Rubric、Verify、summary内容/Read、各辅助奖励、Discard-All和多种最佳阈值的完整正交消融；也未给出充分置信区间来作普遍非劣结论。

Table3主动Seal对90%阈值AutoCompaction：同主模型作summarizer/同格式，BC185 Avg@3 54.95→65.23、Pass@3 68.11→76.22、Maj@3 56.22→68.11。首次memory中位数仅在发生memory的轨迹内：217turn/231.4K→67turn/67.5K，不是所有轨迹token均值。全轨迹平均turn却112.2→217.7；更早压缩与更多探索同时发生，不能声称净节省上下文/成本/延迟。没有所有summarizer/Verify/搜索后台重试的总usage和费用，不能用首Seal token替代全链token。

附录D/Table5：BC185先固定随机排列，再按5次历史Bo1和4次Bo5全量成绩回溯选择最小K；185满足所见Bo1≤3pp/Bo5≤5pp。不是未来模型/新策略误差保证，也不是未选择独立holdout或185独立重复实验。Appendix B/Table4两个成功案例保留失败候选/冲突并重定向；Appendix E/Figure4三匿名正确恢复故事仅定性、无失败率分母或逐步因果对照，不可由成功案例证明普遍检测语义停滞。

附录A/Eq6–13：交集约束、以唯一子实体问题替换常量的链/分支扩展、可追溯模糊化、来源与结构过滤；实际唯一性只对KG邻居/同类型/agent候选集合近似验证，不是开放世界唯一证明。无检索直答去污染与K次agent难度过滤的具体K/阈值未充分量化，不能证明零泄漏。已读参考文献不抵算额外精读论文。

## 工具、评分和作者实现核对

F.1：search默认10结果/title/url/description/rank；link_summary按问题读单/多URL，可透明重试或reader+LLM回退。模型可见统一schema不证明backend成本相同，摘要还可能遗漏反证。F.3/Table6：BC/中文/GAIA/xbench用DeepSeek-V4-Flash答案等价；DSQA Gemini2.5Flash逐分量含额外答案FP；Wide GPT4.1表解析/归一化/主键语义对齐后ItemF1。展示的BC/中文完整prompt忽略格式差异，与本库接口格式/权限合规验收不同；GAIA/xbench及官方外部全部prompt正文未全部嵌入，不能称已读这些未展示prompt或独立审计judge原实现。

作者仓库固定ByteDance-BandAI/Traverse commit2517b6ad97ed69d954c5cb379db0a986d4450c42，tree8bfa353cf60bd82fe527a433e7f3663e0d30290e，2026-10-10。只读完整root README与commit元数据；未读/运行作者源码、训练栈、数据或第三方部署。README说明训练/权重与harness分离，搜索/page reader需用户后台，AutoGen称将发布8617对；launch示例MAX_VERIFY3、可独立Answer/Verify预算及trajectory重试/恢复。示例限制不自动认定论文所有实验使用同值；确切v2实验源码对应未认证。安装/endpoint配置文字不是当前宿主可用能力。许可仅记录README的Apache2声明，未复制实现。

## 与本库关系与取舍

采用评价方向：后续真实宿主实验把“保留反证/排除原因、下一行动、更正依赖”及终局任务质量与全部角色usage一起测；对语义停滞、窗口溢出、格式/工具重复分别归因。复用MemoryLedger/定向handoff/唯一TASK与现有按需加载，不另建聊天池/任务清单。

暂缓直接移植Seal、最新checkpoint-only检索、rubric自验收、最终段RL和自动重启策略。原因：本库没有本论文训练/搜索后台，同策略自验不满足独立授信；最近尾部可能丢更正/异议，现有声明依赖闭包不能被无来源字段替代；turn增加与完整成本未知。agent_doc架构/重大迁移仍需版本化有证据方案与对齐。本次仅阅读与适用性审查，无生产代码/接口/稳定Plan更改、模型任务或性能结论；旧失败/耗尽范围与SYSTEM99端到端缺口全部保留。
