# [EXP-CONTAM-01] 已证实实验污染的停止、隔离与修复恢复

Task-ID: EXP-CONTAM-01
Date: 2026-10-11

## Plan

用户明确授权：主 AI 证实缺陷影响正在运行的实验，立即停受影响作业，即使接近完成；清理污染有效结果/排行榜/缓存引用，修复验证后新身份重跑。只改 agent；不运行模型、Claude、GPU或新增付费；测试与独立审查后普通推 main。源码/配置/数据/运行/实际作业必须绑定，怀疑不得误杀，隔离可恢复，停止失败阻止清理/重跑。

复用 result_validation / ResultStore 的消费者门禁及 project_docs 写入保护。新增窄可信宿主 API，不另造调度框架，不用整链 Store.cancel 代替单作业停止。主 AI/maintain 适配器提供真实确认、授权、精确作业停止与完整引用闭包；缺外部控制能力明确 blocked。主作者维护此任务与相关源码/测试/契约/生成镜像/CODEMAP。独立审查只读。

验收：确认/未证/无关作业、部分结果、缓存失效、停止失败/部分移动恢复、修复验证/新身份，以及现有消费者门禁。CPU 实际子进程停止验证；完整 unittest、reader 与同步检查。独立检查之后刷新远端，整合并发、复测、只暂存直接相关文件、非 force 推送并读回 SHA/内容/CI。没有必需证据不标完成。

### 授权范围修订：发布必需的已有文件打包

后续用户明确授权：仅通过现有 sync_plugin_references.py 把 canonical advice_meetings.md 按既有相对路径分发到消费该链接的独立技能，并刷新 project_docs.py、coverage.json、learning_state.json 镜像；不改 canonical 科学内容、知识引擎、旧查询或测试，不重做 advice 框架。此前六条基线失败现在是本任务获准处理的直接发布依赖。仍需独立审查、完整回归、刷新整合 main、非 force 发布与远端/CI读回；若失败更新同一 Library 候选。

## Progress

2026-10-11：初始 work checkout 干净，fetch 后 fast-forward bcfb0ec → f11cc4b。未发现 checkout .agents/skills；只读相关源码 Skill，guide/GUIDE.md 为空。唯一索引无同主题任务，相关历史检索 `experiment contamination invalidation stop` 实际扫描141轮，词汇候选为语料/通信旧结果，任务与运行身份不匹配，不复用。部分旧记录缺失如实保留，不修无关档案。现有 TASK 未完成历史工作不冒领。

能力边界：本会话未部署 tmux/受管监督器或可信 plan-review runtime adapter；使用当前工具完成授权源码工作与真实独立子代理审查，不伪造受管服务ID。新模块不启动作业；外部 stop 与资源授权由已有可信宿主提供。知识科学迁移不适用：这是既有运行时正确性控制，不新增科学/性能主张。

最终候选：污染回归17/17，独立上下文 `/root/review` 实跑17+79通过并记录源码SHA；main入口5/5、实验10/10、reader3/3。全仓1008项出现3 failures/3 errors/1 skip；相同origin/main的干净独立worktree991项复现完全相同失败，均为既有知识镜像及包内advice_meetings缺失链接。本次不维护这些无关文件。分支保护/必需CI读取Forbidden，提交状态接口statuses为空不作通过。证据见 `agent_doc/results/contamination-20261011/report.md` 与各log。任务未完成；按用户后备要求保存本地可续候选，不推main，不宣称部署外部作业控制。

下一步由主AI在基线分发检查修复、必需CI可见后恢复：fetch整合最新main，复核独立源码哈希并复测，通过后只暂存本次文件、非force推main及远端内容读回。保留停止失败/归档失败与边界，不改SGLang，不运行模型/Claude/GPU或新增付费。

后续收尾指令：重新fetch仍是f11cc4b。六条测试记录及源码提交归因见 `agent_doc/results/contamination-20261011/blocker-diagnosis.md`；证实为此前无关知识/任务解析/advice分发工作，而非本次五份引用的缺口。不扩大修改范围或放宽测试。运行时代码未变，既有独立审查哈希保持；明确没有内置远端/多rank/SGLang停止适配器，仅真实测试适配器验证单个受控Linux子进程。按用户要求将完整源码快照、补丁、日志、SHA身份和恢复步骤保存为新的Library候选；收到上传回执与下载字节核对后报告ID/版本。main仍不得发布。

按最新收尾指令实际整合897c032：合并构建044201214ee371c4ad3505d851aa1c2d346328fc；TASK唯一追加冲突保留双方条目及远端原始字节。新全仓1008项与clean main991项均同样3 failures/3 errors/1 skip；污染17/17、结果79/79、reader3/3通过；代码哈希仍匹配既有独立审查，没有新模型调用。完整新日志/测试归属/六条精确失败在 `agent_doc/results/contamination-integrated-20261011/`。无关源代码和测试未改、main未推，原Library身份以版本0保护更新整合后的完整候选；发布仍待基线及CI门禁恢复。

发布依赖收尾：用户明确授权后，仅扩展既有同步映射并生成16份导航、刷新3份镜像；canonical文档/解析器/知识未改。ae80bfaff通过全仓1008项（1项opt-in跳过）、reader3项、sync检查和独立复审。此前阻塞记录现为历史；GitHub app成功读取main保护与rulesets，未配置必需检查。证据见 `agent_doc/results/contamination-release-20261011/`。普通推送与远端读回待完成。
