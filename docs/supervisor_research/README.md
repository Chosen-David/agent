# 自动任务链监督：研究与设计索引

Run `supervisor-upgrade-2026-10-03`。起点为 pull 后 `e72e0cfc0d9223f5d5b0dc273f3a5d41a12c5e3b`；原有监督续跑只是规范与 TEST_ONLY 合成规则示例，没有持久执行器。保留原决策、低风险默认和 baseline-first 协议，补可运行核心，不重复创建权限规范。SGLang 不在修改范围。

## 十篇原始论文与深读证据

全部读取固定版本原始全文中的方法、算法、关键实验和限制；不是搜标题。定向深读不表示逐字读完所有附录。完整定位和具体结果分别见 [A组笔记](papers_a.md)、[B组笔记](papers_b.md) 与 [A来源锁](papers_a_sources.json)、[B来源锁](papers_b_sources.json)。终端下载 PDF 受代理403限制，浏览器原始 PDF/HTML 正文读取成功；未伪造本地PDF哈希，也未提交论文全文或私密数据。

| 论文 | 固定原始来源 | 用于设计 | 不支持的主张 |
|---|---|---|---|
| ReAct | [2210.03629v3](https://arxiv.org/pdf/2210.03629v3) | 动作—观察闭环、重复失败诊断 | 不保证长期任务完成 |
| Reflexion | [2303.11366v4](https://arxiv.org/pdf/2303.11366v4) | 保存失败反馈、独立验收、防假阳性 | 反思不等于持久化或无限重试 |
| Tree of Thoughts | [2305.10601v2](https://arxiv.org/pdf/2305.10601v2) | 有预算的分支探索/回退 | 不能把模型评分当验收 |
| LLMCompiler | [2312.04511v3](https://arxiv.org/pdf/2312.04511v3) | DAG规划与确定性就绪分发分离 | 并行加速不证明恢复/授权安全 |
| Plan-and-Solve | [2305.04091v3](https://arxiv.org/pdf/2305.04091v3) | 显式拆解、输入/依赖 | 静态计划不等于自治执行 |
| AutoGen | [2308.08155v2](https://arxiv.org/pdf/2308.08155v2) | 可插拔工具/角色与终止边界 | 终止token不等于done |
| MetaGPT | [2308.00352v7](https://arxiv.org/html/2308.00352v7) | 类型化产物、依赖就绪、有限修复 | 本文也承认检查点困难 |
| AgentVerse | [2308.10848v3](https://arxiv.org/pdf/2308.10848v3) | 诊断目标—状态差距 | 多Agent共识不是正确性证据 |
| SWE-agent | [2405.15793v3](https://arxiv.org/pdf/2405.15793v3) | 可测接口、工具反馈、测试验收 | 自动提交/预算耗尽不等于成功 |
| Voyager | [2305.16291v2](https://arxiv.org/html/2305.16291v2) | 验证过的程序复用、失败反馈 | 换探索目标不完成原任务 |

论文数字仅作来源分析，未运行其模型实验。10篇都不证明本系统的租约、重启或定时间隔；这些性质由下面的工程契约和本地故障测试独立验证。

## 开源实际实现和 SKILL 决策

[详细源码阅读](opensource.md) 与 [完整commit、许可证、28文件SHA/读取范围](opensource_sources.lock.json)。LangGraph 借鉴 checkpoint/write identity；Temporal 借鉴活动/控制分离、取消与未知副作用核实；APScheduler 借鉴到期/租约/事件唤醒；Superpowers 读取实际 SKILL 和 task-done 脚本，借鉴证据门禁与ledger。均为 MIT；本次是机制复用与自有实现，未复制实质源码或技能全文，不引入运行依赖。

选择标准库 SQLite + 可信宿主 Handler + 显式 Scheduler 接口，是授权/依赖范围下的决定，不声称优于成熟分布式服务。Temporal 需要服务、worker和运维授权；LangGraph 不替代scheduler；当前 APScheduler HEAD 预发布；Superpowers Markdown 不提供后台运行。适配/维护成本和不采用部分在源码笔记中逐项说明。

## 实现契约与取舍

实现：[core.py](../../agent_runtime/core.py)、[scheduler.py](../../agent_runtime/scheduler.py)、[CLI](../../agent_runtime/__main__.py)。使用/宿主授权边界见 [工作流](../../workflows/task_supervision_workflow.md)。

| 要求 | 实现机制 | 验证入口 |
|---|---|---|
| 自动规划 | 主AI入口主动生成 task-dag/v1；确定性校验未知依赖/环/预算 | validate、plan fixture |
| 状态机 | todo→doing→verified done / retry todo / blocked / failed；cancelled独立 | Engine.tick、状态断言 |
| 真完成 | Handler.verify、hash证据、失效沿依赖传递、全节点成功 | evidence/refusal/invalidation tests |
| 持久恢复 | SQLite事务，plan immutable，任务/事件/monitor/journal落盘 | 真DB重开/worker terminate |
| 幂等/租约 | 稳定key、原子领取、token+expiry提交fencing；未知非幂等先核实 | 真多进程与合成时钟过期 |
| 监督时间 | ETA/risk + no-progress指数退避 + clamp；change唤醒不突破下限 | policy/backoff/wake tests |
| 授权/取消 | 默认拒绝host callback，取消写入账本拒绝迟到结果 | blocked独立分支/cancel race |
| 后端诚实 | capability + create ID + live readback；无服务blocked | local进程与fake adapter分开 |
| 收尾 | done/failed/cancel停止本链monitor，blocked退避保留原因 | converge/owned-monitor tests |

核心一次tick领取一个节点以控制事务和预算；独立支线在后续tick或其他worker继续，未实现论文的流式函数并行优化，不宣称速度提升。DAG校验当前最坏 O(V²+E)（上限1000节点），状态JSON每次事务 O(V+E)；证据核查成本额外取决于产物总字节数（内置每文件16MiB上限）。此范围下优先明确正确性与零外部依赖，大图/高吞吐应换经验证的后端。

数据库是单机磁盘账本，不是权限沙箱；同权限恶意代码可改库。外部副作用 exactly-once、任意进程强制取消、多机/NFS、断电磁盘丢失恢复、LLM规划质量和生产SLA均不在本次保证内。宿主需提供可信动作接口与当前批准；仓库升级不部署服务。

验收记录与实际日志见 [测试边界](../task_supervisor_validation.md)。独立 [review](review.md) 保留发现与修复复核，不把首版缺陷藏起来。
