# 科研项目协调报告：measurements v2

本轮在 CPU 上实际解析并计算了四条 synthetic CSV 记录，建立了输入版本影响记录及有界依赖计划。未执行新实验、优化实现、独立审稿、作图角色或后台监督。当前代表性协调任务完成；项目的最终图与图文一致性交付尚未完成。

## 输入与计算

`project.json` 明确把当前 `measurements.csv` 标为 v2；CSV 本身没有版本字段，本轮采用该版本声明并绑定 SHA-256。未获得 v1 字节，不报告 v1→v2 数值变化。输入文件和加载的冻结规范哈希见 `loaded_references.json`。数据为合成示例；计算的执行是真实的，但不是性能实验。

定义 speedup = baseline/candidate，延迟降低率 = 100×(baseline−candidate)/baseline；负降低率表示回退。

| workload | scope | baseline ms | candidate ms | speedup | 延迟降低率 |
|---|---|---:|---:|---:|---:|
| small | end_to_end | 100 | 80 | 1.2500× | 20.00% |
| medium | end_to_end | 120 | 100 | 1.2000× | 16.67% |
| large | end_to_end | 200 | 220 | 0.9091× | −10.00% |
| kernel | kernel_only | 20 | 10 | 2.0000× | 50.00% |

若假设三个端到端 workload 各执行一次，总和为 420→400 ms，即 1.05× / 4.76% 延迟降低。这只是明确假设下的算术诊断，不代表生产 workload 权重或统计均值，不把 kernel_only 加入总和。缺重复数、方差、正确性校验、执行配置和 workload 频率，不能补造误差条、显著性或整体优势。

**继续优化的有界判断：**不能采纳“所有端到端 workload 都变快”或“kernel 2× 等于端到端 2×”。在本合成输入内，优先定位 large 回退，并保留 baseline；不建议凭该 CSV 宣称候选全面替换成功。是否值得实际继续投入，仍取决于真实数据、目标 workload 权重及非退化阈值。当前只推进分析、图规划和缩小主张；不运行新实验或改变预算。若日后允许优化，先固定正确性门禁、目标指标、预算和停止条件；这不是本轮已授权实验。

## 版本影响与保留

| 原任务 | keep / invalidate | 本轮动作与证据边界 |
|---|---|---|
| collect done，v1 输入/输出 | 保留历史完成声明；v1 不可作为当前输入 | 不编造重新采集。对现有 v2 文件做字段、单位口径、唯一 workload、正值和 scope 检查；形成 RES-INPUT-v2。v1 文件缺失，不能重验其收集 |
| figure done，依赖 collect/v1 | figure@v1 对当前 v2 用途 stale | 保留其历史 ID，不覆盖。安排 FIG-T-v2 重制并核对所有四条数据、scope、标签、图注；旧图文件未给，不能宣称看过 |
| write todo，依赖 figure/v1 | 取消旧 v1 派发，旧输入绑定失效 | 先完成可独立进行的有界结果草稿；最终段落改绑 v2 分析与 FIG-T-v2，不把未生成的图当依赖已满足 |
| background done，concept@v1 | 数据更新没有声明语义依赖，保留历史记录与 concept@v1 | 现有 concept.txt 可读且与 CSV 无声明依赖，不重跑背景解释。background@v1 成品未给，BG-REUSE 必须 blocked，找到旧成品后核对来源/范围/哈希才准复用 |

v1 原始记录即使旧结论失效也不删除。隐藏依赖不能自动推断：若背景实际引用性能结论，需要补查 manifest 并使其对应部分失效。保留检查的完成只证明影响范围判断，不等于缺失历史成品通过本轮验收。

## 可复用结果草稿

> 在提供的合成 v2 数据中，候选实现对 small 和 medium 的端到端延迟分别由 100 ms 降至 80 ms、由 120 ms 降至 100 ms，对应 1.25× 与 1.20×；large 则由 200 ms 增至 220 ms，增加 10%。kernel-only 延迟由 20 ms 降至 10 ms（2×），其口径不支持推断端到端 2×。这些单条合成记录展示了 workload 相关的收益与回退，尚不足以确认真实环境中的总体收益或稳定性。

这是已写出的有界草稿，不是独立写作角色执行结果；最终写作节点仍等待新图与图注一致性检查。

## 依赖与验收

`task_chain.json` 是本轮静态协调账本，不是假称已经载入 Engine 的执行状态；没有 DB、租约、monitor、scheduler ID 或运行回执。来源清单就是提供的 project.json/task.txt；本轮子角色不另建项目 TASK.md。task_refs 绑定到这两份可见材料的稳定条目，由宿主未来整合到总清单。

