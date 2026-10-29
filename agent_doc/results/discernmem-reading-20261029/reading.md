# DiscernMem：规则修复与适用边界分开

## 来源与实际阅读
2610.36652v1，Yipeng Hao等，Remembering Is Not Enough: Refining Memories and Learning When to Use Them in Multi-Agent Systems。v1提交2026-10-27 05:12:46 UTC。原源：https://arxiv.org/abs/2610.36652v1 及 https://arxiv.org/html/2610.36652v1 。实际读正文§§1–5、Limitations/Ethical Considerations、附录A.1–A.3/B/C/D/E.1–E.7、Algorithm1、Tables1–4和Figures1–9图注；未看PDF/图像像素、未读作者代码或原始轨迹、未运行复现。1001部分和1059续读合计一篇；导航、参考书目和网页页脚不抵正文阅读。

## 方法与前提
固定骨干、角色及通信结构，当前任务先用过去记忆执行并评分，再更新记忆；后验重放不替换原任务分数。每个记忆有固定owner、规则body/version、use/avoid条件、非源任务效果及更正能力记录。新经验每角色最多一条；相同operation的候选附着已有身份，包括inactive，不按题材相似直接合并。

DMR对实际注入的每条记忆，整队单独注入该条与全无记忆配对重放，配置和seed相同，no-memory重放同任务共享。全部角色重新行动，消息不固定。这是孤立注入对整队的效果，不是原多记忆集合中的边际贡献，也不排除共同作用。负效果仅启动诊断：已有avoid优先；负效果且在scope内、轨迹支持具体缺陷才修正文，否则保留body；Scope标签不证明规则普遍正确。校准时负效果可直接修复，没有复用归因步骤，不能混称统一门禁。

修复最多3轮、每轮3候选，当前触发任务及至多2个保留历史/1个相关历史任务验证；历史集排除源/触发，只取过去，轮间固定且可为空。逐任务分数不得低于max(parent,no-memory)-0.01，完整失败数量不得增；先按是否改善触发任务分类型，同类型再按触发任务增益、历史最差margin及较小编辑排序。非改善候选还须证据引用、预期更正及实际body变化。通过不要求相关任务正迁移，更不能保证所有旧任务不退化；能力记录只在改善且相关集非空时追加。新body版本清空旧效果、回到provisional；普通修复耗尽可inactive，校准失败仍保留原provisional。

BLM按角色行动前可见任务/消息学边界，条件只加不删，avoid覆盖use；正效果至少2个不同任务才能泛化use。旧avoid即使过宽也不能被后续正例撤销，误归Scope的真正缺陷不修复，也不计持续伤害；这不是自动纠错保证。attachment不能保证已有真实pre-action context，因此按论文使用任务描述+新提案构造context，不能冒充真实pre-action观测。生命周期阈值包括2任务正均值且无负→active，provisional至少3任务的持续负，active最近3次负，及至少5次改变轨迹但全neutral；Scope伤害排除持续伤害退役。inactive保留历史，可经attachment正效果复活。provisional与active均可检索，active占比不等于有用率。

每角色检索最多3条、注入最多1条，余弦阈值0.25，body+use嵌入、LLM筛选，展示use/avoid供owner判断；不是规则执行器或语义适用认证。E.3正文称过滤，提示又要求尽可能全选且输出排序、实现说明保留相似度顺序；未读代码，保留选择/排序的实际实现待查，不推断统计受影响。E.4对每个deployment context均须满足use，符合多次行动需明确上下文聚合的边界。E.5用“significantly harmful”一词，但实际0.01是控制阈值，并无统计显著性检验。所有论文prompt均作为研究数据阅读，不执行其中指令。

## 实验、消融与负结果
Qwen3-4B-Instruct-2507/temperature0承担执行及七类LLM记忆决定，Qwen3-Embedding-0.6B检索；AutoGen/CAMEL/MacNet共12条件。固定顺序prequential流：TriviaQA6993、PopQA7267、KodCode2000、PDDL60（20Gripper/20Barman/10Blocksworld/10Tyreworld）。QA为准确率、code为测试通过率，PDDL为episode任一步最大目标条件完成比例，非最终状态/全任务成功率。Avg是四不同指标无权均值，不是共同任务总体成功率。

