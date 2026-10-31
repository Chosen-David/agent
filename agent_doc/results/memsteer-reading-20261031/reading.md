# MemSteer 2610.39276v1：证据诊断与设计优化的适用边界

实际HTML页眉2610.39276v1 [cs.AI]，2026-10-29。续接同SHA正文，完整读到主文1–5、伦理/可复现/LLM使用说明、参考文献、附录A.1–A.5/B.1–B.5/C、Tables1–9、Figures1–5图注、Eq1–2及未编号定义。没有完整PDF/像素或曲线点审读；图3/4引用趋势来自正文，图5设计步骤来自B.5文字，不补图内隐藏内容。最初12000字符已读记录只合并覆盖，不重复计篇。

## 方法：监督、诊断与选择（§3/Eq1–2、A.4–A.5）

MemSteer把无标注history变成(q,a,E)监督，不训练模型参数，也非直接修补memory bank。记录图边来自同会话、相邻文档节、显式引用或词法重叠；seed路径扩展取预算内连接子图B，保留原text/ID/结构元数据和source spans。LLM先作答案计划：目标答案、带span事实、每record贡献和组合操作；先程序检查结构/来源覆盖，再另调用生成独立问题。语义审查逐事实、逐record贡献、答案支持和问题–计划一致性，全部必要判断supported才继续。

Blind recovery只见q/答案类型/B，不见参考答案/计划；要求自报answerable、类型归一后精确答案相等、引用覆盖每个选中record。A.4区分文本归一、list集合相等、数值和单位精确相等、boolean精确。附录C明确：被引到不证明每record必要；同类LLM共享错误可漏过，不是人工认证/独立真值证明。材料bundle可恢复也不等于全history中任意检索可恢复。生成QA的train/val不交叉，但源history可以相同；不使用official题不证明语义/事实零重叠或真实用户需求覆盖。

MemSteer-Opt设计d=(store,retrieve,context)，固定answerer、指令和最终context预算；从record BM25原query、按rank装配开始，20次反思迭代。train错误先查最终answer context是否齐备必要record及span：齐备仍错标answering；缺证据则按source ID查当前memory能否取回record，有任何不可恢复标storage，全可恢复标retrieval。诊断依赖生成标注/ID可查规则，不是自动证明错误的因果根源或隐藏依赖闭包，context遗漏也并入此分法。每类最多10个采样、附q/reference/evidence/当前响应/诊断/设计与修订历史，防高频失败挤掉其它类别。

设计在同一个固定val上，只有二元accuracy严格增加才接纳；接纳后重跑train刷新反馈。二元选择是答案等同则true，否则固定LLM judge，不等于最终ATM的列表partial-credit QS。20次适应性反复用val仍有选择过拟合风险；没有本库权限/独审/原始观测保留门禁的授权效力。既有M⋆/MemEvolve保留自身起点/搜索空间，不是共同起点的算法公平竞赛。

## 实验群体、指标与主要结果（§4、A、Tables1–3/6–9）

ATM有11034 email/image/video records，main1013题、Hard31题；DS-V4-Flash负责answerer/open judge/proposer，QS含数值EM、list Jaccard partial和开放judge分，R@10是每问前10检索结果中的gold record覆盖比例再平均。RHELM21142互动record/10persona，官方1305题，有/无external data分开，GPT4.1mini回答与评价。官方引用baseline来自leaderboard/既有报告，不能当都在同一端到端环境重跑。

ATM generated/Official各400train+200val；Official这600题仍在1013评价内，generated不以official题优化，二者评价泄漏条件不对称。RHELM Official524train+264val仍计入1305；最终generated说明788训练项，最终val数量在正文未单独充分说明，不自行补成等预算。Table9十用户Official每人40%train/20%val，评价仍全体。上述数值不是严格完全未见test对照，不能将“接近Official”当人类标注等价/非劣定理。

ATM Base main QS54.9/R@10 61.7、Hard8.2/10.0；MemSteer68.3/84.1、29.1/43.6，主QS+13.4pp。Official67.3/83.5、27.9/42.2。正文称差1.1/1.3pp，而显示舍入数相减为1.0/1.2；保留原文与表的口径差异，不编造未舍入值。M⋆起点47.4→53.4 mainQS，Hard1.9→12.9；MemEvolve35.1→53.7，Hard7.1→9.5，而Hard R@10 18.7→18.6下降。表箭头HardQS+2.3与舍入相减2.4也不擅自修原数据。Oracle main71.8/Hard46.2，不是达到oracle即整个memory正确。

RHELM Base22.3/33.3（无/有外部），generated26.4/39.9，+4.1/+6.6pp；Official26.5/40.7仍更高。无外部RAGk50为28.9，不能说generated全榜最好。有外部33.9是同GPT4.1mini列的较强baseline；其它模型reference不是可控对照。冻结ATM设计跨域26.4/38.6，再用target generated优化30.6/42.8；同为更多优化预算，不把它与Base的一次数字只归为迁移本身。

