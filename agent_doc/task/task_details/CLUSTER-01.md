# [CLUSTER-01] 多机异构 GPU 编排升级

Task-ID: CLUSTER-01
Date: 2026-10-08

## Plan

按本次用户要求，调研截至 2026-10-08 的原始论文、官方博客/文档，实现机器/卡清单、依赖就绪任务的有界放置规划、跨机数据契约及主 AI 按需入口。仅规划和本地 CPU 验证；不访问服务器、不安装调度后端、不修改 SGLang。方案、允许写入、预算和验收固定于 agent_doc/results/cluster-planning-20261008/plan_v1.json；生产 → 独立验收 → 发布合同在 dag_v1.json。保留未提交文件。

## Progress

方案v1经独立审核要求补充证据后修订为plan_v2；独立方案审核v2通过。最终生产/验收/发布合同为dag_v4，manifest_v4 SHA256 1386a9e7947f5b6bbafda0accd559dc80aedb438b59b4910bde099eac2e0b644。Plan正文保持不变；上述版本与新增边界验收没有放宽要求。

完成资源清单、有界依赖就绪放置、整组GPU/CPU/RAM/磁盘准入、hash数据交接、流式文件校验与通用主AI入口。检索日期2026-10-08；近期NCCL M2N v1、multi-model schedulers v1及官方博客/文档的版本和实际阅读范围保存在sources.json。复用math.discrete-budget-allocation@1并拒绝错误套用：共享GPU/网络/整组准入导致成本耦合，不满足独立可加菜单条件；当前启发式不声明最优。

独立代码审查发现超大JSON整数溢出；后续边界检查发现深度10000 JSON解码递归溢出。分别保存failed_v2/failed_v3失败代码与日志，v2/v3回执失效。v4修复后主方和独立方均重跑：专项20项、全量833项OK（跳过8）、reader3项；独立另有14项判别案例。原始命令/时间/日志分别execution_v4.json和independent_execution_v4.json。已公开并用于修订的案例均属于回归，不再算未见测试；未做模型实测。

独立验收usable-with-scope，canonical receipt SHA256 96c47a0daa3cc8608a1ecdd4baadc2797b514beb700683f030d6d76872ced78a；root依据实际独立调用完成事件核对所有绑定，host_validation_gate.json与record.json保存限定范围。直接本地宿主审核，不冒充已部署Engine认证。稳定Plan与人类guide未改；完成后更新Progress使早期全文件TASK证据成为历史，当前结果代码/数据绑定不变。

已直接发布main 76914d32195128a764868f59ddcb4355eac3b9d9，并fetch/ls-remote核对远端SHA与本地树da67790186dcc55a1a28c4a0f7270b14d6931250一致；publication_receipt.json记录实际观测。后续提交仅登记此回执与任务关闭。仅本地CPU合成资源规划与文件校验；未访问用户机器、占用真实GPU、启动远端作业，也未修改SGLang。没有吞吐、模型质量或token节省实测。后续需可信宿主整组原子预留、环境/链路校准、submit/poll/reconcile/cancel与独立数据验收，执行真实单卡/同机/跨机/故障实验和同预算A/B。下轮知识建设先检索已覆盖主题，保留新的未用于开发验收；不得把本轮结构/回归通过当作数学推理模型能力提升。
