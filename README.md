# Agent Workflows

一个按**场景与能力**组织的通用 Agent 仓库。主 AI 根据用户目标选择工作流，保持通用身份；科研助手是其中一个专业组合，论文伴读与知识讲解也可以独立使用。

适用于具备相应工具能力的 ChatGPT/Codex、Claude 及其他主 AI。当前提供科研/论文角色与独立旅行规划能力，并附完整工作流、可复制 Prompt 和插件包。未来可增加编程、学习、产品等领域的独立分类，不必改写主 AI 的身份。

## 从你的目标开始

| 目标 | 路由 |
| --- | --- |
| 让主 AI 根据各种任务选择合适 Agent | [通用主 AI 调度](prompts/orchestrator.md) |
| 推进科研项目，串起多个角色 | [科研项目调度](prompts/research_orchestrator.md) |
| 上传论文，边读英文原文边提问 | [论文伴读](workflows/paper_reading_companion_workflow.md) |
| 理解概念、公式、图或技术机制 | [知识点讲解](workflows/concept_explanation_workflow.md) |
| 单独实现代码或提高性能 | [实现与优化](workflows/implementation_optimization_workflow.md) |
| 规划城市游、情侣旅行或周末行程 | [旅行规划](workflows/travel_planning_workflow.md) |
| 没有匹配的工作流 | 主 AI 用通用能力处理，按需发现新 Skill，不强行转成科研任务 |

**分类是导航，不是限制。** 实现优化可以用于普通软件任务；知识讲解可以脱离论文；科研项目也可以调用伴读。安装专业技能不应让所有聊天都变成科研流程。

## 模式：默认编排，灵活调用

支持通用/自动、科研助手、论文伴读、代码实现与优化、知识学习、旅行规划等模式。模式选择默认流程，Agent 按能力跨模式复用。科研中随时调用知识讲解；伴读中可以调用代码实现；临时任务结束后回到原来的研究任务或阅读位置，不必反复切换整个模式。

用户可直接说“进入科研模式”“陪我读这篇论文”，也可以只提出任务让主 AI 判断。模式不增加权限或预算。完整规则见 [模式与跨模式调用](prompts/modes.md)。

## 主 AI：先核验方案，再执行

主调度先检查目标、假设、真实接口与可行性。原方案成立就执行；实质更优方案或重大设计分歧先写入项目临时区/方案文档，在对话简述依据，等用户对齐再实施。证据不足先验证，不编造数据或文献；简单任务不会强制变成研究项目。见 [反思与决策协议](prompts/decision_review.md)。

检查顺序为目的 → 合理性 → 接口与资源 → 同约束下比较 A/B → 证据 → 执行决策。接口用代表性输入输出核验；结论逐项对应实现、测试、数据或权威来源。可用 [方案提案模板](templates/decision_proposal.md) 记录等待对齐的版本与范围，续跑及角色交接保留同一决策；同意验证 B 不自动授权实施 B。

本仓库 `.codex/config.toml` 为支持该设置的 Codex 项目默认请求 `model_reasoning_effort = "high"`，不锁定模型。实际档位取决于模型、客户端、项目可信状态及更高优先级配置；不等于已开启 ChatGPT/Claude 的深度思考开关，不修改全局设置。部署和验证边界见 [验证记录](docs/main_ai_validation.md)。

旅行同步已按用户对齐方案采用 [插件内共享契约](plugins/travel-assistant/skills/travel-planner/references/planning_contract.md)，两种入口分别保留导航与详细工作流。设计依据见 [接口评估](docs/decisions/travel_workflow_sync.md)；没有接入 JourneyPilot runtime。

## 旅行规划

[旅行规划工作流](workflows/travel_planning_workflow.md) 会结合天气、开放/营业时间、逐段交通、用户已订酒店/活动、体力与午休约束生成可执行行程；复杂旅行采用 JourneyPilot 风格的 RequestContract → 候选研究/准入/选择 → 行程 → Intent Fidelity Gate → DeliveryBundle，并支持阶段状态与断点续跑。插件入口位于 [plugins/travel-assistant/](plugins/travel-assistant/)。

## 科研与论文生产

| Agent | 主要交付 | 工作流 |
| --- | --- | --- |
| 科研探索 | 查新证据、可证伪假设、最小判别实验、研究任务链 | [research_workflow.md](workflows/research_workflow.md) |
| 实现与优化 | 先进解法比较、正确代码、复杂度、CPU/GPU 实测与优化 | [implementation_optimization_workflow.md](workflows/implementation_optimization_workflow.md) |
| 论文数据可视化 `research-data-visualization` | 真实数值、主动美学设计、可复现数据图与数值/视觉检查 | [data_visualization_workflow.md](workflows/data_visualization_workflow.md) |
| 流程与架构图 `research-diagrams` | 精美布局、准确节点/箭头语义、可编辑源与最终尺寸检查 | [diagram_workflow.md](workflows/diagram_workflow.md) |
| 作图协调 `research-figures` | 旧入口兼容、图规划、混合多 panel 风格/拼版与整图验收 | [figure_workflow.md](workflows/figure_workflow.md) |
| 论文写作 | 指定模板下的源稿、引用核验、证据账本与可构建 PDF | [paper_writing_workflow.md](workflows/paper_writing_workflow.md) |
| 论文审稿 | 最新文献核验、贡献价值比较、科学审阅与修订任务链 | [reviewer_workflow.md](workflows/reviewer_workflow.md) |
| 最终 PDF 读者检查 | 实际逐页看图，检查乱码、重叠、图文含义与叙事理解 | [reader_workflow.md](workflows/reader_workflow.md) |

