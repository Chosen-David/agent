# 工程知识持续维护

用户已授权的本机部署在 2026-10-07 验收：WSL 3.0.1、Ubuntu-26.04 (WSL2)、普通用户 wi、tmux 3.6。定时会话为 socket `agent-knowledge` / session `agent-knowledge-maintenance`；实时心跳与 pane 读回成功。2026-10-07 按用户要求改为每隔 3600 秒一次；下次时间以 status 的 next_due_shanghai 为准。保留同一会话、配置、登录与历史轮次，未新增重复任务。迁移及研究卡证据见 [本轮报告](knowledge_learning/2026-10-07-rl-probability/report.md)。

每轮执行 [学习 Prompt](../prompts/engineering_knowledge_continuous_learning.md)，当前优先轮转 RL 与概率论，保留 AI Infra、AI 算法、数据结构的后续队列，核查 3–6 个来源，最多发布 3 张卡、45 分钟。论文原始实验/消融与固定代码优先，保留反例与条件，不运行大型 GPU 实验。代码/检索/相关测试通过后，按已有授权发布 main；CLI 没有 Git 写认证时可用已连接 GitHub 写工具和 expected_sha 非强制更新。认证过期、保护规则或并发冲突未解决时保留成果并报告阻塞。

真实执行链是 WSL tmux → `knowledge_maintenance.py` → Windows Python → `run_knowledge_windows.py` → 原生 Codex CLI。复用已有 Windows 登录，凭据不复制进 Linux。旧 CLI 0.114.0 的模型请求被拒绝；实际改用桌面应用自带的 0.160.1，登录探测返回 READY。第二次只读验收成功读取 GitHub 仓库元数据（push=true），并执行 decision CLI，返回 `insufficient_context` / `automatic_skip_authorized=false`。这些证明执行器及连接器可调用，不等于后续每轮来源质量/写入必定成功。

已将验收过的 CLI 及其五个 exe 依赖复制到私有 `.agent-runs/engineering-kb/tools/`，codex.exe SHA256 为 `3b8f6e33caa75f232558a3cf76ff9b87bb5ef6dbcf4996372f24e55c78b1b916`，全部二进制哈希保存在该目录的 manifest.json，避免桌面包更新移除版本路径。首轮复制遗漏工具宿主的失败已保留，补齐后实际 shell 文件写入与公开论文 HTTP 200 通过。登录、额度、模型可用性及 CLI 版本仍需维护；未安装第三方服务或付费 API。

模型采用 workspace-write，仅为该轮启用资料检索网络，不改变用户全局配置。`.git` 保持只读；实测 Git blob 写入被拒绝，不声称已通过。可信宿主的 `--host-git-sync` 在模型前执行 fetch/fast-forward，模型通过已有 GitHub 连接器发布；结束后宿主用临时索引比较完整工作文件树与远端树，只在完全相同时更新本地 Git 元数据，工作文件不删除。脏副本、越出知识维护范围或树不一致时保留成果并阻塞，不用 hard reset。真实 Git fixture 覆盖已发布树对齐、不匹配保留、脏副本和越界暂存。边界依据见 [官方 workspace-write 说明](https://learn.chatgpt.com/docs/agent-approvals-security)。


GitHub 写工具采用仅本进程的 granular MCP 审批与官方 `auto_review`；sandbox 提权仍禁用，用户全局配置不变。旧 `never` 策略的审批拒绝已保留；新策略实际创建无分支引用的无害 blob `80a6f5fd7f9b40163d956f72c87d0775e12cc391`，主 AI 独立读回一致。未来自动审查拒绝写入时必须保留成果并报告原因，不绕过审查。

## 查看、恢复与停止

从仓库根打开 WSL，`cd` 到同一仓库的 `/mnt/c/.../agent` 路径，然后执行：

```bash
python3 scripts/knowledge_maintenance.py status --config .agent-runs/engineering-kb/maintenance/launch.json
tmux -L agent-knowledge attach -t agent-knowledge-maintenance
# Ctrl+b，再按 d：只脱离终端，保留后台会话。
python3 scripts/knowledge_maintenance.py start --config .agent-runs/engineering-kb/maintenance/launch.json
python3 scripts/knowledge_maintenance.py stop --config .agent-runs/engineering-kb/maintenance/launch.json
```

当前 Windows 终端可直接附着：

```powershell
wsl -d Ubuntu-26.04 -u wi -- tmux -L agent-knowledge attach -t agent-knowledge-maintenance
```

`start` 对同一配置复用已有会话；`stop` 等当前有界轮次结束后退出，仅停止自有维护任务。配置、state/live/receipt、supervisor.log 与每轮 prompt/events/final/receipt 保存在被 gitignore 的 `.agent-runs/engineering-kb/maintenance/`。模型退出码只是执行状态，必须阅读证据和最终报告才能接受成果。脏工作树会阻塞该轮，避免覆盖用户工作。

guard 可在 scheduler 异常退出后重启，使用原有 next_due；停机后重新 start 会对已过期的 due 补跑一次，再沿原固定周期安排下轮，跳过已错过的时段，不追补无限轮次或并发轮次。首次从旧周历迁移或改变 interval_seconds 时，记录迁移并从当前时刻加一个周期；同一周期的重启保留原 due。45 分钟轮次不会把下次推迟为结束后再等 1h。若残留 round.lock，不凭过期时间删除：先核验记录中的 Windows/WSL 进程是否仍在运行和已有提交/成果，再人工恢复。没有已确认终态时，锁阻止重复模型执行。

tmux 可以在终端断开后继续；聊天界面本身无法迁移进 tmux。电脑关机、重启、睡眠或 WSL 被终止时任务不执行；本次未安装开机自启动，重新启动后运行上述 start 恢复。不要使用 kill-server 或停止用户其他会话。

## 迁移到另一台机器

脚本使用 Python 标准库，Linux 需 tmux/git。私有 launch.json 结构如下；路径必须替换为可信实际路径，不提交凭据。Windows 桥的 runner 使用 WSL 可执行的原生 Windows Python，其他参数是 Windows 路径；纯 Linux runner 自行提供同一 `--repo/--prompt/--run-dir/--timeout` 接口，windows_repo 为空。

```json
{
  "repo": "/absolute/agent",
  "state_dir": "/absolute/agent/.agent-runs/engineering-kb/maintenance",
  "session": "agent-knowledge-maintenance",
  "windows_repo": "",
  "timeout_seconds": 2700,
  "interval_seconds": 3600,
  "runner": ["/absolute/trusted-model-wrapper"]
}
```

配置不是部署证明，迁移后重新探测模型、源码检索与 GitHub 权限，并核验 status 的 live/heartbeat/pane。部署检查快照见 [本轮验证](knowledge_learning/2026-10-06-engineering/validation.json)。
