# 工具调用与有界搜索：3 篇全文阅读

日期：2026-10-06。去重检查：本轮开始的 `papers.json` 未记录以下三个 arXiv ID；不同版本不重复计数。仓库对照基线：`cb3e133ded7f2c878b3eddb10a0e7876fe6cac2b`。以下区分原文报告、工程推断与本库实测；本任务没有复现论文模型实验，也没有改源码。

## 原文范围与机制

| 论文/固定原文 | 问题、机制与关键证据 | 成立条件、成本与失败条件 | 本轮决定 |
|---|---|---|---|
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/html/2210.03629v3), v3, 2023-03-10 | §§2–4：模型根据外部观测更新计划，再选择行动；决策任务使用稀疏状态说明。PaLM-540B，Table 1：HotpotQA EM ReAct 27.4、CoT 29.4；FEVER 60.9、56.3。Table 2 人工分析200轨迹，错误检索与重复行动是失败来源。Table 3 ALFWorld 134游戏，ReAct平均57、六套提示最佳71；Table 4 WebShop 500指令，SR40.0 vs Act30.1。 | 提示/模型/环境限定；最佳提示与平均不可混用。21条CoT采样不是一次调用；示范受上下文长度约束。仅可读Wikipedia及模拟购物，并未验证真实交易或科研。附录A.3更正示例不是系统记忆纠错实验。 | 保留已有外部证据检查，不照搬思维链模板。候选P1待测；不能推断每个任务加更多反思都有收益。 |
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/html/2302.04761v1), v1, 2023-02-09 | §2：采样API→执行→按返回信息降低后续token损失筛选→微调GPT-J6.7B。Table 4 SVAMP29.4 vs禁用API6.3；Table 5 QA仍落后GPT-3。§5/Table 10有无关返回降低损失的反例。§7：不支持调用链、查询改写；调用成本未进入目标。 | 附录B：8×A10040GB、BF16、最多2k训练步；原宿主模型不开放这些权重训练接口。单输入最多一次API；next-token效用不是事实正确性或用户任务成功。MLQA有分布迁移退化，不能宣称全面优胜。 | 拒绝本轮训练迁移；只将“信息确有贡献才保留”的思想作为P2待测，不把PPL筛选替代独立验收。 |
| [Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models](https://arxiv.org/html/2310.04406v3), v3, 2024-06-06 | §4/附录A：MCTS选择/扩展/观测后估值/模拟/回传/失败反思；LM分数与self-consistency是搜索启发式。Table 4 GPT-4 HumanEval92.7，n=5、8轮、生成内部测试后择一交付。Table 8移除反思HotpotQA63→58、去LM估值→37。Table 9成功搜索token约173290。 | 环境可恢复是必要条件；真实外部动作不能仅靠重放文本撤销。WebShop只50任务，SR38 vs Reflexion35；分数75.9不等于全部硬约束满足。附录D.1深度6与C/main深度7表述不一致，D.2 GPT-3.5六内部测试与main四测试需源码核对，不默默统一。 | P3待测；拒绝默认所有任务MCTS、自评分验收和无限探索。本库预算/权限/独立验收优先。 |

## 实际阅读记录

- ReAct：全文主文§§1–6、A/B、C.1若干完整多跳例子、C.4代表任务及IM对照、D.1/D.2/D.3、E.1失败分析。原PDF实际查看pp.2、4–7、15（Figure1–3/5、Table1–2）；未逐页检查其余示范长表/参考文献。Figure3提示与微调结果方向不同，不能把训练效应写成Prompt增益。
- Toolformer：全文主文§§1–8（方法损失/全部任务/规模/过滤反例/局限）、A.1实现、A.2选读QA/检索/翻译/calendar提示、B训练、C评测、D日期构造。PDF实际查看pp.2、8–9（Figure2/4、Table7–9）；未逐字检查全部提示示例及参考文献。
- LATS：全文主文§§1–6、附录A伪代码、B局限、C消融、D全部环境；E.1接口提示代表例子。PDF实际查看pp.4–5、7–9（Figure2、Table4–10）；未完整阅读E–G所有长提示、未逐页全稿视觉检查。Table9成本仅成功轨迹口径，不能外推所有运行成本。
- 三份固定PDF下载用于图表核对，哈希记在JSON；不把版权全文或渲染图片提交本库。网页截图接口曾仅返回占位文本，最终用本地PDF渲染与`view_image`真正查看，上述页码均指原PDF一基页码。

## 与本库对照：组合而非追加三个Prompt

实际读取 `prompts/orchestrator.md`、`workflows/project_memory_workflow.md`、`workflows/supervised_continuation_workflow.md`、科研协调Skill入口及 `scripts/agent_eval_pipeline.py` 的dispatch/collection预算部分。本库已要求按当前任务渐进加载、外部证据绑定、候选记忆与已验收事实分离、旧意图失效传播、冻结评分与失败保留；因此重复添加“先推理再行动”没有明确收益。

工程推断：三篇的互补关系是**用观测发现信息缺口→必要时尝试不同工具/候选→只用独立证据采纳结果**。ReAct支持动态更新，Toolformer提示工具返回需有用途，LATS提示困难且可回滚时搜索。冲突点是Toolformer不支持链式/交互调用、LATS增加大量计算且用LM分数搜索；二者不能直接合成为全局自我训练或自动成功门禁。模型的可见状态摘要只记录“缺什么、已验证什么、下一项检查”，不索取私密思维链。

| 候选（均为推断，未实测） | 文件与预期收益 | 适配成本与最小判别实验 | 决定 |
|---|---|---|---|
| P1：无新证据重复调用检测 | `agent_runtime/task_supervisor.py`、`scripts/agent_eval_pipeline.py`；同一规范化输入+工具+观测hash重复且任务状态无变化时建议改查询或保存阻塞，降低空转 | 中：必须区分正常轮询/暂时失败/会变化的外部状态；冻结四类保留任务（空搜索、API瞬断、合法poll、新信息到达），同条件比较调用数/最终成功/硬约束；不得因重复直接将任务标done | 待测；现有预算已限制尝试，应先证明预算内仍有无效空转 |
| P2：交接证据按需读取并测效用 | `plugins/research-assistant/skills/research-assistant/SKILL.md`、`workflows/project_memory_workflow.md`；保留来源hash、约束、当前有效意图和最小观测，详情按索引读取，减少冗余 | 低到中：保留来源/纠错必须硬门禁，不能凭模型觉得“没用”丢弃；同模型同任务对照全量与索引，记录可观测上下文bytes/来源错误/硬约束漏失/任务成功，未观测tokens写未知 | 待测；渐进加载已有，优先测镜像或链路重复而不另造记忆系统 |
| P3：困难代码的有界候选探索 | `workflows/implementation_optimization_workflow.md`、`workflows/supervised_continuation_workflow.md`、`scripts/agent_eval_pipeline.py`；仅独立目录、真实反馈、预算内候选可恢复探索 | 中到高：可信环境回滚/实际成本/内部测试与hidden验收隔离；冻结同一总工具及时间预算，直修vs≤3候选，用未见功能测试评分，同时测延迟/正确改错；真实外发与付款禁止当树节点重放 | 待测；先TASK授权基线，探索权限不等于发布权限；不默认引入MCTS runtime |

本任务只形成研究候选，采用状态须由根执行者根据本轮实际基线/门禁更新；本文不声称本库科研准确性、图美观或调用效率已提升。