作图角色共享 [证据、设计与 QA 契约](workflows/figure_shared.md)。单图直接调用专业技能；混合图按 panel 分工并指定唯一整图负责人。美观不允许改数据或虚构结构；实际尺寸读图与可编辑源是验收要求。测试与边界见 [作图验证记录](docs/figure_validation.md)。

审稿人每轮按当前日期核查领域知识与相关文献，逐贡献评估**新颖性、可行性、必要性和收益代价**。它比较强基线与替代路线，区分投稿时贡献和今天的研究价值；可比性不足时不能仅凭 SOTA 数字否定工作。最终输出核验 → 判别实验/修订 → 复查的任务链。

## 论文阅读与学习

| Agent | 主要交付 | 工作流 |
| --- | --- | --- |
| 论文伴读 | PDF/链接接入、英文原文定位、双栏阅读页、阅读状态和问题交接 | [paper_reading_companion_workflow.md](workflows/paper_reading_companion_workflow.md) |
| 科研知识点讲解 | 核查来源、直觉、小例子、公式推导、图解和解释卡片 | [concept_explanation_workflow.md](workflows/concept_explanation_workflow.md) |

伴读服务用户阅读节奏；最终 PDF 读者检查服务论文质量验收，两者不混用。伴读中的知识问题交给讲解角色；没有独立 Agent 功能的平台可顺序执行相同流程，不能声称已启动另一个模型。

双栏 HTML 左侧保留 PDF 原页，右侧保存讲解卡片，并生成带论文 hash、页码和问题的提问上下文。**目前没有实时模型后端：复制上下文回聊天问答，再由主 AI 更新卡片。** 不保证能改变 ChatGPT 的原生界面布局。

## 快速开始

```bash
git clone https://github.com/Chosen-David/agent.git
cd agent
```

通用主 AI 入口：

```text
读取 README.md 和 prompts/orchestrator.md。
根据我的当前目标选择需要的工作流，保持通用助手身份。
目标：[填写]
已有材料：[路径、上传文件或链接]
约束/交付要求：[填写已知信息]
在授权范围执行到交付完成，不强制启动所有角色。
```

论文伴读：

```text
按 workflows/paper_reading_companion_workflow.md 陪我读这篇论文。
保留英文原文，优先显示原文与讲解并排的阅读界面。
知识问题使用 concept_explanation_workflow.md 核查并解释，必要时画直观图。
论文：[上传 PDF 或链接]
当前问题：[可选]
```

单独科研任务读取对应 workflow 中的完整 Prompt 即可。完整科研项目使用 [科研专用调度](prompts/research_orchestrator.md) 与 [项目输入模板](templates/project_brief.md)。聊天平台不能读本地仓库时上传相应 Markdown；只贴网址不能保证模型已经读到文件。

## 科研助手插件包

[plugins/research-assistant/](plugins/research-assistant/) 包含 11 个技能：

`research-assistant`、`research-explore`、`research-implement-optimize`、`research-figures`、`research-data-visualization`、`research-diagrams`、`research-write`、`research-review`、`research-read-pdf`、`paper-reading-companion`、`explain-research-concepts`。

这是面向科研与论文学习的技能包，不是通用主 AI 的替代品。仓库顶层通用调度独立存在。每个 Skill 有触发范围、完整参考流程和 `allow_implicit_invocation: true`，表示在相关任务中允许自动选择；并非每条消息都执行科研流程。

- `plugin.json`：可移植插件描述与 OpenAI 界面元数据。
- `.agents/plugins/marketplace.json`：本仓库的插件目录，配置 `INSTALLED_BY_DEFAULT`。
- `.codex/config.toml`：支持该机制且信任本项目的本地客户端中，配置该插件 `enabled = true`。