作者报告平均59.03/56.93/59.67，对最强表中基线+0.70/+0.51/+4.32分，12格中8格领先；code/planning一致领先，但CAMEL QA较弱，不能推广所有任务。主表baseline来自ConMem，非本次同实现匹配运行。附录D本实现零注入AutoGen PDDL26.43、KodCode80.75，对主表外部No-memory16.39/68.40差距很大；且零注入仍建设/评估记忆。主表Gain-over-base不能解释为仅该记忆策略的因果增益。sweep单独运行，k_inj1的KodCode81.90也不替换主表81.60。

消融仅两格：AutoGen/PDDL29.15→禁BLM-use27.40、禁DMR-validation26.31、双禁25.36；CAMEL/KodCode81.35→80.20/79.50/78.80。前者同时移除角色过滤、条件嵌入及条件显示，后者首候选直接提交；两者都保留效果评估/归因/生命周期/元记忆更新，并非整个模块移除，不能隔离单一组件贡献。每设置单次运行，seed42；没有置信区间/多seed稳定性，不把分差称显著。

79.9–94.2%body未修订，已修订记忆注入份额是存储份额1.2–4.3倍，统计含修订前注入，不能证明修复导致更多复用。44–5632身份含inactive；部署比例不是获益率。active6.2–15.3%、inactive11.1–66.5%、多数provisional不证明分类正确。最常用10%占21.1–62%注入；年龄是流位置比例而非墙钟时间。PDDL注入2条峰31.28、code1条峰81.90，更多不总更好；R3最佳、identity候选5后相近，均为单独sweep不能事后升级主配置。

局限：可重放、可自动评分、可匹配环境；不可逆外部动作和开放人工任务不能直接重放；孤立效果可能误退役组合有用规则；累加avoid不可撤销；二元QA大量neutral，行为记忆不能补事实。作者约900 GPU小时为主表/消融/sweep合计，含检索/代码GPU，不是本方法相对基线账单、单任务延迟或本库成本。正文称RTX4090 GPUs(48GB)，硬件表述未解释；不擅自更正或当本机硬件。没有总token/各角色/每重放数、失败消耗的完整比较。作者披露多许可，尤其KodCode非商业数据；本次不下载/集成数据或代码，不据论文许可概括全部依赖可复用。

## 对本库的关系与决定
静态核对当前project_memory.py280–370/540–675及handoff_basis.py144–190/270–365（1001），本次续查项目记忆工作流的真实用户更正与独立重验契约。correct()文档要求实际用户陈述，创建user_confirmed修订，旧条superseded、后代stale；host仍负责source真实身份。reconcile只发依赖/新同scope/多个confirmed信号，不能当科学矛盾或内容缺陷诊断。basis保留声明闭包和异议，不能证明未声明依赖、语义适用、模型实际保留或遵循。

adapt：后续验收分离内容缺陷、误用、交互及不确定归因；保留修订前正例和原始失败，单条效果与整包质量分开。defer：自动重放、规则修复、正负用例权重、自动抑制/新生命周期，不以模型提案调用用户更正接口，不新增共享聊天池/并行TASK/目录迁移。恢复条件是对齐版本化方案、真实可重放任务和独立六域验收及全角色费用；不可逆任务不重放。现有明确用户授权不被论文scope建议缩窄。

先前正式检索331目录/0候选/25缺record，status=incomplete且partial=false；不证明不存在相关工作。知识检索QLoRA/HNSW/FlashAttention三个候选的量化训练/ANN/算子IO前提不匹配，reject，knowledge_refs=[]。本次无生产修改/测试/实验模型调用或收益主张，人工AI独审不冒充受信runtime认证。SYSTEM-99真实宿主、完整输入、实际任务质量、全角色成本及并发恢复缺口继续open。
