# [FIG-QA-01] 绘图验收绑定

Task-ID: FIG-QA-01
Date: 2026-10-08

## Plan

### 目标与验收
改进通用绘图验收，区分科学语义、几何技术、阅读美学和最终载体；资产用途、文件版本、承载页及实际嵌入尺寸必须对应。通过直接契约测试、分发同步和独立实际差异审核后，整合最新 main 并非 force 发布与读回。静态规范通过不代表实际视觉质量提升。

### 范围与方法
只修改 figure_shared.md、diagram_workflow.md、直接契约测试及七份既有生成副本。保留人类 guide、SGLang、历史任务及失败；不公开私稿、私有数据或用户反馈原文。按用途配置可读性阈值，不建立统一“顶会”分数。计划审核与结果验收使用不同实际上下文。此文档于已发布实现后补齐治理记录，不伪称事前已登记 TASK 或已部署双主运行时。

### 既有证据取舍
查阅结果库、COH-T25/COH-T26 详情及历史架构验收报告。旧有限样本通过不支持当前视觉提升结论，故不复用为新质量数据；保留旧记录，不以无关知识候选恢复阻塞本工作。

## Progress

### 实现、独立验收与测试
实现提交 `0711fe78d1a2a8d724357d8dc0be5ef0faf16fb2`。加入 asset_id/usage、文件哈希与页码/比例绑定、用途字号和线宽核验、机制视觉编码及可定位独立读图要求；负例拒绝资产替代、版本错配、错误端点和技术结果冒充视觉通过。

独立计划审核 approve；另一上下文结果验收 usable-with-scope。结果审核指出两处旧论文尺寸措辞与用途区分冲突，已修正并独立复验关闭。规范完整性/分发一致性验收通过，不是实际图的美学验收。

全仓 851 项中 850 通过、1 项真实 tmux opt-in 跳过；Reader 3/3；末次措辞修订后针对性 16/16，并独立复跑通过。全量回归在末次两处措辞修订前完成，修订未改变代码；未重复无影响全量测试。引用同步及 diff 检查通过。未运行新绘图、模型质量 A/B 或后台部署。

持久证据：[源码绑定与验收摘要](../../results/figure-review-binding-20261008/verification.json)、[全仓摘要](../../results/figure-review-binding-20261008/full-regression.txt)、[Reader摘要](../../results/figure-review-binding-20261008/reader-regression.txt)、[末轮契约摘要](../../results/figure-review-binding-20261008/final-contract.txt)。仅保留隐私审查后的简洁输出；临时完整日志哈希用于标识，完整日志不承诺持久可用。

### 发布及边界
提交前及推送前 fetch/整合 main；普通推送上述实现成功，git ls-remote 与父线程 GitHub 独立读回 SHA 一致。父线程查询该 SHA：check-runs=0、statuses=[]、rulesets=[]；combined pending 不代表 CI 正在运行。classic branch protection 未核实：本地 gh API 返回 Forbidden，父线程连接也返回 403 Resource not accessible by integration。不能推断无保护或声称必需 CI 已通过，不绕过或扩大权限。

本次补录仅新增唯一 TASK 条目、详情及持久摘要，不改变实现。补录提交身份以这些文件的 Git 历史为准；补录自身普通推送及远端 SHA 读回由本次交付报告记录，避免自引用提交哈希。classic branch protection 的配置保留未核实边界，不阻塞本次已完成的普通推送，也不宣称 CI 通过。实际视觉改进需要另行实际成图评估，本轮未作该承诺。旧未完成任务保持原状态。

补录独立复核：原结果审核者核对源码/摘要及原日志哈希、TASK 旧内容逐字保留、唯一 ID、链接和隐私边界，结论 usable-with-scope，无阻塞错误；本次纯文档追加无需重复全量测试。
