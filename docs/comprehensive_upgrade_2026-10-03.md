# Agent 全面升级：源码对照与实施记录

日期：2026-10-03。基线 main：`526bfc17732eb92cd9f8881ac13d8203cb15ffbc`。本次按用户授权在 main 工作，不创建分支或 PR。上轮 `be8fcc00` 只选择性恢复 registry、交接说明、探测/同步工具与测试；保留 main 的反思协议、配置与决策。期间 main 前进到 `db19c5f`，含增强反思协议和已对齐的旅行契约；本轮先fast-forward并逐项合并，未覆盖并发更新。再次检查发现 `3b3a06a` 拆分了数据图与示意图角色，继续fast-forward、保留其完整包内契约，为新增角色和混合图入口另开独立执行任务。

## 当前组织和实际能力

本仓库是可移植的指令/技能层，不是十二个已部署服务。`prompts/orchestrator.md` 保持通用身份，`prompts/modes.md` 选择默认模式，`workflows/` 保存领域流程；research 插件有11个技能，travel插件有1个。Skill用描述触发、正文约束、references按需展开；科研主调度自带其他角色流程作为离线后备。`apps/paper-reader` 和离线 `build_reader.py` 是实际程序。平台分发配置与模型、连接器或后台服务的真实安装状态不同。

原有长处是证据边界、用户硬约束、CPU/GPU性能口径、PDF逐页视觉阅读、午休和逐段交通，以及通用路由；不应换成另一套固定“软件公司角色”。缺口主要是执行规范过长、重复引用漂移、外部能力可用性描述不精确，以及缺少逐角色实际任务产物。

## 调研范围与选择

[固定版本及文件校验和](upstream_sources.lock.json)记录了实际阅读的文件、commit和日期。下表 stars 来自当日 GitHub API，只表示关注度，不是“执行效果评分”。没有发现一个可直接全面替代本仓库的项目；分层吸收更合理。

