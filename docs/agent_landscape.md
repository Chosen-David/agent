# 现有 Agent 与开源项目对照

核查日期：2026-10-01。

本页回答两个问题：本仓库已经做的 Agent，外部是否已有成熟实现；如果已有，应该替换、组合，还是继续保留自己的 workflow。

## 总结

| 本仓库能力 | 外部优质项目 | 建议 | 原因 |
| --- | --- | --- | --- |
| 通用主 AI 调度 | BMad、Superpowers、OpenAI Agents SDK、LangGraph | 保留自有上层路由，借鉴/按需接 runtime | 外部框架擅长软件开发或运行时，本仓库的价值是跨科研/学习/旅行的目标路由 |
| 科研探索 | GPT Researcher、STORM/Co-STORM、PaperQA2、AI Scientist | 升级为组合式 | 网页深研、文献 RAG、知识梳理和自动实验已有成熟实现，不应全部自研 |
| 论文伴读 | PaperQA2 | 优先作为多论文/本地语料检索后端；保留伴读 UI/阅读状态 | PaperQA2 的科学文献检索、证据排序、引用强，但不负责用户逐页阅读体验 |
| 知识点讲解 | STORM/Co-STORM（部分重合） | 继续自有 | Co-STORM 的多视角知识梳理和 mind map 可借鉴，但按用户问题做直觉/公式/图解教学不是其主要目标 |
| 实现与优化 | OpenHands、SWE-agent、Superpowers | 代码库级修改可优先外部执行；性能研究保留自有 | 它们更擅长 repo-level issue→patch；本仓库在 CUDA/硬件基线、复杂度、测量和系统优化上更专门 |
| 论文数据可视化与流程架构图 | 按当前任务验证专业 Skill | 专业入口分开，research-figures 协调混合图 | 数据侧数值保真，示意侧语义保真；共用主动美学设计、可编辑主源与最终尺寸 QA |
| 论文写作 | STORM、AI Scientist（部分重合） | 保留自有，前置阶段借外部 | STORM 适合调研→大纲；AI Scientist 能自动产论文，但模板化且风险/成本高 |
| 论文审稿 | AI Scientist reviewer、PaperQA2 | 保留自有，外部做第二意见/检索后端 | 自动 reviewer 可补问题发现，PaperQA2 可核查文献矛盾；venue 标准、公平比较和修订任务链仍需自己的规则 |
| 最终 PDF 读者检查 | 暂无直接替代 | 继续自有 | 必须逐页看最终渲染、检查布局/图文/叙事，和普通 PDF QA 不同 |
| 旅行规划 | LangGraph/Agents SDK 可作 runtime；现有 travel-agent 多为 demo | 继续自有 workflow | 午休、逐段交通、精确门店/入口、平台受限降级和增量重排更细 |

## 1. 科研探索：不要重复造“深研引擎”

### GPT Researcher

仓库：https://github.com/assafelovic/gpt-researcher

适合公开网页的大范围资料搜集、自动拆研究问题、多来源检索聚合、带引用长报告，以及 MCP/本地文档混合检索。

优点：
- 已有 planner → execution agents → publisher 的完整链路；
- 支持多 source、MCP、长报告和多格式导出；
- 比自己在 prompt 中手写“搜索很多网页再总结”更成熟。

不足：
- 主要是 information research，不等于科学假设设计和实验判别；
- 不能替代 GPU 实验、论文方法创新、可证伪 hypothesis；
- 引入 API/search provider 和运行环境。

建议：research-explore 在“公开网页深研”子任务上优先考虑 GPT Researcher；自己的 workflow 负责研究问题、可证伪假设、实验设计和结果解释。

### PaperQA2

仓库：https://github.com/Future-House/paper-qa

适合一组论文/PDF 的高质量检索问答、带文献证据的回答、文献元数据、重排、contextual summarization、contradiction detection 和本地 scientific corpus。

优点：
- scientific literature RAG 是核心能力，而不是通用 RAG 顺带支持；
- 可索引 PDF、Office、文本等；
- 有 agentic search/evidence gathering，并支持本地索引缓存。

不足：
- 不是逐页伴读 UI；
- 需要 Python、LLM/embedding 配置；大量文献还涉及外部元数据 API；
- 不能替代论文图像逐页视觉理解。

建议：
- paper-reading-companion：多论文或本地 corpus 问答时优先 PaperQA2 做 retrieval backend；
- research-explore/review：需要找支持/反驳证据时可优先 PaperQA2；
- 单篇正在逐页读的论文仍由自己的伴读 workflow 保持 page anchor、原文和讲解状态。

### STORM / Co-STORM

仓库：https://github.com/stanford-oval/storm

适合从零建立主题知识地图、多视角问题生成、调研→outline→长文，以及 human-AI collaborative knowledge curation。

优点：
- perspective-guided questioning 比单纯多搜几个关键词系统；
- Co-STORM 的 discourse + mind map 对复杂新领域学习很有价值。

不足：
- 输出目标更像百科式文章/知识整理，不是实验科研项目管理；
- 官方也明确生成物通常不是 publication-ready。

建议：research-explore 的背景调研/视角补全可借 STORM；concept-explanation 可借 Co-STORM 的动态知识图谱思想；论文正文仍需自己的 evidence ledger 和模板约束。

### AI Scientist

仓库：https://github.com/SakanaAI/AI-Scientist

