# COLLAB-01

Task-ID: COLLAB-01
Date: 2026-11-17

## Plan
用户授权：先读代码并复述，与用户讨论关键歧义；验收/约束脚本和变异假设先于实现，放 agent_doc/<项目名>/test/；逐步展示代码、结果、新发现并共同确定下一步。本次项目为 agent。不迁移旧项目目录或改人类指南。
计划 v2（2026-11-17，依据用户纠正及“开始 work”）：以真实任务行为验收为主，不实现自报记录分类器。第一小步接入统一协作流程与已有 Skill 路由，测试安装/加载/离线引用和文件故障注入；后续用真实任务对话及工具轨迹共审意图、测试先行与小步实现，再决定是否需要宿主强制门禁。每步展示代码、实际证据、限制与下一步，不把文档/打包测试当模型行为验收。

计划补充 v3（2026-11-17）：用户要求 AI–人类 / 双 AI 模式，并授权调研演讲和开源实现后整合。当前小步为来源核查、模式/审查契约及已有 API 故障回归；不启用第二模型或自动迁移历史保护计划。

计划补充 v4（2026-11-17）：用户授权直接升级，并改为批量实现后统一测试、集中修复，完成直接推远端 main。实现可选双模型协议、绑定两阶段任务文件与真实宿主身份；默认人类模式保留。GPT 接入复用本库 Codex 安装器，同步已提交 Skills 和受管指令；配置同步与真实模型运行分别报告，不修改人类指南。

计划补充 v5（2026-11-17）：用户明确四项验收：默认人类讨论与约十分钟超时双 AI 接续；实际环境探测并加载相关 Skill；直接路由任务验收脚本；串联可见规划、任务链、审查监督、实现与有界返修。计时只验收正常等待/超时接续/答复终止/恢复语义，不做毫秒级边界检查。沿用既有模型认证与项目测试入口；完整宿主调用和隔离须真实证据，不用合成测试冒充。

计划补充 v6（2026-11-17，用户明确要求实际 fix）：沿同一 COLLAB-01 任务继续，修复 Windows 原生入口、可信 Codex 宿主、真实双模型调用和人类/双 AI 显式切换。仅一个主 AI 写代码，审查者使用不同真实模型、独立上下文及只读沙箱。新增任务验收在 collaborative-flow/test_runtime_host.py；模式转换保留任务 ID、原始问题、预算和历史，失效的设计/测试授权不得复用，inflight/保护账本不得绕过。接入用户级运行配置，不改人类指南；真实调用记录和候选快照只放临时维护目录。验收包括真实讨论→设计审查→实现→测试→最终审查、人类反馈/切换、拒绝/篡改/超时及冷安装，未验收范围如实列明。

v6 范围澄清：项目代码和验收脚本由操作者明确声明可信，运行于当前 OS 用户；模型只读限制不等于测试进程隔离。Windows/POSIX 锁、输入和恢复属于本轮；未部署的后台监督、GPU、恶意宿主防护和全库绝对正确性不作完成声明。原始人类模式和旧保护账本保留，CLI 新任务默认双模型。

计划补充 v7（2026-11-17，用户明确纠正模型不应固定）：新 profile 默认记录自动选型策略；从有效 Codex 默认配置及分页模型目录获取候选，由默认模型在结构化枚举约束下选两个不同的实际模型，并验证真实调用。推理档位/提供方以实际目录和服务端身份为准，不写死模型系列。选型纳入持久调用预算，恢复/模式切换不得重新选型或清零；明确失败/结果不明时只允许带理由重试。旧固定 profile 支持，显式开启自动策略时保留旧配置与账本匹配，旧任务不强迁移。新增自动选型用例在 collaborative-flow/test_model_selection.py；实测当前默认和临时 CLI 默认覆盖的两条路径及真实完整流程，最终独立审查后推 main。

## Progress

### Progress v7（2026-11-17）
基于 main `89f93fc0`，新 profile 默认采用自动策略：读取有效原生配置及分页模型目录，由默认模型真实选择两个不同的规范模型，再核验实际身份和 nonce；不固定模型系列。旧固定 profile、任务配对、账本、回执和已用预算保留。恢复与模式切换不重复选型，模型上下文只携带选择摘要和哈希。