| 项目 | 当日 stars | 组织/实际读取 | 借鉴与不照搬 |
|---|---:|---|---|
| [Superpowers](https://github.com/obra/superpowers) | 294,513 | skills目录；systematic-debugging、verification-before-completion | 复现→根因→最小改动→验证；不照搬所有小改动强制测试、固定次数要求审批等绝对规则 |
| [Anthropic Skills](https://github.com/anthropics/skills) | 179,424 | SKILL+scripts+references；skill-creator、grader；PDF入口 | 渐进加载、隔离任务、产物级评分；不同文件许可证不同，PDF为专有条款，未复制其内容/实现 |
| [BMad](https://github.com/bmad-code-org/BMAD-METHOD) | 53,743 | 当前为skills+bmod/customize；bmad-review与verification-gap lens | 按审阅视角聚焦、追踪消费者与可观察断言；不照搬某adversarial视角至少10条问题的配额，也不引入其整套安装依赖 |
| [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 47,389 | hypothesis-generation、literature-review、scientific-writing、scientific-visualization、peer-review及部分验证脚本 | 假设与替代解释的可判别预测、论文版本去重、数值口径、缺测与独立重复；不把生物医学检查表强加Infra，不自动付费生图或安装全库 |
| [STORM](https://github.com/stanford-oval/storm) | 31,558 | knowledge_storm；knowledge_curation里的persona提问、检索回答、max_turn | 多视角补问题、检索有界、回答受证据约束；不把角色对话当独立证据，不把百科大纲当可投稿论文。最近push为2025-09，不能称所有候选都活跃更新 |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | 29,879 | multi_agents/agents、memory；orchestrator、fact_checker、MCP Skill | 明确研究/写作/核验边界与限额修订；其SKILL仅为短MCP入口，不是完整研究方法。fact_checker读取合成draft并由模型判断，不足以替代原文核验；不沿用预算耗尽后强制接受计划 |
| [PaperQA](https://github.com/Future-House/paper-qa) | 9,287 | src/paperqa/agents/tools.py；PaperSearch、GatherEvidence、GenerateAnswer、EnvironmentState | 发现论文→筛证据→回答分离；保留查询/文献/证据状态；GatherEvidence自身不宜并行，当前会临时变更问题；不因装有包就认定LLM/embedding/语料就绪 |
| [JourneyPilot](https://github.com/Lagom-TA/JourneyPilot) | 0 | StrictModel、RequestContract等真实类型 | 专题参考而非“高star优胜者”；严格版本/意图/交付关系值得借鉴，本地自然语言对象不是其API。没有部署或接通runtime |

MIT/Apache项目仅用自己的文字改写机制，未vendor上游实现。BMad API的license为NOASSERTION，但已打开LICENSE确认MIT正文；Anthropic按文件检查，不把整个仓库当统一MIT。

## 每个角色具体怎样改

[机器可读角色映射](../config/role_registry.json)是入口清单。每个SKILL显式读取包内 `references/execution.md`，把关键步骤放在长workflow之前；原有领域工作流入口也指向它；新作图家族保持完整副本契约，通过各SKILL加载角色补充。以下是方法改造，外部backend没有因此自动安装。

| 角色 | 吸收的机制 | 保留自有优势 | 本次实际任务 |
|---|---|---|---|
| 通用主AI | 能力/就绪/授权分开，产物交接检查 | 反思与对齐门禁、跨领域路由 | 配置/引用/交接完整性检查；未单独测开放域路由 |
| 科研主调度 | 状态和依赖、局部失效、检查真实产物 | REV/READ先核验后处理 | v2测量使依赖产物失效，保留独立背景 |
| 科研探索 | 替代解释、判别预测、证据筛选 | 创新与价值分开、最小实验 | 从混合性能证据决定go/pivot/stop |
| 实现优化 | 最小复现、失败回归、根因修复 | GPU同步、复杂度与端到端口径 | 修复滑动均值边界并运行检查 |
| 科研作图协调 | 依赖和来源分层、整图重新验收 | 最新main的表达目的路由与唯一整图owner | 混合方法示意与性能panel，保留各源及拼版源 |
| 数据可视化 | 缺测/重复单位、冗余视觉编码 | 最新main的图型选择与数值保真 | 保留退化及不同计时层级，不捏造误差 |
| 科研示意图 | 可观察断言与稳定节点/边清单 | 最新main的语义契约、美学与精修边界 | 6节点5条有向边，V绕过softmax，明确proposed |
| 写作 | claim绑定、数字和方法一致性 | 用户模板、构建/审读分离 | 修正夸大摘要，给证据表 |
| 审稿 | 分视角、可撤销发现、反查附录 | venue适配、公平对比 | 拒绝不支持主张，不误报已披露的退化 |
| PDF读者 | 声明与证据分开、hash绑定 | 每页看图、首遍不看源码 | 3页真实渲染与查看、处理渲染差异 |
| 论文伴读 | 检索/证据/回答分层 | 原文锚点、阅读状态、离线UI | 定位第2页，计算、卡片和实际HTML |
| 概念讲解 | 多视角补缺口、证据边界 | 短答案→手算→公式→边界 | 双路径softmax例子与Jacobian |
| 旅行规划 | 候选准入、修订/交付版本、费用单位 | 午休、服务多窗口、公开来源优先 | 两版行程，交通时长变更后重排 |

## 具体程序与接口修复

1. 恢复旧分支的backend registry与metadata探测，增加 `readiness=not_verified`、`authorized=false`。禁止对子模块做find_spec以免导入父模块执行初始化；异常变成诊断。
2. 实跑复现旧sync脚本的 `NameError: RAW_COPY_SOURCES` 后修复。只生成已有对应关系的科研镜像，包内存在的依赖优先相对引用；新作图家族用显式RAW_COPY_SOURCES保留六类工作流的字节一致、包内闭合副本。旅行全文未进入机械同步。
3. 增加 `validate_handoff.py`：验证产物哈希、相对路径边界、证据ID、任务DAG和完成状态；它不能证明语义正确，需读取实际产物。
4. 增加12个隔离任务、合成输入、预定rubric和工作区准备脚本；输出与评分分离，执行者不读取rubric或其他角色产物。

旅行B方案在本轮期间由并发main更新实施并记录用户同意。整合保留其planning_contract.md、local-travel/v1和全部新测试；执行补充改为遵循该唯一字段权威，明确输入per_vehicle/per_group到per_car/per_package的映射，并针对新入口重跑旅行任务。没有机械复制旅行全文或接入JourneyPilot。

## 评测解释

运行方法、逐项结果和实际产物见 [evals/README.md](../evals/README.md)。代码回归与LLM任务执行分别统计。每个角色一次合成任务只能证明这批任务的观察结果，不能据此称生产成功率100%、比基线全面更好或已通过外部服务集成。没有同模型旧版A/B，因此本次不报提升百分比。

外部MCP/API、真实旅行即时查询、GPU优化、长论文/真实投稿和跨客户端自动安装需对应环境另测；这是明确的覆盖边界，不以静态文档测试填充结果。今后新失败先保存脱敏最小输入和独立断言，再复跑受影响角色，不为了通过而放宽ground truth。

发布保护最后检测到并发提交 `741aa2c`（有界监督续跑协议）。保留该提交并重新通过76项根目录测试、3项阅读器测试；未伪造真实监督触发或追加未授权实验。先前各角色执行的确切skill快照已保存，监督续跑并未实际触发。
