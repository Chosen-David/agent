# 项目检查工作区

`test/` 存放AI根据用户prompt和人类GUIDE编写的检查：lint shell脚本、编译/依赖结构检查、行为回归和轻量变异测试。`suite.json` 的每个check记录对应要求、脚本、类型与期限；按清单顺序执行，任一失败/阻塞后其余项记为not-run。测试代码和清单是可审查源码，不能为了通过而削弱用户要求。

```bash
/absolute/agent/.venv/bin/python /absolute/agent/scripts/project_test.py \
  --workflow-root /absolute/agent --project agent \
  --target /absolute/agent \
  --output /tmp/agent-system99/<unique-run-id>/checks
```

真实代码可以在相邻或其他目录；`--target` 必须为准确Git根且origin匹配清单（容忍可选`.git`后缀）。其他项目使用 `agent_doc/<项目名>/test/`，不在目标源码仓库生成agent_doc。

| 本库检查 | 执行内容 |
| --- | --- |
| lint.sh | Git差异空白错误，保留文件/行定位 |
| compile_structure.py | 内存编译运行时Python；核心调度模块不得反向依赖CLI脚本 |
| mutation.py | 真实core.py临时副本：原版通过，语法错和CLI依赖变异必须被抓住 |
| unittest回归 | 复用串行恢复/文档边界；验证外置入口的真实相邻Git仓库绑定和失败行为 |

清单支持 `shell`（bash）、`python`（当前解释器）及 `unittest`（目录发现）。脚本通过 `AGENT_TEST_PROJECT_ROOT` 和当前工作目录读取目标；`AGENT_TEST_OUTPUT` 与 `TMPDIR` 指向本次证据目录。每项必须有有意义的断言，退出0表示该脚本检查通过，非0表示未通过；入口不能证明任意脚本实际检查了需求。unittest额外拒绝零测试、skip和expectedFailure。

变异测试须先运行未变异对照，再确认指定缺陷被相应检查拒绝。缺工具、检查器崩溃和超时不算抓住缺陷。本库两个变异只验证这两种拦截能力，不代表完整变异覆盖率。只在临时副本变异，不改真实源码。

每项日志和 `report.json` 写入全新外部目录，绑定目标HEAD、Git状态与非忽略文件内容指纹、检查源码/入口哈希、Python版本、退出码和测试计数。运行期间输入变化使结果失效；忽略文件、依赖环境、外部服务不在内容指纹范围，报告不是独立认证。退出码0通过、1检查失败或运行阻塞、2入口配置阻塞；缺报告或旧报告都不能当通过。CI使用相同入口并设五分钟总期限。

脚本必须受信任且前台运行，不启动后台作业。入口不是沙箱；超时终止直接子进程并停止后续项，但不能证明脚本的后代进程或外部作用已结束，必须核对后再续跑。没有加载脚本对应的GUIDE/当前prompt时不能用清单文字替代要求核对。

依据：Lauren Tan 的 [All Code Is Slop (Except Mine)](https://ai.engineer/code/2026/talks/lauren-tan) 提倡设计约束与确定性反馈；本目录将讨论落实为可执行检查。目录布局与具体规则由本项目决定；测试不等于形式化证明。

迁移v1：先启用集中test工作区。当前唯一TASK仍为 `agent_doc/task/TASK.md`，人类指南仍为 `agent_doc/guide/GUIDE.md`；不复制出第二份TASK或指南。文档入口、嵌套guide守卫及受管恢复路径切换尚待下一阶段验证。已有测试暂不搬移，按需复用以保持当前CI。

注释策略以 [concise engineering](../../../workflows/concise_engineering.md) 为准。`comment_policy.py` 用Python tokenize检查新增COMMENT token，保留必要指令及公开docstring；仅覆盖Python，不能判定docstring是否必要或任意语言的注释。Shell新增普通注释由主agent自检。默认相对HEAD检查已暂存、未暂存和未跟踪Python；CI用PR基准或push前SHA设置 `AGENT_TEST_BASE`，无有效基准即阻塞。历史注释不批量删除；新提交复验须显式指定改动前SHA，不能对自身HEAD做空差异检查。

真实功能、源码入口及未覆盖项见 [features.md](features.md)。首次运行先用 `python -m venv /absolute/agent/.venv` 创建环境；本套件不需要第三方Python包。

重复验收先核对当前要求与suite覆盖，再直接执行已有入口；不要每次重写或整份读取脚本。成功回执保持status/report两字段；失败/阻塞回执附各检查状态、退出码、计数和日志路径，not-run不伪造日志。先读失败项日志，需要核对来源/输入/范围时再读完整report；简短回执不是独立验收。修改测试前仍需阅读对应实现和要求。

可选载荷测量：在.venv安装`tiktoken==0.12.0`后，设置`TIKTOKEN_CACHE_DIR=WORKFLOW_ROOT/.venv/tiktoken-cache`，运行`.venv/bin/python agent_doc/agent/test/token_cost.py --output /tmp/agent-system99/RUN_ID/payloads`。它对真实core.py的通过/语法错/依赖错场景执行相同检查，比较内联相同代码与复用文件调用的命令和输出token；保存原命令、原输出及哈希。这里不启动第二模型，内联是等价载荷对照，不是模型自行生成脚本的实验；没有覆盖推理、历史重传、缓存计费与首次编写维护成本，不报告端到端token节省。冷启动的完整suite清单单独计入，不能只报热复用。
