# SYSTEM-99：从记忆问答到动作链验收

2026-10-26，基线 `d39f5ba1447a283daaa6ec0189cbdd11b114987e`。
本次仅正文精读和静态源码检查，没有测试/模型benchmark、生产修改或收益验收。

## MemoryArena

Zexue He 等，[MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session
Agentic Tasks](https://arxiv.org/html/2602.16313v2)，`2602.16313v2`，2026-09-17。
读到 HTML 正文 §§1–5、Tables 1–4/图注、Appendix C.2/C.3；其它附录未精读，
没有 PDF 页面或图像像素审查。版本正文标题省略 MemoryArena 前缀，ID/版本不变。

方法（§3）：701个任务、四类环境，分会话完成有依赖的购物、旅行、搜索和形式推理。
指标（§4.2）：成功SR、子任务进度PS与约束级软进度sPS分开；后两者不等于完整成功。
SR按环境定义，搜索/推理只看终题，不能据此证明此前每步动作都正确。
结果（§4/Table3）：旅行SR近零，局部约束仍可满足；外部记忆/RAG并非所有环境均有益。
诊断（C.3）：加golden结果与提炼workflow的近似oracle有帮助但未解决任务；表7深度L4为0.15，
不照抄附近“最终到零”的叙述。局限：任务集中、推理与记忆耦合、专家标注昂贵，
oracle不是真正充分状态；Table4/C.2为子任务/任务动作链延迟，不能当本库检索函数成本。
本文未复现作者运行。

## AMA-Bench

Yujie Zhao 等，[AMA-Bench: Evaluating Long-Horizon Memory for Agentic
Applications](https://arxiv.org/html/2602.22769v4)，`2602.22769v4`，2026-05-27。
读到 HTML 正文 §§1–7、Tables 1–7/图注、Appendix C/G；其它附录未精读，未做PDF视觉审查。

方法（§§3/5）：真实轨迹2496问、合成轨迹1200问；AMA-Agent用局部LLM抽象的因果图与工具检索，
不是对原始DOM/AST的无损规则解析。主评测（§6.1）是固定轨迹、独立离线QA，不更新后续问题记忆。
报告平均0.5722（Table5）；消融（Table7）去图约0.43、去工具约0.44。
§6.3另做TextWorld/Spider2动作链，六系统QA/E2E相关性不证明对所有任务的预测能力。
局限（§7）：episode内范围，跨任务终身学习未验；baseline沿用各自embedding默认值，
不把全部差值单独归因于图结构。C中judge验证样本300，不能证明所有排序不变；
G延迟缺少完整调用/硬件成本口径，不作为本库提速证据。本文未复现实验。

## 现有实现与采用决定

继续复用现有增量导航、MemoryLedger和定向交接，不新增聊天池或竞争任务清单。
只读检查：artifact_context的比较包包含完整base，restore核对独立源引用；
advice_context的显式H2视图保留leading_text并要求补读依赖；reference_context
恢复完整有序值后仍要求既有新鲜性/结果门禁。以上只证明接口意图，不是本次运行结果。
ReportingHandler在run/verify核对声明的文档、记忆、知识、结果及底层handler验收；
这些门禁不会自行证明自然语言理解、隐藏依赖发现或真实环境动作正确。

采用：把跨会话“记住→正确执行→环境反馈→下一步修正”作为后续质量验收的必要链路，
同时报告最终任务成功与局部进度。暂缓因果图改造；论文的LLM推断边不应自动升级为
本库已验证依赖或科学事实。先将本批现有纠错/恢复证据与真实宿主输入、动作验收对齐，
避免重复CPU微基准冒充全链收益；没有实际后端与完整输入/用量接口时相关结论仍blocked。

本次新增2篇正文，清理后可恢复的新记录本候选共7篇；旧55篇私有原件仍缺失，
十篇门槛与系统验收未完成。未确认本次须改的生产缺陷，不为提交而改实现。
旧PID/ALIAS/role/Codex门禁和预算不重置；主控/独审有实际AI推理，精确所有actor
provider tokens/cache/输出/费用未知，不记零；没有额外被评测Agent或后端benchmark调用。
