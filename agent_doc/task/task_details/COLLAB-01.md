# COLLAB-01

Task-ID: COLLAB-01
Date: 2026-11-17

## Plan
用户授权：先读代码并复述，与用户讨论关键歧义；验收/约束脚本和变异假设先于实现，放 agent_doc/<项目名>/test/；逐步展示代码、结果、新发现并共同确定下一步。本次项目为 agent。不迁移旧项目目录或改人类指南。
计划 v2（2026-11-17，依据用户纠正及“开始 work”）：以真实任务行为验收为主，不实现自报记录分类器。第一小步接入统一协作流程与已有 Skill 路由，测试安装/加载/离线引用和文件故障注入；后续用真实任务对话及工具轨迹共审意图、测试先行与小步实现，再决定是否需要宿主强制门禁。每步展示代码、实际证据、限制与下一步，不把文档/打包测试当模型行为验收。

计划补充 v3（2026-11-17）：用户要求 AI–人类 / 双 AI 模式，并授权调研演讲和开源实现后整合。当前小步为来源核查、模式/审查契约及已有 API 故障回归；不启用第二模型或自动迁移历史保护计划。

计划补充 v4（2026-11-17）：用户授权直接升级，并改为批量实现后统一测试、集中修复，完成直接推远端 main。实现可选双模型协议、绑定两阶段任务文件与真实宿主身份；默认人类模式保留。GPT 接入复用本库 Codex 安装器，同步已提交 Skills 和受管指令；配置同步与真实模型运行分别报告，不修改人类指南。

## Progress
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
