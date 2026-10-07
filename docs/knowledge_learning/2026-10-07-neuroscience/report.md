# 跨物种神经科学知识增补（2026-10-07）

检索窗口为2021-10-07至2026-10-07。本轮定向选取2023–2026年的10项研究：9篇正式论文、1份明确绑定版本的作者预印本，另核查4篇作者/机构博客。知识库从46增至56条。不是五年文献穷尽综述，也不是所有物种的完整脑图谱。

已读论文的相关结果、对照、讨论、图注及可访问的方法；鸟类工作未读取单独的补充Methods或Science终版，最新2026-09-29论文依据出版方网页相关章节。全文/缓存私有，公开目录只记录定位、读取范围和实际缓存哈希。sources.json中的path相对于私有.agent-runs/neuroscience，不能当作仓库公开全文链接。Nature下载曾返回HTML挑战页，未将其误记为论文PDF。

## 跨物种结构的比较范围

| 对象 | 本轮实际研究的结构/层级 | 可比较的内容与边界 |
|---|---|---|
| 线虫 | 头部神经元与突触/突触外通路 | 解剖边与刺激传播的差异，不是全部行为图谱 |
| 果蝇 | 单只成年雌蝇脑的化学突触连接组 | 脑区、细胞、阈值与缺失边，不涵盖全部腹神经索 |
| 斑马鱼 | 脑干眼动模块；另有单幼鱼全脑活动基准 | 局部模块模型与全脑预测须分别看，不把两份数据当同一个体 |
| 鸡及爬行动物对照 | 端脑pallium细胞类型、空间表达和发育 | 分子相似性、空间布局与同源性须分开，不等同哺乳动物皮层功能 |
| 章鱼 | 中央脑多个区域的睡眠电活动与皮肤模式 | 未覆盖全部腕部神经系统，不能据此推断梦 |
| 小鼠 | 视觉皮层兴奋性回路与几何关系 | 局部同调连接规则，不代表所有脑区 |
| 人/猕猴/狨猴等 | 宏观fMRI与部分人类MEG/iEEG | 意识内容、麻醉动力学与反应性是不同问题 |

每行的原始论文和取样条件见下列卡片；这是研究范围的对齐表，不是各物种全部脑结构的百科。

## 条目与可复用结论

每张卡均保留物种/阶段/方法/任务条件、负结果、限制、最小迁移对照和原文定位。所有 local_reproduction=not-run。以下“AI启发”是待验证假设。

<a id="neuro.worm-extrasynaptic-propagation"></a>
### 线虫：静态突触图不足以预测信号传播，需考虑突触外通信

ID `neuro.worm-extrasynaptic-propagation` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.worm-extrasynaptic-propagation.md)。

线虫单细胞光遗传扰动与全脑钙成像显示，解剖约束模型与实测传播存在差异；UNC-31 突变对照支持致密核心囊泡依赖的突触外信号参与快速动力学。

AI启发（未验证）：将固定路由与状态相关广播分开建模，检查被静态调用图遗漏的通道；不据此新增无约束的全局共享状态。

版本/原文：[Nature 2023](https://doi.org/10.1038/s41586-023-06683-4)；Results: Functional measurements differ from anatomy; Extrasynaptic signalling; Figs.3–6; Discussion; Methods。

<a id="neuro.flywire-structural-limits"></a>
### 果蝇 FlyWire：全脑结构图的版本、阈值与缺失边界

ID `neuro.flywire-structural-limits` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.flywire-structural-limits.md)。

成体雌性果蝇 FlyWire 提供可导航的神经元与化学突触图；论文分析绑定版本783，连接阈值与突触附着完整度会改变图统计，结构图不提供完整动力学。

AI启发（未验证）：作为稀疏计算图、局部反馈和类型化节点的候选来源；成熟数据门户可用于定位结构，不复制整个连接组到系统提示。

