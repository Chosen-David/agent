# Claude Code 快速接入

仓库是主 AI 的工作流与技能层。安装接入按需调度入口、全部角色 Skills 和 Claude 子 Agent。简单任务直接处理，复杂任务才加载完整编排。适用于 **Claude Code**；后台监督是可选配置。

## 两步开始

```bash
git clone --filter=blob:none --depth 1 --sparse https://github.com/Chosen-David/agent.git
git -C agent sparse-checkout set agent_runtime scripts config templates plugins shared-references prompts workflows knowledge examples apps docs/codex_adoption docs/token_optimization docs/assets/readme
python3 agent/setup.py --target /absolute/path/to/your-project
```

默认使用轻量检出，包含两种安装器的全部依赖与应用，不带本库历史任务/实验结果和大型开发资料。维护本库自身或运行完整测试前，请在 agent 目录运行 `git sparse-checkout disable` 恢复完整工作树。

仓库的 Skills 随 clone 一起下载。脚本读取角色注册表，当前配置 16 个 Skills 和 16 个 `agent-*` 子 Agent，不需要逐个找文件。Python 3.10+，无 pip 依赖。Windows 原生环境默认复制技能，无需管理员或符号链接权限，命令中的 `python3` 可换成 `python`。Linux/WSL 默认链接技能，也可传 `--copy-skills`。已有链接保持链接；已有复制安装继续按复制方式更新。tmux 监督需要 Linux/WSL/server，仅后台任务才用。

如果直接在本仓库工作：

```bash
cd agent
python3 setup.py --target .
claude
```

如果接入其他项目，在安装后进入**目标项目**启动 `claude`。已有 Claude 会话应重新启动后检查 `/memory` 和 `/agents`；这些宿主读回才表明 Claude 实际加载了规则/角色。安装脚本只检查文件连通与环境，不自动调用模型或验证登录。

## 安装了什么

| 入口 | 用途 |
| --- | --- |
| 项目 `agent_doc/task/TASK.md` | 新项目创建空白日期索引，不编造任务；已有内容不覆盖，卸载也保留 |
| `agent_doc/task/task_details/`、`agent_doc/advice/`、`agent_doc/results/` | 创建目录，分别存任务详情、需评估建议、新数据/元数据/验证共享结果 |
| `agent_doc/guide/` | 仅 mkdir 空目录；人类自行发布 GUIDE.md，安装器不创建任何文件 |
| 项目 `CLAUDE.md` 中的受管块 | 简短按需入口，保留已有内容；不自动导入整篇编排说明 |
| `.claude/agent-workflows/orchestrator.md` | 完整编排副本，复杂任务按需读取 |
| `.claude/skills/<角色>/` | Windows 为内容校验的副本；Linux/WSL 默认链接，包含完整 references/scripts/assets |
| `.claude/agents/agent-<角色>.md` | Claude 可调度子 Agent，预加载对应 Skill，返回任务 ID、数据和证据 |
| `.claude/agent-workflows/installation.json` | 记录仓库位置、版本、受管文件哈希和安装清单 |

主 AI 保持通用身份，不因接入科研技能把旅行/编程等任务全部转成论文流程。项目现有规则和宿主权限继续适用。安装不会修改全局 Claude 配置、全局默认模型、permissionMode、API key，不会替换同名用户 Skill，也不会自动开始不存在的任务。

Git 仓库本身的 `CLAUDE.md` 可在 clone 后被 Claude 发现，引导完成 setup；正式角色接入仍需运行脚本。不要同时给同一项目安装这套本地 Skill 和同名 marketplace 插件以免名称冲突。已有 marketplace 用户可继续原方式使用，但需要主 AI 调度入口时优先选择此完整项目接入流程。

## 按角色选择模型

普通安装保持默认模型。可选 `--model-inventory /private/host-models.json` 为当前宿主已支持的型号生成角色配置；缺模型/能力则继承默认。Opus用于规划和审阅、GLM用于代码、Kimi用于长文/视觉阅读、DeepSeek用于推导/整理，完整18角色映射及依据见 [角色模型配置](docs/role_models.md)。这是可调整初值，不是本项目实测排名。

安装保存目录和路由快照；`--check`离线检查，更新时不传目录则保留上次选择。跨厂商通过 `scripts/run_role.py --adapter /trusted/agent-model-adapter` 的显式宿主接口；本库不附带厂商凭据或在线Agent后端。适配器/模型不可用时回退宿主默认，任务已启动后不自动换模型重跑。只有原生Claude入口消费安装的model字段；Codex/marketplace纯Skill安装不修改模型。

## 旧项目迁移与人类指南

已有根 `TASK.md` 而没有 canonical 索引时，安装器在写入前阻止安装并保留原文件，要求先核对/显式迁移，不偷偷创建第二份活跃清单。已有 canonical 加根导航可正常接入；两个含任务复选框的清单会阻止安装。

```bash
python agent/scripts/project_docs.py --root /absolute/path/to/your-project inspect
python agent/scripts/project_docs.py --root /absolute/path/to/your-project migrate --date 2026-10-07
python3 agent/setup.py --target /absolute/path/to/your-project
```

日期按真实迁移任务选择。迁移先检查活跃作业和引用，保存旧清单原始字节、稳定 ID、状态、证据与取消/阻塞记录；根文件只留导航。完整说明见 [项目文档治理](workflows/project_document_workflow.md)。

人类自行在 `agent_doc/guide/guide.md` 发布项目目标、硬约束、架构约定和优先级。它在当前用户决定和宿主安全/权限边界内具有最高项目规划优先级；AI 永不修改该目录任何文件。指南缺失可按现有明确授权继续，不能由 AI 代写。其他 AI 反馈或改进方案放 `agent_doc/advice/`，必须核验证据并记录 adopt/adapt/reject/defer 和理由。