修复目录能力缺失、隐藏/重复/别名冲突、选型调用归属、任务状态及最终绑定竞争、一次性核对对象、外来 pending 记录和断连后误重试。缺少可信终态的已发送调用在本机退出后仍保持 pending；显式核对只证明本机终止，远端完成与计费不作结论。单文件与项目清单哈希分开标注，并在送审前机械核对，避免审查误读触发无效返修。

冻结代码 Windows 97 项通过；Linux 161 项中 160 通过、1 跳过，另 12 项验收器检查通过；24 项精确变异均被断言捕获，未修改控制组及源/测试哈希匹配。两条全新标准 `--backend codex` 流程均完成：默认 `gpt-6.1-sol` 主写、`gpt-6-luna` 审查；隔离原生默认配置为 `gpt-6.1-terra` 主写、同一独立审查模型。各 8 次调用，讨论/设计/最终审查全部批准，实际测试通过，运行前后代码哈希一致、全局配置未改、临时登录副本已移除。此前失败任务沿原账本显式追加 2 次审查额度，在原 20 次总上限内由 15 到 17 次调用完成；配对与已用记录未重置。旧 v1 三个真实回执仍可验证且零新增调用。

独立只读 `gpt-6.1-terra` 复核九项全部 pass、无 findings，批准本轮限定实现与发布前验收；原始证据留在仓库外 `C:/tmp/agent-system99/codex-auto-models-20261117/`。索引 `evidence-manifest.json` SHA-256 `e2c5573dfc7beb98a2bee10475f520988d2eb947acf88aaa6680c45bd98f878d`；独审 `implementation13-review.json` SHA-256 `77ad1cedc56a66436d0fbd5ecf26f19da353cf30fb085c964816d849d8672969`。既有未修改 dispatch alias / memory 日期失败及可选 fitz 缺口保留原说明，不宣称全库完美。发布回读与安装核验由本轮后续执行，临时项目、配置、密钥和日志不提交。
基线 main 7ac2e578d7969a327b59ba76d784b9e37b0c30aa，完整克隆。已读单主工作流、指南与决策协议；不启用子 agent。
新增 agent_doc/agent/test/collaborative-task/test_contract.py：8 项契约用例，全部因目标模块尚未实现而失败（预期红灯）；不是 8 个已确认产品缺陷，也不是变异杀死结果。
已核对 cursor/plugins 的 pstack/skills/create-verification-skill/SKILL.md 与 statechart/SKILL.md、MIT 许可。路由候选尚未安装或执行，不能声称可用。前者要求真实 launch/doctor/drive/evidence/cleanup；后者需 TypeScript、mise、Java/TLC，检查模型后还要在代码重放反例。
待完善：当前测试仅定义记录分类，非可信认证。字符串 evidence 与布尔先后声明不能证明真实文件、执行顺序或人类同意；后续须绑定当前规格/代码/脚本哈希及实际执行记录，测试覆盖伪造/过期/空清单/重复 ID/变异未运行等情况。不得把当前 PASS 记录定义宣称完整验收。
本步尚未修改实现/主入口/Skill，未提交或推送。下一步先向用户展示测试与路由范围，再细化证据契约。

### 2026-11-17：流程与入口接入

- 再次 fetch main，仍为 7ac2e578，ff-only 核对无远端新增。保持单主串行。
- 已用真实安装/加载测试替换先前 8 项自报记录草稿；未引入 agent_runtime.collaborative_task，也未实现虚假的人类同意认证。旧草稿的红灯事实保留在上文。
- 新验收先运行：5 个方法、11 个子场景失败，原因是缺少协作入口/文件；日志 /tmp/agent-system99/collab-01/red.log。测试草稿最初根路径层数写错，修复后才计入上述红灯，不将导入错误算产品缺陷。
- 新增 workflows/collaborative_implementation_workflow.md：读库/澄清、任务自己的输入→动作→结果验收、变异、验证方法边界、外部候选路由与五步共审。四个仓库入口及两个现有 Skill 导航到同一源；镜像由同步器生成。
- 测试先行记录见 agent_doc/agent/test/collaborative-task/README.md；根 tests 发现同一组用例。5 项通过（3.860s），包括复制/链接安装、独立包本地闭合、删除/篡改安装文件后真实 CLI 拒绝。两项文件故障不是业务算法 mutation score。
- 来源复核：2026-11-17 实际读取 pstack create-verification-skill 与 Trail of Bits property-based-testing 当前正文。其余候选沿用本轮前序已读入口；本次 create-formal-verification-skill 网络复核失败，未声称最新版已核验。只提供原始链接和按需选择规则，未复制上游实现、安装套件或运行 TLA+/Lean。
- 未执行真实模型对话验收，未证明 AI 理解/遵循率，未声称性能提升。作者测试是自检，整个 COLLAB-01 保持未完成。