版本/原文：[Nature 2024](https://doi.org/10.1038/s41586-024-07558-y)；Reconstruction of a whole fly brain; Synapses and connections; Discussion; Extended Data Fig.2; data release v783。

<a id="neuro.zebrafish-modular-memory"></a>
### 斑马鱼脑干：模块化回路与眼位记忆的受约束前向模型

ID `neuro.zebrafish-modular-memory` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.zebrafish-modular-memory.md)。

幼体斑马鱼脑干连接组可分出眼动与身体运动相关模块；在符号、归一化及动力学尺度等约束下，模型预测眼位敏感性与慢动力学的群体分布。

AI启发（未验证）：研究分模块递归记忆与不同时间尺度；先问细节是否能被目标任务辨识，再决定增加模型复杂度。

版本/原文：[Nature Neuroscience 2024](https://doi.org/10.1038/s41593-024-01784-3)；Results: Axial and oculomotor modules; three-block cycle; Predicting neural coding and dynamics; Figs.2–5; Discussion。

<a id="neuro.avian-pallium-convergence"></a>
### 鸟类与爬行类端脑：细胞类型保守性、空间组织与趋同需分别比较

ID `neuro.avian-pallium-convergence` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.avian-pallium-convergence.md)。

2024预印本的鸡端脑单核/空间转录组与鼠、蜥蜴/龟比较提示：部分抑制性及海马相关细胞类型保守，其他兴奋性类型分化；相似表达不自动证明同源或同功能。

AI启发（未验证）：同一计算功能可能在不同空间布局实现；探索替代架构时按功能与资源约束评估，不把哺乳类层状布局当唯一模板。

版本/原文：[bioRxiv v1; subsequent Science publication metadata only 2024](https://www.biorxiv.org/content/10.1101/2024.04.30.591857v1.full.pdf)；bioRxiv v1 PDF pp.3–6,8–14; Figs.2–6 and experimental setup described in Results; separate supplementary Methods not reviewed; final metadata PMID39946461 (not final experiment verification)。

<a id="neuro.octopus-sleep-state-boundary"></a>
### 章鱼双阶段睡眠：状态与皮肤模式可观测，梦和巩固功能仍待验证

ID `neuro.octopus-sleep-state-boundary` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.octopus-sleep-state-boundary.md)。

Octopus laqueus 的行为干预与脑内记录支持静息/活跃睡眠两阶段；活跃睡眠出现醒样神经活动和皮肤模式，不直接证明做梦、记忆重放或学习收益。

AI启发（未验证）：以离线重放/维护阶段作为可测试设计候选，保持相同总训练预算对照；本论文不给出应采用的 AI 周期或收益。

版本/原文：[Nature 2023](https://doi.org/10.1038/s41586-023-06203-4)；Behavioural signatures of sleep; Neural activity during AS/QS; AS skin patterning; Figs.2–5; Discussion。

<a id="neuro.mouse-like-to-like-wiring"></a>
### 小鼠视觉皮层：相似响应连接规则、几何对照与 RNN 消融

ID `neuro.mouse-like-to-like-wiring` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.mouse-like-to-like-wiring.md)。

MICrONS 的小鼠视觉皮层数据支持兴奋性神经元的相似响应连接偏好；需区分轴突几何与单突触选择。论文RNN消融提供功能线索，但不能证明同规则对LLM普遍有效。

AI启发（未验证）：筛选基于功能相似性的稀疏连接/模块候选；作者现成消融支持先做有信息增益的对照，省去重新证明其简单RNN结论。

版本/原文：[Nature 2025](https://doi.org/10.1038/s41586-025-08840-3)；Multi-scale anatomical controls; Like-to-like connectivity in RNNs; Figs.1–6, especially Fig.6d; Discussion。

<a id="neuro.consciousness-adversarial-predictions"></a>
### 意识理论对抗性检验：预注册的不同预测分别受支持与挑战

ID `neuro.consciousness-adversarial-predictions` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.consciousness-adversarial-predictions.md)。

COGITATE 用人类多模态数据比较 IIT 与 GNWT 的具体生物预测；既有支持项也有负结果，不构成某理论整体获胜或 AI 意识判定标准。

