# [COMM-PERF-01] 通信待处理邮箱索引

Task-ID: COMM-PERF-01
Date: 2026-10-09

## Plan

按 agent_doc/results/comm-pending-index-20261009/plan.json （v2，SHA-256 8d8ae18d169d51a9d4f1553d7c743d1c6c65d050c79a01258bda7f9ef9eb3c37）固定的工作负载和门禁，评估部分索引减少已回执历史扫描；不改变路由、回执、版本、预算或模型语义。独立计划审阅→实现与测量→独立结果核验→同步并普通推送 main。无需新依赖。仅报告本地 SQLite 合成测量；无模型质量或 token 收益主张。

整合补验v3：main并发0498816引入事务usage账本，保留两方修改；按 `agent_doc/results/comm-pending-index-integration-20261009/plan.json` 在同6场景/门槛下比较新main与新增索引，完成独立复核再发布。旧验收只适用于旧源快照。

## Progress

- 已同步 main，读取通信实现、历史验收与空 GUIDE.md；未写指南。已有每小时通信自动化启用，未重建。旧结果不覆盖本轮查询瓶颈，安排新实测。

- 独立计划审查 v1 要求补齐实验细节，v2 在固定6场景/31配对重复/明确收益门槛后批准。实现仅新增 pending-recipient/seq 部分索引，尚未改排序或语义。原始首轮计时与回归部分重叠，保留并标为探索；独立上下文正在无重负载并行下复跑全部6场景。
- 回归854项：845通过、8跳过、1项插件生成引用不同步；在干净基线 bb5bf5b 独立worktree复现相同失败，非本轮引入。本轮16项通信测试均通过。

- 独立全6场景复测与六域验收完成，verification.json为usable-with-scope。默认/大型历史/已清空场景分别3.17×/17.70×/20.20×，小队列不宣称提升；多run的VM工作量退化、写成本及文件增长完整披露。冻结manifest已登记，下一步普通main发布及远端读回。

- 发布前同步发现main新增0498816（事务usage账本）。保留其实现与文档，合并仅文档尾部冲突；未强推。新增整合run独立批准，使用相同工作负载/阈值复测新基线，原manifest/原始数据/验收不改写。已完成25项通信+1项插件同步补验。

- 整合版独立6场景复测完成并验收usable-with-scope；三个门槛2.29×/14.36×/18.78×，25+1补验通过。最终证据与限制见 `agent_doc/results/comm-pending-index-integration-20261009/report.md`，该结果已登记；原始版本仅作历史证据。

- 发布方式：终端git push缺少凭据，改用已连接GitHub Git-data接口；同一已验收树，expected_sha=0498816、force=false，最终提交身份以main实际回读为准。原每小时通信任务保持启用。下一轮优先跨run查询选择性/真实模型质量成本A/B；不宣称全局或模型端到端加速。

- 最终协调：expected_sha发布时main已到ab6cc59，已实现仅索引名称不同的等价候选。保留现有源码/测试/benchmark，不重复索引；本次只合入独立研究与测量证据，当前程序等价和针对性回归单独复核。旧manifest/record维持历史，不假装source哈希仍与currentmain一致。

- 并发去重复核通过：当前ab6cc59通信实现仅索引名差异，其源码/测试/脚本原样保留；独立运行现有24项通信测试全部通过。本次main提交为证据补充，不重复声称第二次实现加速。原25项对应归档测试；精确测试字节另存test-communication-reviewed.py。