### 本小步回归与共审检查点

- 全库首轮：2142 项，8 skipped，1 failure + 3 errors（426.695s）。3 个错误来自本任务详情缺 Task-ID/Date；已补齐。1 个原有 FIFO worker 测试超过 2s，不擅自放宽阈值。
- 修复后实际执行 `python -m unittest tests.test_repository_task_integration tests.test_supervisor_lock_files -v`：9 项全通过（9.168s），FIFO 不改代码/阈值即通过；只能报告复测结果，不能据此断言原超时根因。未再次运行完整 2142 项。
- Reader 3 项通过；插件同步 --check 与 git diff --check 通过。人类 guide 无改动。完整任务未结案，本小步保留共审，下一步拟用一个真实重试/取消任务验证对话与写入顺序；尚未推送 main。
- 原始日志仅为本机自检证据，不是独立验收；以下哈希固定日志内容：
  - `/tmp/agent-system99/collab-01/red.log` sha256 `f509b904cf056b529f78840b8aea0fd1e7a42987e3390463f7587b68db66c2c6`
  - `/tmp/agent-system99/collab-01/green.log` sha256 `6be8a891848feb5139c2e4f93eadc80b1180a0b0f788de5cace4d1e29a49488b`
  - `/tmp/agent-system99/collab-01/regression.log` sha256 `3e0639ac0efe47a1bededcbef56733e74cffa36919b4c328c797e7322779ccbc`
  - `/tmp/agent-system99/collab-01/retest.log` sha256 `b8f0d0a864308cdd0d600da69cd282eed4aaac64f6897199c0617b94ddbe80e2`
  - `/tmp/agent-system99/collab-01/reader.log` sha256 `5f56f1c8afc9fd09f3a5ed874b6e06f7422531cb142a83e000d6a4bdaadc90d9`

### 双 AI 来源调研与整合

前一小步已发布远端 main d0f7766b，树与本地 49ad61f1 一致；本地已对齐远端提交身份。当前新改动基于再次 fetch 后同一版本。
实际读两场演讲的官方文字版、Anthropic evaluator-optimizer 正文及四个固定版本上游源文件。采用/调整/拒绝与运行缺口见 docs/decisions/paired_ai_review.md；没有安装外部套件或启动子 agent。
先写并运行五个既有审核机制的故障注入测试，全部通过（0.179s）；首次即绿，保护现有行为。初次测试发现导入 fixture TestCase 会被重复发现，改为模块导入后准确为五项。
双模型尚未实跑：现有独立上下文核验允许同模型，不能替代可信模型身份检查。模式契约现已写入协作流程并同步两个插件副本；不改变默认单主或人类指南。

本小步定向回归：`python -m unittest tests.test_collaborative_task tests.test_plan_review tests.test_single_main_plan tests.test_repository_task_integration tests.test_plugin_reference_sync -v`，44 项通过（14.106s）；未重跑全库，未修改运行时实现。日志 `/tmp/agent-system99/collab-02/regression.log` sha256 `c1a218b97213710a7bc0d2563cfe42ab419cec8cc1d01844c61cfef195631da3`。新研究与协议整合留在本地提交，尚未推送；整个 COLLAB-01 未完成。

### 2026-11-17：批量运行时升级与回归

新增可选双模型 ReviewSession 协议、可信模型身份/指定审查模型绑定、设计→实现两阶段规格/测试/代码引用及独立需求符合性/代码质量检查。复用原账本与预算，旧协议不降级。新增 23 项合成宿主测试；不宣称真实模型调用或质量收益。GPT 接入使用现有 Codex 安装器，待发布后同步已提交版本。
全库统一回归 `python -m unittest discover -s tests -v`：2170 项，1 failure、8 skipped，402.134s。唯一失败为 prepare CLI 输出新增 collaboration_mode 字段破坏旧精确输出契约；已移除该新增输出字段，模式仍由参数和计划 schema 表达，不改旧断言。Reader 3 项通过，1.706s。日志位于 /tmp/agent-system99/collab-03/。
发布前 fetch 发现远端 f6fdeb20 新增统一项目检查/pstack 验证流程；保留并合并后执行受影响回归。整个 COLLAB-01 的真实模型/对话验收仍未完成。