AI启发（未验证）：将对抗式预注册用于 AI 架构比较：冻结竞争预测与失败标准，保留部分支持和不确定结果；本研究不证明 Agent 具备意识。

版本/原文：[Nature 2025](https://doi.org/10.1038/s41586-025-08888-1)；Preregistered predictions; Decoding/Maintenance/Interareal connectivity; Figs.1–4; Discussion; Extended Data Fig.7。

<a id="neuro.mammal-integration-anesthesia"></a>
### 跨哺乳动物麻醉：信息整合、抑制分布与局部控制的证据层次

ID `neuro.mammal-integration-anesthesia` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.mammal-integration-anesthesia.md)。

人、猕猴、狨猴和小鼠研究发现多数麻醉条件下 fMRI 信息整合指标下降，并在猕猴丘脑刺激后恢复；小鼠一种混合麻醉存在例外，指标不等于通用意识量。

AI启发（未验证）：区分信息冗余、协同和控制节点，筛选可恢复跨模块信息流的方案；不把该指标作为AI意识或最佳性能的代理。

版本/原文：[Nature Human Behaviour 2026](https://doi.org/10.1038/s41562-025-02381-5)；Results: Integrated information; Breakdown across species (Fig.2); thalamic DBS; gene-expression/model analyses; Discussion。

<a id="neuro.anesthesia-temporal-isolation"></a>
### 2026跨六物种麻醉研究：慢活动的时间窗口缩短与空间去耦

ID `neuro.anesthesia-temporal-isolation` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.anesthesia-temporal-isolation.md)。

2026-09-29发表的六物种成像分析发现麻醉下慢神经活动的内在时间尺度缩短、区域同步减弱；不能把它概括为所有频段都变快，也不能用反应性推断全部主观体验。

AI启发（未验证）：研究局部信息保持与跨模块传播是否共同制约长程任务；固定采样尺度后再作最小消融，不宣称更长记忆必然更好。