## 第一个任务

在目标项目启动 Claude，检查 `/memory` 和 `/agents` 后，直接描述想完成的工作。例如：

> 找出项目的启动入口，给出最短运行步骤；若发现一个阻碍运行的问题，修复并做必要验证。只加载相关技能。

简单任务由主 AI 直接完成，已有项目规则继续适用。无需先配置 DAG、模型适配器或 tmux。
涉及多个专业产物、独立审核或长期运行时，主 AI 再按需读取完整编排说明。
复杂任务的指南保护、唯一任务索引、结果复用和独立验收要求仍按对应工作流执行。

**可选后台任务**：只有确需无人值守时才配置监督器。安装器不提供模型登录、可信 host adapter 或运行中的 tmux 服务；这些能力必须在实际宿主核验。文件检查成功不等于模型已加载技能或后台任务已启动。

## 可选文档依赖：一次安装、反复复用

PDF阅读/渲染、Markdown转HTML、PPTX生成及LaTeX源码使用独立固定版本profile，
不会随普通setup自动联网安装。完整checkout下显式执行：

```bash
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  install --pymupdf-license agpl-3.0
python -m agent_runtime.documents --root /absolute/dedicated/documents-env probe
```

PyMuPDF许可必须按用途明确选择AGPL或商业许可；首版支持CPython3.12/Linux x86_64/glibc≥2.28。
离线wheelhouse、四种公开操作、资源上限和失败恢复见[文档工具说明](docs/documents_profile.md)。
LaTeX源码可生成，TeX编译器未随库安装。

## 检查、更新和卸载

```bash
# 检查已安装文件、主 AI 入口、全部 Skills/子 Agent，以及 claude/tmux 是否在 PATH
python3 agent/setup.py --target /absolute/path/to/your-project --check

# 仓库更新；先 pull，再重新同步主调度副本与子 Agent 入口
cd agent
git pull --ff-only
python3 setup.py --target /absolute/path/to/your-project

# 只移除本安装拥有且未被用户修改的文件/链接；保留原 CLAUDE.md 内容
python3 setup.py --target /absolute/path/to/your-project --uninstall
```

安装/卸载在写入前拒绝指向人类 `agent_doc/guide/` 的目标或别名；角色链接的父目录也不允许重定向到指南。重复安装不会重复添加规则。安装清单绑定写入的 `CLAUDE.md` 受管块：本地修改会阻止更新并保留，未修改的旧版本在仓库升级后仍可安全卸载。同名用户文件/手改受管 Agent 会精确报冲突并保留；先比较内容再由主 AI 在授权范围内处理，不强制覆盖。复制安装按清单逐文件校验，技能中的用户修改或新增文件/目录会阻止覆盖，卸载保留这些改动。不要删除/移动仓库目录：链接安装会失效，复制安装的完整编排工具也仍从该仓库调用。更新前先让运行中的任务到达可恢复检查点，避免热替换其 Skill/验收规则。

### 复制技能的资源限额

复制安装、检查和卸载共用显式策略：默认每阶段最多100000个子条目、256MiB正文，
每文件32MiB、目录深度64（根为0）。重复目录别名按每个逻辑目标计费，忽略项也占条目数；
空目录、文件别名和旧清单继续保留。CLI 可用 `--skill-max-entries`、`--skill-max-bytes`、
`--skill-max-file-bytes`、`--skill-max-depth` 调整；值须正整数，深度支持上限128。
API 用 `SkillCopyLimits` 和 `skill_limits=`。清单不能自动放宽调用者限额。

限额分别覆盖整个操作的每个阶段，跨技能累计：安装预检旧副本/源码、实际复制、暂存核验、
替换前旧副本复查，以及最终检查的副本/源码；卸载先整体预检，再在移除时重新验证。
这些阶段各有预算，**不是整个操作总共只读256MiB**。流式读取最多使用64KiB块；为发现文件增长，
失败阶段可额外读一个判定字节，该字节不写入，首次超限后该阶段停止读取。
不承诺操作系统调用的硬超时、固定内存占用或文件系统元数据读取量。

超限会指出种类和路径；先确认内容，再在后续检查/更新/卸载中显式提高相应限额。
超过支持深度的旧副本保留，需另行处理，不会冒称本地编辑后自动删除。
源码或旧副本预检超限时不改安装；卸载预检超限保留全部文件和安装清单，便于重试。
复制途中超限清理本方暂存，不替换当前旧技能；更早的受管文件/其他技能可能已更新。
预检后的并发修改及后续I/O失败不具备整个安装/卸载事务回滚保证。

`--check` 的 `status=configured` 只表示文件接线正常。`capabilities` 分别报告 Python、Claude CLI、tmux 路径以及未检查的模型认证；`supervisor=not_started` 表示 setup 本身没有启动后台，不推断机器上没有其他监督器。tmux 无法跨服务器断电/重启保活，重启后由主 AI 使用同一 state-dir 恢复。

## 官方依据与验收

2026-10-06 核查 Claude Code 官方文档：

- [Skills 的项目目录与符号链接支持](https://code.claude.com/docs/en/skills)
- [CLAUDE.md 与 @import](https://code.claude.com/docs/en/memory)
- [子 Agent 与 skills 预加载](https://code.claude.com/docs/en/sub-agents)

本仓库的文件安装、幂等性、冲突保护、卸载、agent_doc/task/TASK.md 证据闭环由自动化测试验证；Claude 实际模型是否遵循所有流程必须通过真实任务观察，不能由配置文件保证。见 [本轮验证与限制](docs/tmux_supervisor_validation.md)。