合并 f6fdeb20 后，修复及关联回归 90 项全部通过（11.799s），包含旧 CLI 精确输出、双模型协议、旧审核、任务文档、插件镜像和 Codex 安装器。统一 project_test.py 在 .venv 标准库环境执行 lint/comments/structure/mutation/regression 五项，全部 pass；注释差异基准显式设为 f6fdeb20，不用自身 HEAD 作空检查。全库首轮的唯一失败已由原测试复验通过；未声称修复后重新运行完整 2170 项。
- `/tmp/agent-system99/collab-03/batch-regression.log` sha256 `bb1385b302d65183a8bcced87fbea1798756bc5fff03062b6c32685f6ea01ed8`
- `/tmp/agent-system99/collab-03/retest.log` sha256 `f33e5376fc4a2a121c00129508bc0c4e7a5aade9e6253de808120621aec7cd2b`
- `/tmp/agent-system99/collab-03/reader.log` sha256 `c5143b0490431e0882fb352aad3e8dd7e53b19d5454f1c562c9770cec478b260`
- `/tmp/agent-system99/collab-03/project-checks/report.json` sha256 `7472bb1986ca6eb6e9366ea778d59b9d4dabc2197e6227db783b9ba5262b969c`
发布候选保留远端统一测试入口和本地双模型/批处理升级，未改人类 guide。待推送读回后同步 Codex；真实双模型宿主调用与审查质量评估仍未完成，不能将安装视为此项通过。

### 2026-11-17：人类优先全流程运行时

实现 agent_runtime.collaborative_flow：人类讨论默认、约十分钟超时双 AI 接续、选择/文本输入、关键决定保留人类、晚到答复与持久恢复、可见决策摘要、串行依赖步骤、环境探测与真实 Skill 正文加载、任务测试直达和有界返修。支持显式可信宿主，复用原模型认证；没有实际模型后端时 blocked，不将合成宿主称为上线。已有保护任务禁止经新入口降级，未知副作用不自动重放。
讨论阶段先准备任务 test；新增 --task 路由复用项目测试入口的目标/源版本和日志绑定。用户明确计时无须精确，验收覆盖正常等待、超时接续、答复停止等待和恢复，不做毫秒级边界。
初始 12 项红灯因模块尚未实现；随后 19 项通过。扩展测试发现共享测试入口抽取函数后漏传 manifest_path，引发三项真实路径失败；已修复。全库首轮 2195 项，4 failures、1 error、19 skips（412.760s）：三项上述路径问题、一项原链接检查把章节锚点当文件名、Reader 缺 fitz。链接检查改用已有 Markdown 解析器；PyMuPDF 1.26.6 安装在 .venv。
修复后关联 84 项通过（12.434s），Reader 3 项通过（1.627s）。任务专用清单 27 项通过；三项代码变异各自有通过对照，并被断言检出：越权委托人类决定、忽略变更测试、正常等待时提前切换。后续 CPU 型号解析补全后同组 27 项再次通过。统一项目清单也通过，含 51 项原回归、33 项已有协作协议、27 项本轮流程和变异；未宣称修复后全库重跑全绿，剩余可选依赖/平台跳过未验证。
实际环境探测到 Python 3.12.14、CPU 环境；未观测到 GPU/驱动或 CUDA toolkit。H20 路由用合成环境检查，不宣称 H20 实测或性能提升。现有工作流/Skill 入口同步到新 CLI 文档；详情展示决策摘要，不是内部 CoT。
期间合并远端 cc6db960 的集中嵌套测试接入，保留其他工作。真实双模型调用、宿主工具权限与隔离、后台监督部署仍需真实接入验收，整个 COLLAB-01 保持未结案。
- `/tmp/agent-system99/collab-04/red.log` sha256 `bec3361f1ed74161dc5df561f4a4044428c0065e3870c633b7c45e9ecbec2f67`
- `/tmp/agent-system99/collab-04/full.log` sha256 `d3481817e902747740f02b45fea8301dad1b391647e9a7472bb07d0fe8fda64b`
- `/tmp/agent-system99/collab-04/final-regression.log` sha256 `be7a39dcefb7fdcaf244432d5fe8e4a7d86f54813be4f89ea806cfe9c6056cb2`
- `/tmp/agent-system99/collab-04/environment-final.log` sha256 `0d6acc34c636e830b51e390073a3c2b6deb4bc88793ca0f26e4c0a625d226746`
- `/tmp/agent-system99/collab-04/reader-fixed.log` sha256 `4e713f4fac3842ce474eff57c054f41c51410a8d5a439d090aac32579d1d41e8`
- `/tmp/agent-system99/collab-04/task-final/report.json` sha256 `9e4c49dd806ad9f6c9885403569de071ce77e49f311ad0000b27a9da91b42f71`
- `/tmp/agent-system99/collab-04/merged-checks/report.json` sha256 `28bc6f36fd77b74845e372365c740b7d70b666f03863ad89715276a7f28869ff`