版本/原文：[Nature Neuroscience 2026](https://www.nature.com/articles/s41593-026-02460-4)；Published 2026-09-29; Results: intrinsic timescales and global networks, Figs.4–5; Discussion; Methods: datasets/feature extraction。

<a id="neuro.zapbench-forecasting-controls"></a>
### ZAPBench：全脑预测先校准基线、上下文长度与分布外刺激

ID `neuro.zapbench-forecasting-controls` v1；[知识卡](../../../knowledge/entries/neuroscience/neuro.zapbench-forecasting-controls.md)。

ICLR2025的单幼鱼全脑预测比较显示：长上下文多有利于远期预测，却非所有设置更好；简单刺激基线有竞争力，跨神经元混合与空间信息的收益需按设置核对。

AI启发（未验证）：利用成熟全脑数据/基线筛选预测架构；迁移到 Agent 长程记忆先区分远期与近期指标及未知协变量，不重造该基准。

版本/原文：[ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/668563ef18fbfef0b66af491ea334d5f-Paper-Conference.pdf)；§2–4; Figs.3–5; Appendix B/C and Figs.S3/S4/S7; official ICLR2025 PDF pp.4–9。

## 机构与作者技术博客

| 来源 | 日期 | 用途 |
|---|---|---|
| [blog-mouse](https://alleninstitute.org/news/scientists-complete-largest-wiring-diagram-and-functional-map-of-the-brain-to-date) | 2025-04-09 | 工具、资源与解释线索；经验结论回到原论文，预测不当作实验 |
| [blog-octopus](https://www.oist.jp/news-center/news/2023/6/28/octopus-sleep-surprisingly-similar-humans-and-contains-wake-stage) | 2023-06-28 | 工具、资源与解释线索；经验结论回到原论文，预测不当作实验 |
| [blog-simulation](https://alleninstitute.org/news/how-far-are-we-from-a-human-brain-simulation-and-what-does-that-mean-for-science) | 2026-05-21 | 工具、资源与解释线索；经验结论回到原论文，预测不当作实验 |
| [blog-zap](https://research.google/blog/improving-brain-models-with-zapbench/) | 2025-04-24 | 工具、资源与解释线索；经验结论回到原论文，预测不当作实验 |

## 已知缺口与未采纳结论

Science鸟类终版仅核对书目信息，实验仍绑定2024-04-30预印本；2026-03-24潜意识状态识别研究目前只有摘要，不发布实验卡；AI意识指标文章属于Opinion且全文未完整核对，不当作已验证意识测试。具体链接及状态见knowledge/neuroscience_sources.json的candidates。下轮优先核对这些全文，再补头足类腕部控制、蜜蜂/蜘蛛、树突与局部信用分配。

连接数量不是有效信息流；相似表达不是同样计算；睡眠活动不是梦的证据；麻醉无反应不直接等于无体验。2026两篇麻醉工作存在数据集重叠，不能称两次独立复验。Phi_R与IIT完整Phi须区分；不同时间尺度的“快/慢”不能混用。COGITATE检验的是具体理论预测，不提供意识理论的唯一胜者，更不证明AI有意识。

## 检索、决策与软件验收

[完整检索与40项决策检查](checks/retrieval-and-decisions.json)：新领域10条任务查询在文件/SQLite两后端均Top1命中（Recall@3=MRR=1），无关问题无命中。每张卡分别验证条件缺失、匹配、不匹配、显式复现，disposition正确且automatic_skip_authorized=false；引用哈希逐项复核。它们是作者编写的回归，不是盲测或模型行为评测。

语料增长暴露旧基础查询的原始Top3退化：[初始失败保留](checks/initial-base-default3-failure.json)。基础目录的文件Recall@3=0.95238、SQLite=0.80952；默认3候选SQLite上下文召回=0.85714。评估显式使用context-limit=5后，在相同8条/20000字符上限内两端上下文召回=1。没有更改检索运行时默认值，也不宣称原始排名回归已修复；已知领域先用search --domain收窄，缺上下文仍须继续检索。旧round2/morphology也沿用显式候选5门槛；文件后备不支持morphology，对此不作通过宣称。工程、RL/概率论原Top3门槛均通过。

全部六个目录的实际参数、原始与上下文指标见checks/*.json。最终软件测试结果另见[validation.json](validation.json)及checks中的真实日志；实测全仓548项：537通过、11跳过；Reader 3/3。插件生成闭包、知识格式与14个来源缓存哈希检查通过。测试使用冻结提交 fcc4e79347ef7b6f1316e764a86b15fbfc918542；其后仅增补验收文档，不改程序或卡片。生物学复现、GPU/训练性能、代码下载执行、AI意识检测和实时模型遵从性均未测试。

## 持续维护与发布

复用原有WSL tmux每3600秒维护任务，不新增重复调度。优先队列按神经科学→RL→概率论轮转，保留原有数学游标、AI Infra/AI算法/数据结构算法队列及历史。单次自动维护仍最多45分钟、核查3–6来源、增补0–3卡；这10卡为本轮人工核查，不冒充自动轮次结果。既有任务下次读取更新后的Prompt和learning_state；tmux只保持进程，不能覆盖关机/休眠，也不能保证本聊天持续运行。

主任务只读督导v1因来源定位修订后哈希变化撤销旧验收，保留失败记录；v2重验最终证据，扣除v1已用尝试，不增加预算、不将failed伪装done。最终发布前fetch，普通非强制CAS更新main，远端内容树独立核验后同步安装技能；功能发布 `effbab2480a770c70aaba075860c42464fe5a70d` 与完整树已独立读回，证据见[publication.json](publication.json)。安装后实际CLI复检10查询与40决策通过；见[installed-cli.json](checks/installed-cli.json)。督导v2对83项要求all_reportable=true、remaining=[]且done/monitor stopped/live=false；v1已cancelled/live=false。既有每3600秒维护live，下次2026-10-07 11:22:56 +08:00；见[runtime-readback.json](checks/runtime-readback.json)。收尾审计只修订TASK及文档，不改已测试代码或知识卡。