适合在受控模板和 GPU 环境中自动提出 idea、跑实验、画图、写论文、review。

优点：
- 真正覆盖 idea→experiment→paper→review 的完整自动科研链；
- 对“自动科研”比纯 prompt workflow 更接近实际执行系统。

不足：
- 官方明确提示会执行 LLM 生成代码，有安全风险；
- GPU/环境/模板要求高；
- 原始项目模板领域有限，不能当任意科研项目的通用替代；
- 自动生成论文不等于可信科学结论。

建议：不作为默认 research runtime。只有用户明确要求自动实验、环境已 sandbox/container、预算允许时才作为可选 backend。

## 2. 实现与优化：把“写 patch”和“性能研究”拆开

OpenHands / SWE-agent 类项目更适合读取完整代码库、根据 issue 定位代码、编辑文件、运行测试并迭代 patch。普通 repository-level bug/feature，不值得本仓库再维护一套 repo runtime。

但 implementation_optimization_workflow 还覆盖算法/数据结构替代、CPU/GPU 分路线、CUDA/PTX/ISA 核查、正确性与性能实测分离、roofline/通信/硬件限制、负结果与适用范围。这不是 SWE-agent 的主要价值。

推荐路由：

repo issue / 常规 feature / bug
→ 当前成熟 coding agent / OpenHands / SWE-agent 类执行器

CUDA kernel / HPC / 模型系统性能 / 算法优化
→ 本仓库 implementation_optimization_workflow
→ 必要时让 coding agent 负责实际 patch

Superpowers 继续作为开发方法论来源，尤其 TDD、debugging 和 Skill regression，不作为底层 repo executor。

## 3. 写作、作图、审稿：不要被“自动写论文”取代

### 写作

STORM 可负责资料调查、多视角提问和 outline 草稿。AI Scientist 可参考自动实验后的 paper generation 和 reviewer loop。

本仓库继续掌握：
- 用户指定 LaTeX/Word 模板；
- evidence ledger；
- 图、表、实验快照的一致性；
- 不能支持的 claim 缩小而不是补写；
- 最终 PDF 构建和交付。

因此不是换掉 research-write，而是给它增加成熟的前置 research backend。

### 审稿

AI Scientist reviewer 可以作为第二意见，PaperQA2 更适合作 reviewer 的证据检索层：找同类方法、找 contradiction、检查引用所支持的 claim。

本仓库 reviewer 继续负责 venue/year/track、contribution 的新颖性/必要性/收益代价、资源公平比较，以及 findings → revision task chain。

### 作图和最终读者检查

目前没有发现值得直接替换的通用开源 Agent。

不要把 image generation / plotting agent 等同于论文作图：本仓库还要求真实数据、定义、可编辑图源、图注、论文叙事和最终视觉检查。

最终 PDF reader 也不应被 PaperQA2 替换；RAG 能回答文本问题，但不能证明最终页没有乱码、裁切、图例遮挡或版面错误。

## 4. 旅行 Agent：现阶段保持自有

GitHub 上有不少 LangGraph/CrewAI travel planner 示例，但多数是 attraction/weather/hotel/itinerary 多 Agent demo，并不自动优于本仓库。

当前 travel workflow 已明确处理：已订酒店/无酒店/只有集合点、精确门店与入口、默认午休、逐段公共交通/网约车取舍、最后入场/最后点单、平台只有摘要或登录受限时的证据等级、用户更新条件后的局部重排，以及 Word/PDF 交付。

建议：保留 travel workflow；如果以后要部署真正长期运行的旅行服务，再映射到 LangGraph 或 Agents SDK，不要因别人有 multi-agent travel demo 就替换。

## 5. 推荐的主 AI 组合路由

- 普通网页深度研究 → GPT Researcher（可用时）
- 科学论文集合检索/证据问答 → PaperQA2（可用时）
- 陌生主题多视角梳理/outline → STORM / Co-STORM（可用时）
- 自动科研实验 → AI Scientist（仅 sandbox + 明确授权 + 资源预算）
- repo-level bug/feature → 当前成熟 coding agent / OpenHands / SWE-agent 类 runtime
- GPU/系统/算法性能优化 → 自有 implementation_optimization
- 逐页论文伴读 / 教学 → 自有 companion / explanation；PaperQA2 可做检索后端
- 写作/作图/审稿/PDF QA → 自有 workflow；STORM/GPT Researcher 做前置材料，PaperQA2 做文献证据
- 旅行 → 自有 travel workflow；长期运行时才接 LangGraph/Agents SDK

## 6. 集成原则

1. 优先 backend，不优先 fork：能通过 CLI/API/Skill 调用就不要复制一大份外部代码。
2. 外部项目负责最擅长的原子能力：PaperQA2 负责 literature RAG，不负责最终 PDF 视觉 QA。
3. 主 AI 保持统一证据与状态：外部输出进入本仓库的 fact/evidence/task 状态，而不是让外部 agent 接管项目。
4. 真正接入时记录 release/commit、依赖和最小测试。
5. 外部 backend 不存在时，现有 workflow 仍能用当前平台能力完成受限版本。
6. 不要“装得越多越好”；只有反复出现且明显优于当前工具的能力才值得成为依赖。
7. AI Scientist / autonomous coding runtime 涉及执行 LLM 代码时默认 sandbox，不能把“研究 workflow”当成无限执行授权。