这些是**分发配置，不是账户安装证明**。克隆仓库不会把插件自动注册到所有 GPT 会话。ChatGPT 的技能保存、插件连接和公开目录发布是不同操作；平台审核仍需正常通过。官方机制会变化，使用时查 [构建插件](https://developers.openai.com/plugins/build/plugins) 与 [连接 ChatGPT](https://developers.openai.com/plugins/deploy/connect-chatgpt)。

当前支持该命令的 Codex 客户端可先核对 `codex plugin marketplace --help`，再添加仓库目录：

```bash
codex plugin marketplace add Chosen-David/agent
```

之后在该客户端确认实际安装和启用状态。没有此命令或 GPT 不支持仓库插件导入时，使用平台正式的技能安装方式；不能把配置复制到未知目录就声称完成安装。仓库不提供绕过平台审核的步骤。

## 本地 Web 阅读器

新增 [apps/paper-reader](apps/paper-reader/README.md)：在自己的电脑启动后，左侧看 PDF，右侧提问、保存讲解与笔记。可连接本机使用 ChatGPT 登录的 Codex 客户端，加载同一知识讲解规范；并非自动继承当前网页对话。支持 arXiv 导入与 QuantMLA 示例。真实模型连接需在运行电脑上登录验证。

```bash
python -m pip install -r apps/paper-reader/requirements.txt
python apps/paper-reader/app.py
```

启动后在该电脑打开 `http://127.0.0.1:8765`；在线讲解另需官方 Codex CLI 和有效登录，详见应用 README。

## 生成离线伴读页

需要本地 PDF、Python 和 PyMuPDF。按当前环境决定是否安装缺失依赖：

```bash
python -m pip install pymupdf
python plugins/research-assistant/skills/paper-reading-companion/scripts/build_reader.py paper.pdf --out reading/paper.html --pages 1-8
```

页面内嵌原页图与文本，可离线阅读；默认最多渲染前 20 页，支持 `--pages 1-3,7` 分批。`--notes notes.json` 加入 hash 匹配的解释卡片，格式见伴读工作流。渲染覆盖不等于 AI 已读覆盖。脚本不自动下载论文、不提供模型 API、不内置密钥。

## 外部项目沿用

现有各 Agent 与成熟开源项目的逐项对照、替换/组合建议见 [Agent 开源生态对照](docs/agent_landscape.md)。

本仓库不重新实现所有 Agent 框架。主 AI 在现有能力不足时，可按 [外部 Agent 项目沿用与能力发现](docs/external_projects.md) 进入经过筛选的项目读取当前实现，并区分方法论借鉴、Skill 复用、可选代码依赖与 runtime 接入。

当前默认建议：Anthropic Skills 用作 Skill 组织参考；Superpowers 借鉴 Skill discovery 与回归测试；BMad 借鉴 right-sized workflow 与上下文延续；Fabric 作为单步 Pattern 补充库。OpenAI Agents SDK、LangGraph、Agency Swarm、MetaGPT 只在运行时需求真实出现时按需使用或参考，不作为全局依赖。

## 共同约定

- **动态选型。** 先寻找当前更适合的 Skill，有证据的优势才替换后备。同项目锁定已验证版本，文献和技术事实按本轮时效核查。
- **方案可反思。** 保留用户硬约束，比较先进算法、数据结构、成熟库和 CPU/GPU 路线；按需关联 LeetCode 模式，说明工程场景的差异。
- **硬件与性能靠证据。** 核实型号/ISA 后选 PTX 或 CPU 原语，正确性、复杂度和实际测量分开报告；无 GPU 不声称 GPU 已验证。
- **讲解不猜。** 区分论文原话、外部事实、推导与教学例子。图形帮助理解，不能代替证据或真实测量。
- **模板与原页优先。** 写作遵循用户模板，最终 PDF 检查实际查看每页图片，提取文本或编译成功不等于验收。
- **意见先核验。** 审稿/读者的疑点可能被反证推翻；确认后再改，生成新产物后复查，保留稳定 ID 和依赖。
- **权限不扩张。** 技能启用不自动授予第三方账户、昂贵实验、后台运行或公开发布权限。

后备入口最初核查于 2026-10-01。第三方 Skill 不随本仓库分发；安装前检查其当下依赖、权限与许可证。没有“永久最好”的固定清单，也没有一次安装所有候选的脚本。

## 目录与扩展

| 路径 | 用途 |
| --- | --- |
| [prompts/orchestrator.md](prompts/orchestrator.md) | 通用主 AI 路由 |
| [prompts/research_orchestrator.md](prompts/research_orchestrator.md) | 科研组合调度 |
| [workflows/](workflows/) | 按角色独立的完整规范与 Prompt |
| [plugins/research-assistant/](plugins/research-assistant/) | 科研与论文学习的 11 技能插件包 |
| [plugins/travel-assistant/](plugins/travel-assistant/) | 旅行规划技能插件包 |
| [templates/](templates/) | 科研项目输入模板 |
| [tests/](tests/) | 伴读生成器的边界检查 |
| [docs/validation.md](docs/validation.md) | 本轮验证范围与限制 |
| [docs/external_projects.md](docs/external_projects.md) | 外部 Agent/Skill/Workflow 项目的优缺点、沿用顺序与接入规则 |
| [docs/agent_landscape.md](docs/agent_landscape.md) | 现有 Agent 与 PaperQA2、GPT Researcher、STORM、AI Scientist、coding agent 等的对照与优先路由 |

新增领域时加入独立工作流及入口，写明触发范围、依赖、输入输出、证据标准、验收与降级方式。简单任务不必创建任务链；复杂项目按实际需要组合角色。当前还未实现的领域只作为扩展方向，不列成已有 Agent。
