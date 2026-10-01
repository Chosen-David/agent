# 外部 Agent 项目沿用与能力发现

[返回首页](../README.md) · [通用主 AI 调度](../prompts/orchestrator.md)

本仓库的目标不是重新实现所有 Agent 框架，而是把**用户目标 → 合适工作流/Skill → 工具执行 → 可验收交付**这层经验固化下来。遇到本仓库能力不足时，主 AI 可以进入经过筛选的外部项目，读取当前实现与使用约束，再决定复用其 Skill、方法论或运行时。

> 原则：优先沿用成熟能力，避免复制整个仓库；先核实当前版本、许可证、依赖和接口，再接入。外部项目是能力来源，不自动获得用户账号、网络、GPU、第三方服务或安装权限。

## 推荐项目分层

| 项目 | 建议定位 | 优点 | 主要不足/风险 | 本仓库如何沿用 |
| --- | --- | --- | --- | --- |
| [Anthropic Skills](https://github.com/anthropics/skills) | **默认沿用：Skill 结构与按需加载规范** | Skill 自包含、触发描述清晰、可带 scripts/resources；跨任务复用成本低 | 偏能力原子，不负责完整跨领域 workflow；平台实现仍有差异 | 新 Skill 优先采用兼容的 `SKILL.md` 组织；只复用与当前任务相关的 Skill，不全量加载 |
| [Superpowers](https://github.com/obra/superpowers) | **默认沿用：Skill 发现、流程纪律与回归测试思想** | 强调先发现 Skill；把 Skill 编写当作 TDD，适合验证“Agent 是否真的学会了流程” | 规则偏强、主要面向软件开发；“任何任务都必须调用 Skill”不适合本仓库的通用助手定位 | 沿用 Skill regression / pressure scenario / discovery 优化；不照搬其全局强制调用策略 |
| [BMad Method](https://github.com/bmad-code-org/BMAD-METHOD) | **默认沿用：right-sized workflow 与 durable context** | 能按任务规模决定规划深度；强调显式决策、上下文延续和已有代码库接入 | 主要针对软件开发；完整流程用于普通问答会过重 | 借鉴“简单任务直达、复杂任务加深流程”的路由；科研/旅行等领域使用同一原则 |
| [Fabric](https://github.com/danielmiessler/Fabric) | **推荐能力库：Pattern / 单任务 Prompt** | 大量现实任务 pattern；轻量、易复用、适合一次性转换/提取/总结 | 许多 pattern 仍是单轮 prompt；状态、工具编排和验收弱于完整 workflow | 当缺少某个单步能力时检索 Fabric pattern，抽取可验证的方法，不把整个 workflow 降级成 prompt collection |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | **按需接入：可执行 Agent runtime** | Agent、tools、handoffs、sessions、tracing、human-in-the-loop 等运行能力完整，适合真正部署多 Agent | 引入代码依赖和运行环境；本仓库目前很多场景只需说明性 workflow，无需 runtime | 只有用户要部署长期运行、多 Agent handoff、session/tracing 时才考虑；工作流层保持独立，避免锁死单一 SDK |
| [LangGraph](https://github.com/langchain-ai/langgraph) | **按需接入：长时/有状态图工作流** | durable execution、state、interrupt、memory 适合断点续跑与复杂分支 | 抽象偏底层，学习和部署成本较高；小任务明显过重 | 需要可靠恢复、复杂分支、人机中断时作为 runtime 后端候选；普通 workflow 不依赖它 |
| [Agency Swarm](https://github.com/VRSEN/agency-swarm) | **按需参考：角色化 multi-agent** | Agent 目录、工具与通信流清楚，适合显式团队角色 | 对角色划分依赖较强，易为了“多 Agent”而多 Agent；需要 Python runtime | 仅在任务真的需要长期角色分工与通信时参考，不把当前顺序执行伪装成并行专家团队 |
| [MetaGPT](https://github.com/FoundationAgents/MetaGPT) | **架构参考：SOP + Team** | “Code = SOP(Team)”体现把组织流程程序化；软件项目端到端产物丰富 | 软件开发垂直、运行栈较重；固定角色模板对跨领域任务未必合适 | 借鉴 SOP 显式化与交付物链，不直接作为通用主 AI 的默认运行时 |

## 推荐沿用顺序

主 AI 遇到能力缺口时按下面顺序判断，而不是随机寻找“大而全”的 Agent 框架：

1. **现有本仓库 workflow/skill 能完成**：直接使用，不增加外部依赖。
2. **缺一个可复用能力原子**：优先检查 Anthropic Skills、Superpowers 或其他 Agent Skills 仓库。
3. **缺一个成熟的单步 Pattern**：检查 Fabric 等 prompt/pattern 库，吸收方法并纳入本仓库约束与验收。
4. **缺领域流程设计**：查看 BMad、Superpowers、相关垂直项目的 workflow/SOP，迁移思想，不机械复制角色。
5. **任务需要真正的持久状态、多 Agent handoff、恢复或 tracing**：再评估 OpenAI Agents SDK / LangGraph / Agency Swarm 等 runtime。
6. **仍无合适能力**：主 AI 用当前通用能力完成最小可行版本，并记录能力缺口，后续再新增本仓库 Skill。

## 主 AI 进入外部仓库时的工作方式

外部项目允许作为“当前参考实现”被读取，但必须满足：

- 优先读取项目 README、相关 Skill/Workflow、示例和许可证；不要只依据项目名或旧记忆。
- 明确区分：
  - **方法论沿用**：只借鉴流程原则；
  - **Skill 沿用**：读取并调用对应 Skill；
  - **代码依赖**：实际安装/导入外部包；
  - **runtime 迁移**：把本仓库 workflow 映射到外部执行框架。
- 只有任务需要时才进入外部仓库；不要把所有仓库一次性塞入上下文。
- 外部 Skill 与用户当前硬约束冲突时，以用户要求和本仓库权限/证据规则为准。
- 发现外部项目提供更成熟能力时，先核查是否仍维护、是否兼容当前平台、许可证与依赖，再推荐沿用。
- 不把“GitHub 上有项目”描述成“当前会话已经安装并能调用”。真正运行需要平台或环境实际支持。
- 引入代码依赖前，应优先选择稳定公开接口；避免绑定外部仓库内部目录和易变实现。
- 如果只是借鉴几条规则，不复制大段受版权保护文本；用自己的表述记录原则，并链接原项目。

## 各项目的具体借鉴点

### Anthropic Skills

适合作为本仓库 Skill 目录的主要参考标准：

- Skill 应自包含，主文件描述**何时使用**与执行约束；
- 重型参考、脚本、资源与主说明分离；
- 按需加载，避免所有领域 Skill 常驻上下文；
- Skill 是能力单元，不等于完整任务编排。

**不沿用**：任何平台特有的“已安装即可用”假设。ChatGPT、Codex、Claude 等实际加载机制分别核实。

### Superpowers

最值得引入的是两点：

1. **Skill Discovery Optimization**：触发描述写“何时使用”，而不是把整个流程压缩到 description，避免模型只看摘要不读正文。
2. **Skill Regression Testing**：给 workflow/skill 建压力情境，比较没有 Skill 和有 Skill 时的行为差异，再修订规则。

例如旅行 Agent 应至少回归这些失败：
- 只写“酒店附近吃饭”，没有具体餐厅；
- 给写真馆名字但没有地址/营业情况；
- 两点之间没有交通方式；
- 行程过满，无午休或缓冲；
- 已完成的 live lookup 在恢复任务时被重复执行。

**不沿用**：对所有简单问题都强制调用 Skill。主 AI 仍遵守“简单任务直接回答”。

### BMad Method

沿用其 **right-sized process**：

- 明确的小任务 → 直接执行并验证；
- 多约束任务 → 建立轻量计划与状态；
- 长周期项目 → 持久化决策、依赖、交付与恢复点。

尤其适合本仓库科研和旅行 workflow：规划深度应由任务复杂度决定，而不是由“进入某个模式”决定。

### Fabric

把 Fabric 当作**可搜索的单步能力库**，而不是主调度器。适合补：
- 文本转换；
- 信息提取；
- 总结；
- 内容分析；
- 结构化输出等。

如果一个 Fabric Pattern 被多次证明有价值，应把它转化为本仓库的 Skill/辅助步骤，并补上工具、证据、状态和验收要求。

### OpenAI Agents SDK / LangGraph / Agency Swarm

这些属于 runtime 层。只有出现以下要求时才值得引入：

- 跨多个真实 Agent 的 handoff；
- 长任务断点恢复；
- 持久 session/state；
- human-in-the-loop interrupt；
- tracing / observability；
- 程序化运行而不是只在聊天里执行一次。

本仓库的 workflow 文档应保持 runtime-neutral；可以为某个 workflow 增加 adapter，而不是把核心规范重写成某个框架的 Python 代码。

### MetaGPT

主要借鉴 **SOP 显式化**：输入、角色、依赖、产物、检查点应清楚。不要因为 MetaGPT 使用“软件公司角色”就把科研、旅行、学习也强行套成 PM/Architect/Engineer。

## 项目推荐记录格式

以后发现新的外部项目，追加到本页时至少记录：

```yaml
project:
  name:
  repository:
  checked_at:
  category: skill | pattern | workflow | runtime | reference
  useful_for:
  strengths: []
  limitations: []
  license:
  dependencies: []
  integration_mode: borrow_method | reuse_skill | optional_dependency | runtime_adapter
  use_when:
  do_not_use_when:
  evidence:
```

其中 `checked_at` 是实际核查日期，不表示永久有效。

## 当前结论

本仓库继续保持 **Goal/Workflow 层**：

```text
用户自然语言目标
        ↓
通用主 AI 路由
        ↓
本仓库 Workflow
        ↓
按需加载 Skill / 外部成熟能力
        ↓
工具与可选 runtime
        ↓
验证后的实际交付物
```

推荐默认继承：

- Anthropic Skills 的 Skill 组织与按需加载；
- Superpowers 的 Skill discovery 与回归测试；
- BMad 的 right-sized process 和 durable context；
- Fabric 作为 Pattern 补充库。

OpenAI Agents SDK、LangGraph、Agency Swarm、MetaGPT 不作为全局依赖，只在任务的运行时需求真正出现时使用或参考。