六用户设计Table9(a)：4用户train、2val、4heldout。source679题31.5→34.3，heldout626题35.3→35.1退化，所有1305 pooled33.3→34.7；总体提高不能遮住heldout负结果。Martin228题41.2→37.7（−3.5pp）、David158题37.3→38.6；target continuation后44.3/39.2。Martin生成421监督=282train+139val，David337=223+114，official只作各自评价。不是对所有新用户普遍增益的保证；Table9(b)十用户都参与优化后所有用户提高，不能重称heldout结果。

Table8逐题型也不一致：最终从冻结ATM设计继续generated时，有外部fact59.4→55.6、mixed51.9→51.4下降，尽管总体38.6→42.8；misleading多数仍低。Qwen1M加外部15.3→8.1退化，不能把扩context当可靠提升。Table7换GPT5mini judge时**重跑完整QA**，检索query随机性使R@10也变化，不是同一回答仅换judge的隔离实验。main generated69.2低于Official69.6，Hard27.5高于24.3；native reference是Qwen3VL-2B/8B，与DS answerer不同，不能混称同骨干公平排名。

## 消融、成本和局限（§4.4–4.5、B.2/B.5/C）

Table4 QA质量为四项premise/clarity/answer/evidence全支持才记1，两个LLM judge均值，不是人工真值。Naive+checks保留21.2%、Ragas42.1%、MemSteer47.9%；通过率不是最终任务成功率。MemSteer无checks main/hard65.2/22.0→68.3/29.1，质量75.4→90.9；Ragas checks却Hard23.3→20.7下降（main63.0→65.1）。Naive54.2/5.3低于Base54.9/8.2。生成过滤可改善但非总收益，质量judge支持不认证无共享偏差或全用户任务有效。

Table5固定同600tasks/source/questiontypes/evidence-count与DS generator：DirectQA质量67.8/64.0k tokens每q，JointPlanQ73.1/68.2k，分段PlanQ85.9/105.1k。共同GPT4.1mini filter不见详细plan，只在过filter者上另由盲GPT4.1评估；不是全MemSteer审查pipeline，也不是全部候选全尝试/设计演化/查询账单。两阶段更高质量也更贵，不能以105.1k当当前用户实际模型usage或声称省成本。

Table4的两judge与Table5单盲review设计/群体不同，不强合成一套质量分。B.2训练预算100–500变化时，val也按约60:40扩大、从扩展生成池另采样，不只改变train大小；100→200最大增益/之后recall趋平来自正文/Figure4说明，未读曲线点数值，不能补造每预算结果或独立holdout证明。

四feedback条件同生成监督/Base：Random30给原始错例trace；加Gold指**生成监督的reference evidence**非人工gold；再加diagnosis；最终按类采样最多10。正文称diagnosis提升更大、分层组合QS最高，但Hard recall随机diagnosis更高；图3未像素审读，不填没有表列的精确数据。B.5是一条9次被接纳的设计轨迹（20提案中的接受部分）：逐步dense/hybrid/rerank/decompose/HyDE/第二阶段，最终4HyDE、120候选重排、读25record、允许4000token输出及验证。不是9独立实验或每个组件独立消融；完整构建/外部API调用/重试/验证/生成监督总成本、墙钟、反事实和统计置信区间不足，不能报告本库或作者端到端效率提升。

§C承认LLM共同偏差、引用覆盖不等于必要性、history生成分布不同于真实需求、搜索空间以retrieval为主、仅两基准且RHELM合成。伦理声明第三方API组合事实可能泄露个人信息；本次未处理新个人数据或执行作者接口。可复现说明承认remote API随机性/更新，未据模型名认证精确provider版本。

## 与本库关系

采用后续验收设计：区分原证据未保留、未装进消费者上下文、齐备仍解释错；按错误类型保留负结果，以真实最终动作/任务质量和全角色成本另验。复用MemoryLedger、结果合同与定向handoff的declared依赖门禁，不以生成的QA/reference/evidence替代用户验收或人工guide；引用覆盖不等于已发现所有更正/异议。

暂缓自动更换memory架构、在线反复执行生成代码/embedding服务、自动重置旧耗尽实验或迁移agent_doc。未识别/固定作者实现仓库，HTML中的Github均为reference/framework或arXiv反馈链接，不冒充作者源码；未读/执行作者代码、数据、原trace或复现实验。现有历史检索仅返回上一条partial检查点，不可当已验证原始结果复用。无本库生产改动或性能/质量测量。此新正文仅在完整独审后计一篇；旧双记忆候选缺反馈、此前六原件缺失和所有旧失败/冻结边界保持。