发布前再合并 a8bf4f4b 的验证成本统计，集中检查再次全部通过。报告 `/tmp/agent-system99/collab-04/remote-final-checks/report.json` sha256 `32e619cf6548cf335bc94c295b5d182ed93ba211315ac5eef514d0e152e0c628`。本轮源代码与文档待普通非强制推送；真实双模型后端仍为明确剩余项。

### Progress v6（2026-11-17）

基于远端 main `1268d6e0`，接入用户独立安装的官方 Codex CLI 0.169.0，复用既有 ChatGPT 登录。实际主模型为 `gpt-6.1-sol`，独立审查模型为 `gpt-6-astra`；身份取自服务端实际 thread/turn/model/provider，回执绑定请求、完整响应、任务版本和预算，禁止同模型降级。配置/回执/依赖与运行产物均在仓库之外，人类 guide 和原五项本地未提交工作保留。

修复原生文件锁、Windows/POSIX 管道半行超时和 EOF、显式切换、取消/并发写前核对、可信代码执行边界、测试超时保留 inflight、旧验收与新计划/外部测试版本混用、控制器 Markdown 导致的伪源码漂移，以及旧同步器在 Windows 上覆盖 Git 文件别名的问题。讨论只发送当前决定与历史哈希；详情只写必要进度，完整历史仍留原账本。最终审查收到报告绑定的完整原始日志；缺失、修改、超预算输出均不能批准。

真实冷启动 COLD-01/02/03 均到达 done；最新 COLD-03 使用当前版本、未忽略任务文档、绑定原始诊断输出，讨论/设计/最终三个审查均批准，无返修。人类输入分支为脚本输入，不冒充真人批准；十分钟切换验收使用逻辑时钟和真实管道，不声称实等十分钟。LIVE-01 的早期失败及 6→8 显式预算扩展完整保留，未换任务清零。继承的 MCP/plugin 在调用线程禁用，最新双模型 probe 实际完成且无工具调用。

最终 Windows 针对性回归 64 项通过，执行前后源文件哈希一致；原始记录 `C:/tmp/agent-system99/codex-runtime-fix-20261117/native-final-regression.json`，日志 SHA-256 `5d0cb91e35201d46f5ad6bea981f4226a92dc36fd5f82a55fea696081f054374`。Linux 关联检查 128 项中 127 通过、1 跳过；验收器 12 项通过。全库早期检查 2212 项存在两项未修改 main 也复现的 dispatch alias / memory 日期失败、缺失可选 fitz，以及已修复的六项生成器 fixture 回归；不报告全库全绿。Windows Bash 专用 fixture 未作为本轮可用能力声明。

不同模型依次提出并落实超时副作用、恢复授权、半行输入、跟踪文档、旧验收版本及原始日志等阻断意见；第五次独立复核九项检查全部 pass、无 findings，approve 本轮限定实现。完整请求/真实身份/完整回复保留 `C:/tmp/agent-system99/codex-runtime-fix-20261117/implementation-review5.json`，不把合成故障测试当真实模型证据。v6 缺后端阻断已解除；未覆盖边界和既有失败保留原状态，不据此宣称其他项目或账号级模式自动生效。

### Progress（2026-11-20）

补齐 Linux 用户级 Codex runtime 配置，实际 app-server 探测完成两个不同模型的只读调用。运行时配置和探测记录保存在用户配置目录。CLI 配置与协作入口共用默认 profile 路径，缺失时提供显式配置和探测入口。已有任务绑定、预算、历史回执沿原机制保留。

Codex 用户级技能加载入口使用同步器校验安装版本、文件哈希和全局指引，输出仍绑定实际目标项目。旧 Claude 加载入口兼容。协作 CLI 的任务验收套件使用工作流仓库中的项目分区；项目既有任务与实验资料的物理迁移需另行保留原受保护路径和私有存储边界。
