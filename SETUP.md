# Claude Code 快速接入

仓库是主 AI 的工作流与技能层。下面的安装会接入主 AI 调度、全部角色 Skills、Claude 子 Agent，以及 TASK.md/tmux 监督规范。适用于服务器上的 **Claude Code**，不是在 Claude 网页中粘贴链接即部署后台。

## 两步开始

```bash
git clone https://github.com/Chosen-David/agent.git
python3 agent/setup.py --target /absolute/path/to/your-project
```

仓库的 Skills 随 clone 一起下载。脚本读取角色注册表，当前配置 14 个 Skills 和 14 个 `agent-*` 子 Agent，不需要逐个找文件。Python 3.10+，无 pip 依赖。Linux/WSL 推荐；Windows 原生环境需要目录符号链接权限，tmux 监督运行在 Linux/WSL/server。

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
| 项目根 `TASK.md` | 缺失时创建空白总清单，不编造任务；已有内容不覆盖，卸载也保留 |
| 项目 `CLAUDE.md` 中的受管块 | 自动导入主 AI 通用调度；保留已有内容 |
| `.claude/agent-workflows/orchestrator.md` | 仓库主调度的当前完整副本，按仓库逻辑选择模式、Skill 和 Agent |
| `.claude/skills/<角色>/` | 指向已下载仓库 Skill 的目录链接，包含完整 references/scripts/assets |
| `.claude/agents/agent-<角色>.md` | Claude 可调度子 Agent，预加载对应 Skill，返回任务 ID、数据和证据 |
| `.claude/agent-workflows/installation.json` | 记录仓库位置、版本、受管文件哈希和安装清单 |

主 AI 保持通用身份，不因接入科研技能把旅行/编程等任务全部转成论文流程。项目现有规则和宿主权限继续适用。安装不会修改全局 Claude 配置、模型、permissionMode、API key，不会替换同名用户 Skill，也不会自动开始不存在的任务。

Git 仓库本身的 `CLAUDE.md` 可在 clone 后被 Claude 发现，引导完成 setup；正式角色接入仍需运行脚本。不要同时给同一项目安装这套本地 Skill 和同名 marketplace 插件以免名称冲突。已有 marketplace 用户可继续原方式使用，但需要主 AI 调度入口时优先选择此完整项目接入流程。

## 接入后主 AI 怎么做

可直接对 Claude 说：

> 按当前仓库配置接管这个项目。自动读取 TASK.md 编排任务链，配置真实工作 Agent 和主 AI 恢复适配器，在专用 tmux 会话里启动监督器。每完成一项核对对应任务、数据和剩余工作，直到全部验收完成后汇报。

也可以手动触发：

> 把我刚才列出的目标合并进 TASK.md，编排并执行任务链。

主 AI 负责将唯一总 TASK.md 固定在当前项目根目录，并在启动/恢复、委派前和逐任务结束时读取；code-organization 同时担任文件管理 Agent，协调各 Agent 的输出目录、产物清单和消费者引用。主 AI 负责规范化 TASK.md、补任务依赖/验收、配置 Agent、适配器和计时策略，验证后台启动的真实 ID/心跳，处理恢复，并向你汇报。任务文件可参考 [TASK.md 模板](templates/TASK.md)，不可覆盖已有任务。详细命令见 [监督工作流](workflows/task_supervision_workflow.md#tmux-与-taskmd-闭环)。

**可执行性边界**：本地 Skills/子 Agent 安装成功，不等于已连接可离线调用的模型或已启动监督器。tmux 必须在服务器可用，主 AI 必须配置真实授权的 host adapter；默认运行时只验证文件，不会自动调用 Claude。主 AI 的交互进程和监督器都在 tmux 中，仍需为恢复调用保存会话/job ID 与 submit/poll 接口。首次使用宿主信任提示按 Claude 本身流程处理，不跳过。

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

重复安装不会重复添加规则。同名用户文件/手改受管 Agent 会精确报冲突并保留；先比较内容再由主 AI 在授权范围内处理，不强制覆盖。不要删除/移动仓库目录，否则 Skill 链接会失效；检查会发现此问题。更新前先让运行中的任务到达可恢复检查点，避免热替换其 Skill/验收规则。

`--check` 的 `status=configured` 只表示文件接线正常。`capabilities` 分别报告 Python、Claude CLI、tmux 路径以及未检查的模型认证；`supervisor=not_started` 表示 setup 本身没有启动后台，不推断机器上没有其他监督器。tmux 无法跨服务器断电/重启保活，重启后由主 AI 使用同一 state-dir 恢复。

## 官方依据与验收

2026-10-06 核查 Claude Code 官方文档：

- [Skills 的项目目录与符号链接支持](https://code.claude.com/docs/en/skills)
- [CLAUDE.md 与 @import](https://code.claude.com/docs/en/memory)
- [子 Agent 与 skills 预加载](https://code.claude.com/docs/en/sub-agents)

本仓库的文件安装、幂等性、冲突保护、卸载、TASK.md 证据闭环由自动化测试验证；Claude 实际模型是否遵循所有流程必须通过真实任务观察，不能由配置文件保证。见 [本轮验证与限制](docs/tmux_supervisor_validation.md)。
