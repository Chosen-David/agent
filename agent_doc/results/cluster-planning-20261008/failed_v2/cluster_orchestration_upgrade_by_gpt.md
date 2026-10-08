# 多机多卡任务编排升级_by_gpt

本轮给主AI新增可执行的**单波次资源放置规划入口**，将任务依赖、机器/卡适配和输入传递分别核对。它输出建议，实际资源预留、跨机执行和网络传输尚未接入用户机器。

## 改动及实际入口

`prompts/orchestrator.md` → `workflows/cluster_orchestration_workflow.md` → `scripts/plan_cluster.py` → `agent_runtime.cluster_planning.plan_wave`。

- 宿主清单含机器ID、整卡UUID/型号/单卡可用显存、CPU/RAM/磁盘、能力、双向链路和hash绑定cache。
- 依赖已验收才进入当前波次；整组GPU与每节点容量检查。支持单机单卡/多卡、同型跨机多卡组和单机CPU任务。
- 输入cache命中免传；否则生成源/目标/hash/byte与估计传输秒数。接收端提供独立流式文件校验CLI。
- 按明确优先级和有限候选代理排序；界限耗尽与不可行分开。建议不包含shell、凭证或后端安装操作。
- 三类通信分离：控制状态走可信后端，文件走经授权数据通道，张量collective走作业内部专门后端。SQLite消息箱保留本地语义。

实际科研Skill快照及既有Engine领取算法未修改；本轮选择通用主入口按需加载，既有插件引用同步检查通过。没有把大量新知识塞入每次上下文。

## 研究依据和取舍

检索2026-10-08，准确版本、状态与阅读范围见 sources.json。

| 来源 | 本轮采用 | 不作的推断 |
|---|---|---|
| NCCL M2N v1，2026-10-05预印本 | 先明确数据布局，再由拓扑决定路由 | 未复现256GPU结果，也未部署其API |
| Multi-Model LLM Schedulers v1，2026-05-19，正文列MAIN2026 | 按模型和硬件校准运行/重载估计 | 单请求PCIe观察不能代表并发机群 |
| SkyPilot官方Agent博客，2026-04-09 | 统一机群清单、复用专门后端 | 未安装凭证、申请云资源或部署服务 |
| Ray当前官方文档 | 逻辑准入与物理隔离区别 | CUDA_VISIBLE_DEVICES不是完整基准隔离 |
| MultiKueue当前官方文档 | 管理端/执行端分工与job状态 | 文档存在不证明本项目Kubernetes就绪 |
| NVIDIA拓扑博客，2025-07-14 | 双向互联/拓扑证据 | 旧工程文章未包装成2026新论文 |

ShuntServe检索摘要可得，但正文访问错误，未作为已读论文或性能依据。原始URL均在sources.json与工作流中。

数学卡 `math.discrete-budget-allocation@1` 被明确拒绝直接套用：共享GPU、链路和整组准入使成本耦合。实现采用有限启发式，不声称最优调度。快照内容量检查也不等于实际租约或端到端收益。

## 实际测试与证据

本地CPU合成fixture；种子标记0，确定性无随机生成。冻结命令与日志在 execution.json。

| 检查 | 实际结果 | 范围 |
|---|---|---|
| 新规划器约束测试 | 18项通过 | 就绪、显存、卡型、链路、整组、容量、cache、过期、枚举界、文件/FIFO等 |
| 仓库全量 | 831项运行，OK，跳过8 | 程序/文档回归；不是831项模型任务 |
| reader | 3项通过 | reader应用回归 |
| 合成清单CLI | 3个放置，join因依赖未验收阻塞 | 仅JSON规划，未submit |
| 插件引用一致性 | 通过 | 既有分发快照未变 |

合成多机组分配large-a/large-b各一张H100；两个独立任务使用剩余卡。没有真实H100被查询或占用。48GiB单卡任务不能靠两张24GiB卡容纳，多机组缺一个方向的RDMA链路即拒绝；其失败不占半组卡，不阻塞独立可行任务。

独立结果审查以 manifest_v2.json 和 validation_plan_v2.json 绑定实际代码/输入/日志；复核结果见 independent_review_by_gpt.md / independent_validation.json。当前本文记录生产观测，正式可用性以独立回执为准；提交状态另见publication_receipt.json，不由生产者自报通过。

## 成本、限制和下一步

没有真实模型/网络/GPU性能或token账单实测。本轮省token策略是固定ID/hash引用、紧凑建议、按需读取异常和稳定poll不调LLM，收益仍需同模型/工具/预算A/B。

规划器不保证全局最优、公平等待、完整卡内拓扑、网络无拥塞或makespan；同波次共享输入未预测去重。MIG/分数GPU/CPU多机未支持；直接并发调用不提供跨进程资源预留。整组预留、环境版本、提交幂等、未知状态reconcile、取消终止确认与数据不可变发布仍需真实可信adapter。

后续在实际清单/既有Slurm、Ray、Kubernetes或SkyPilot后端确定后，按工作流执行单卡→同机组→跨机组→故障恢复，比较顺序/既有后端/新规划的质量、makespan、GPU-hours、实际字节和模型token。此次未修改SGLang、人类guide或原有未提交文件。
