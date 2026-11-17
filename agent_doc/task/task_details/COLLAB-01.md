# COLLAB-01

Task-ID: COLLAB-01
Date: 2026-11-17

## Plan
用户授权：先读代码并复述，与用户讨论关键歧义；验收/约束脚本和变异假设先于实现，放 agent_doc/<项目名>/test/；逐步展示代码、结果、新发现并共同确定下一步。本次项目为 agent。不迁移旧项目目录或改人类指南。
计划 v2（2026-11-17，依据用户纠正及“开始 work”）：以真实任务行为验收为主，不实现自报记录分类器。第一小步接入统一协作流程与已有 Skill 路由，测试安装/加载/离线引用和文件故障注入；后续用真实任务对话及工具轨迹共审意图、测试先行与小步实现，再决定是否需要宿主强制门禁。每步展示代码、实际证据、限制与下一步，不把文档/打包测试当模型行为验收。

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