已执行：RES-INPUT-v2 输入检查、RES-IMPACT-v2 版本适用性记录、RES-CALC-v2 Decimal 计算、RES-CHECK-v2 另写复算脚本检查、RES-DECIDE-v2 决策及 WRITE-DRAFT-v2 草稿。计算验证为同一执行者的程序复算，无独立 Agent/宿主科研验收，宿主最终验收待上层记录。

计划：FIG-T-v2 仅以 v2 数值制作端到端 small/medium/large 比较主面板，kernel_only 使用单独面板；单位 ms，baseline 与 candidate 用颜色加直接标签，零基线，保留 large 回退，无误差棒。每个标注绑定 results.csv 和输入 hash，保存可编辑脚本、PNG/PDF、图注；实际打开导出图进行最终尺寸与字形/裁切/单位检查，数值与视觉验收分开。现有冻结流程要求作图前加载 figure_shared 与 data_visualization_learning 并形成适合本次简图的设计 brief；本轮没有执行该角色或范文学习，不宣称图验收。WRITE-FINAL-v2 消费该图及 v2 计算，逐项核对数值、scope 与限定措辞；REV-CHECK-v2 作为未来审阅节点检查图文，不把作者自检写成独立科学审稿。BG-REUSE 被缺历史成品单独阻塞，不妨碍图/文支线。

所有计划节点最多一次常规执行与一次局部修复；发现最多两次修订后重新诊断，预算耗尽为未解决。没有新实验、GPU、外部服务、网络或安装预算。图/文实际生产属于后续节点，不在本次协调角色报告中伪装执行。

## 修订审稿意见和 outgoing 投递中断的处理计划

以下是现有依赖计划的恢复协议，**没有收到真实审稿事件，也没有实际发布或 ACK 消息**。例如审稿意见曾把 kernel 2× 外推端到端，后来修订为“large 的 10% 回退未展示”：先读原 finding 的证据、位置、版本与更新内容，保留原 finding ID/不可变原判断，追加修订记录。核验后仅让依赖失效主张的 FIG/WRITE 后代 stale；CSV 与本轮正确的 RES-CALC 可保留。若变更证据/目标版本，则建立新 run，显式迁移未闭环发现，不把旧消息换个版本冒充重试。不同的新问题保留独立 finding，偏好和证据缺口不能自动当作可复算错误。

真实宿主接入后，COM-RECOVER 的顺序必须是：

1. 核验当前 Engine.current()/租约、取消、授权、run 和 recipient 单有效消费者归属；读真实原消息和当前证据。落盘不可变返修意图，包含真实 seq、run/input_version、原 finding ID、原产物 hash、完整 outgoing envelope、精确 needs_revision 回执及原因。event_id 是幂等键，内容变化用新 ID；refs 必须含真实文件与 SHA-256。当前无真实 seq，计划不虚填。
2. status 确认原 delivery 仍存在；原回执若存在，必须与保存的回执完全一致。冲突先交主 AI，不先发布。此读前检查依赖单消费者契约，不是事务锁。
3. publish 保存的同一 event_id/正文/有效 refs；成功或精确重复返回原 seq 后，才 acknowledge 原消息为 needs_revision。路由、输入版本、引用哈希、消息预算或重复 ID 内容失败时，保留 pending 意图，不先 ACK、不修改验收或预算。
4. 发布前中断：重核 ownership/run/refs/receipt 后用同一意图继续。publish 后 ACK 前中断：精确重放 publish 去重，再 ACK；ACK 后重放：保留原精确回执，不改原因。引用或目标变化则保留旧意图，交主 AI 建新 run 迁移。未知副作用先查证；不承诺 exactly-once 或两个操作原子。
5. 责任方实际修复并成功投递修订产物后，才确认其请求；原审稿者按原复验条件检查新产物。关闭记录绑定原 finding ID、新旧 hash 与复验依据。投递、消费、科学关闭分别记录，consumed/needs_revision 回执均不能代替任务验收。

COM-RECOVER/REV-RECHECK 节点当前 blocked（没有真实原消息、seq、host inbox/Engine 归属、审稿者复验），而正常分析/图规划继续。本文证明按规范做了恢复规划，不证明宿主所有 adapter 已更新，更不证明通信恢复路径端到端实测成功。

## 复现与限制

运行 `python calculate.py` 可从固定绝对路径重算；`verify_calculation.py` 独立于生产脚本的算式读取原 CSV，并核对 JSON 与 DAG。结果保存在 results.json / results.csv，实际运行环境与检查记录在 calculation_log.json / verification.json。没有访问 rubric、旧结果、其他角色产物或网络。

本轮未提供旧成品、真实测量/实验配置、独立审稿和最终图；因此只汇报当前协调分析及明确未完成节点，不宣称全项目、论文交付、优化收益验证或后台监督完成。
