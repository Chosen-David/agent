# tmux / TASK.md / Claude setup 验证记录

日期：2026-10-06。基线：`b1fabee7f44ee30d91dfa1b416bd13bc3beb5e4e`。本轮修改仅在 agent 仓库，未修改 SGLang、用户服务器、模型凭据或平台内部监督配置。

## 实现范围

- `setup.py`：项目级 Claude 主 AI 入口、注册表中的 14 个 Skills 与 14 个子 Agent；可重复安装、只读检查、冲突保护与保留用户编辑的卸载。
- `agent_runtime/task_manifest.py`：自动/手动来源、稳定任务 ID、全量需求映射、源版本核对、结果报告绑定与逐项剩余工作视图。
- `agent_runtime/task_supervisor.py`：tmux detached 入口、启动/worker 锁、guard 重启、每任务核对、失败/源变化保持监督、可信宿主适配器与维护回调、最终证据复查和清理。
- `scheduler.drain_once(..., run_id=...)`：托管 worker 只执行自有链，保留旧 API 默认行为。

## 已执行验收

新增针对性测试（含后续根 TASK.md/维护回调验证）：`test_task_manifest.py` 15 项、`test_setup.py` 10 项、`test_managed_supervisor.py` 7 项本地 worker/guard 测试通过；1 项真实 tmux 测试因宿主能力缺失而跳过。真实 SQLite/文件/subprocess 执行；guard 测试使用真实 SIGKILL、真实 5 秒重启与最终报告，不以 mock 代替进程恢复。

worker 测试**明确设置模拟 TMUX 环境标记**来隔离测试内部循环，不能据此声称运行在真实 tmux 中。guard/worker 的可靠性依赖可信宿主适配器按短 submit/poll 契约工作；没有验证任意外部程序的强制取消或 exactly-once。

本容器最初无 tmux。临时下载 Ubuntu tmux 3.4 与依赖，仅解包到临时目录，版本命令成功；实际新建会话在默认和项目临时 socket 目录都返回 `Operation not permitted`。因此没有验证真实 tmux 创建、SSH 断开后存活，未部署用户服务器。未更改宿主安全限制，也未声称已启动远端监督。

未安装/调用 Claude Code CLI，未运行付费/在线模型。安装测试验证真实生成文件、完整 Skill 链接和 Agent frontmatter，不证明模型一定遵循每条指令。默认 runtime 后端只读验收；主 AI 自动执行/恢复仍需项目内真实 `--adapter`。

## 复现

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
python setup.py --target /absolute/temporary/project
python setup.py --target /absolute/temporary/project --check
python setup.py --target /absolute/temporary/project --uninstall
```

在可创建 tmux server 的 Linux 主机上额外运行：

```bash
AGENT_TEST_REAL_TMUX=1 python -m unittest discover -s tests -p test_managed_supervisor.py -v
```

该测试使用临时项目，验证 launcher 退出后的 detached 存活、重复 start 复用、证据完成后退出及仅清理自有 session；它不等于服务器断电恢复测试。真实 SSH 断链、主机重启后手动恢复和特定模型后端仍需在目标服务器验收。

## 文件管理 Agent 独立使用场景

依据 skill-creator 的前向验证流程，给独立 Agent 提供 Skill 路径和一个未附答案的合成项目：实验与绘图脚本、doing 状态、散落指标/图/报告和未知来源文件。Agent 新增 CODEMAP、任务/未知文件清单与交接记录，保留根 TASK 和原状态，识别空 SVG、缺日志和未知归属，没有把登记完成当实验完成。

主 AI 重新读取产物并逐文件核对哈希：原 9 个文件不变，新增 6 个登记文件，移动/删除均为 0；两个脚本与生产者/消费者/任务均有映射。进程状态查询不可用、fixture 无 Git，因此只对历史重组提出方案。这是一次合成场景的实际 Agent 使用，不是普遍成功率或真实模型实验性能评测。全部原始输入与输出按原路径和哈希封装在 [试用证据](supervisor_research/evidence/file-management-trial.json)。

## 最终回归结果

最终全仓库发现 308 项测试，300 项通过、8 项跳过、无失败；跳过项为 7 项既有可视化环境依赖测试和 1 项真实 tmux 集成测试。另跑 paper-reader 3 项测试全部通过。`sync_plugin_references.py --check`、Skill frontmatter 校验和 `git diff --check` 通过。

[完整仓库测试日志](supervisor_research/evidence/tmux-setup-tests.log)已保存。额外在含完整目录的临时目标项目实际执行 setup → check → uninstall，读回 14 Skills/14 子 Agent、configured、无冲突；root TASK 创建/保留由生命周期测试覆盖。没有将环境跳过项计为通过。
