# Codex 本机接入与迭代

本仓库的 Codex 接入使用用户级技能和简短的全局调度指引，按需加载专业流程。当前提供 15 个角色技能；保持通用助手身份。本机安装先使用系统 skill-installer 从固定提交下载，再由下面的工具验证归属并接管更新。

## 安装和检查

在已 clone 且代码已提交的仓库中运行（Python 3.10+、Git）：

```bash
python scripts/setup_codex.py
python scripts/setup_codex.py --check
```

默认写入 `~/.agents/skills/<角色>/`，在 `CODEX_HOME/AGENTS.md`（默认 `~/.codex/AGENTS.md`）加入受管块，保留块外现有内容。状态位于 `CODEX_HOME/chosen-agent/installation.json`。可用 `--dest`、`--codex-home`、`--state` 指定独立测试环境。现有同名技能会阻塞。已由官方 installer 安装且全部内容与本仓库当前提交精确相同时，可用 `--adopt` 一次接管；该参数不跳过冲突检查。

目录符合 [OpenAI Docs 的本地技能机制](https://learn.chatgpt.com/docs/build-skills)，全局规则采用 [AGENTS.md 机制](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。下一轮或新会话发现技能；若宿主尚未刷新则重启 Codex。安装检查表示文件和版本接线成功；模型认证、实际技能发现和调用另做真实任务核验，见本轮 `validation.json`。脚本不修改模型、登录、审批、MCP、插件或 API 配置，不启动新 Agent/定时器。

工作流相对仓库解析；当前项目以 `doc/task/TASK.md` 为唯一日期索引，AI 在 `doc/task/task_details/*.md` 维护方法/进度/证据。其他项目绝不导入本仓库历史任务。每个安装角色携带 `references/project_document_workflow.md`：先核对人类指南及建议取舍，AI 不得在 `doc/guide/` 写任何文件，`doc/advice/` 须经过 adopt/adapt/reject/defer 与理由评估。知识结论检查前提和版本，不冒充本机实验。

## 每轮迭代

1. 读取当前项目人类指南、`doc/task/TASK.md`、关联详情/建议决定、运行状态及受影响输出。干净工作区先 `git pull --ff-only origin main`，或等效 fetch + fast-forward；有改动时保留检查点并整合，不用 hard reset 清理。记录本轮基线与目标。
2. 针对实际缺陷保留可复现基线、实现、验证和负结果。按改动运行必要检查；涉及主调度或共享契约时执行仓库规定的完整测试，不用文件安装成功代替模型行为验收。
3. 发布前再次 fetch，整合并发提交与冲突，重验受影响范围。按现有授权普通 push main；缺少原生 Git 写凭据时可用已连接 GitHub API 创建 tree/commit，并按 expected_sha 非强制更新。独立读回远端 SHA 与内容树。
4. 运行 `python scripts/setup_codex.py`，再 `--check`，同步已经验证的提交。只在两次任务之间同步；新启动的模型使用新版本。全局指引只放入口，专业正文按需读取。

脚本从 `git archive HEAD` 获取已提交字节，避免 Windows CRLF 工作副本影响快照；源技能/模板未提交时拒绝同步。每次记录文件哈希；用户编辑、额外文件、链接逃逸或受管指引编辑都会阻塞整个更新。Python 的 `__pycache__`/`.pyc` 不算用户改动。移除上游删除的文件时，只处理清单内且仍与旧哈希相同的文件；不递归删除技能目录。

目标布局也在备份和写入前检查，并在持有更新锁时复查：新文件路径已有目录或特殊文件、父路径仍为文件时，返回 `layout conflict`，保留完整旧安装和目录，不创建 pending/备份。上游文件↔目录转换需先人工核对归属并另行迁移；脚本不自动删除目录。普通新子目录仍可创建。该检查不提供针对任意外部进程并发修改的文件系统事务保证；真实 I/O 中断仍按下面的恢复流程处理。复现和回归见 [第二轮记录](round2/report.md)。

## 恢复与范围

更新前在私有 state/backups 保存被替换文件和原全局指引，原子写入单个文件，最后核对完整快照并提交安装清单。若 I/O 中断，保留 pending.json、旧清单和备份，下一次会阻塞。先核对 before/after、实际文件、备份及运行状态，再恢复完整旧快照或完成已验证新快照；确认一致后才清理自有 pending、临时文件与锁。不能按锁龄自动删除，也不能强行覆盖本机修改。

这是工作流、技能与工具的工程迭代，不是修改模型权重。本轮不重复创建已有云端每小时优化任务，现有 WSL 知识维护继续运行。Windows 宿主桥可显式配置 `--host-git-sync --host-skill-sync`：只在模型完成、全部工作文件与发布树一致后运行受保护的安装同步；必须同时开启 Git 验证。冲突会记录 host-skills.json 并保留已发布成果，不扩大模型 sandbox 写权限。本机维护入口启用此选项，后续验证过的知识更新也能进入用户技能快照。

仓库文档迁移、插件引用同步与本机技能安装是三种不同操作。`setup_codex.py` 的既有文件快照机制会携带新增包内契约和受管入口，不创建/迁移用户项目文档，不触碰其人类指南。只有已提交且独立核验后按原同步步骤执行并读回，才可报告本机已更新；新会话是否实际发现和遵守规则仍须另验。

安装器拒绝把 skills、state 或 codex-home 指向任何 `doc/guide/` 子树（含路径别名），并预检状态文件/备份目录的重定向；这属于工具入口保护，不是操作系统 ACL 或针对恶意并发改路径的事务保证。

新项目指令的执行前反思先查 `doc/results/` 的既有数据/元数据和当前独立验证，规则由每个角色的 `references/result_reuse_workflow.md` 发现；完整 checkout 使用 `scripts/result_store.py`，纯 Skill 分发不谎称自带结果运行时。新数据统一入 `doc/results/<run_id>/`，历史冻结引用保留真实路径和哈希；复用仍须代码/数据验收，明确复现与新主张必做实验不可跳过。
