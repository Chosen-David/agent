# 主 AI 的多机多卡编排

适用：多个实验/算法/工程任务在多台授权机器的异构GPU上运行。先读 [因果编排](causal_task_orchestration_workflow.md)、[任务监督](task_supervision_workflow.md)、[通信](agent_communication_workflow.md) 和当前项目指南。身份、授权、独立验收仍由既有任务链控制，不增加后台调度服务。**单卡独立任务大群（扫描/评测/消融，允许同卡分数槽复用）见 [单卡独立任务扫描编排](single_gpu_sweep_workflow.md)**；无后端环境的接机、派单、回传与收口运维规程见 [GPU 资源池运维 playbook](gpu_pool_operations_playbook.md)。本文覆盖 gang job（多机同构整组 + RDMA）。

## 已实现入口

完整checkout提供 `agent_runtime.cluster_planning.plan_wave` 和 `scripts/plan_cluster.py`：计算**一个依赖就绪波次的放置建议**，不预留资源、不连接SSH、不安装后端、不传输或启动作业。主AI从实际Engine状态及独立结果验收取得已完成ID，先调用规划器，再交可信执行后端；规划器不改Engine.claim轮转，也不授予执行许可。纯Skill缺checkout时报告实际接口缺口，不虚构CLI。

```bash
# 合成清单回放，时间1001仅用于fixture，清单中没有真实服务器/模型
python /absolute/agent/scripts/plan_cluster.py plan --input /absolute/agent/examples/cluster_planning.json --now 1001 --max-inflight 8 --candidate-limit 1024
# 真实清单不传--now；工作节点不得用它伪造新鲜度
python /absolute/agent/scripts/plan_cluster.py plan --input /project/.agent-runs/run/fleet-input.json
# 接收端对已暂存的实际文件校验，参数来自冻结manifest
python /absolute/agent/scripts/plan_cluster.py verify-file --path /host-owned/staging/input --sha256 ACTUAL_SHA256 --size-bytes ACTUAL_BYTES
```

CLI仅输出JSON，不把计划字段当命令。有效但无法放置仍为 `advisory-only`，列 `blocked`；退出0不是任务成功，无效输入退出2。输入限2MiB且拒绝重复键；Linux普通文件，不读FIFO/设备。文件校验流式SHA-256、大小、显式byte cap及修改时间检查，拒绝符号链接；不会下载/发布文件，无法防止同权限写者在校验后改动。

## 真实接口与资源约束

顶层严格是 `inventory/tasks/verified_task_ids`，见 [完整合成JSON](../examples/cluster_planning.json)。单位整数byte、秒、byte/s，GiB=2^30 byte；不混GB/GiB或Gb/s。未知字段拒绝，不接受shell、账户、自动安装字段。

| 对象 | 字段与语义 | 必需条件 |
|---|---|---|
| 快照 | `cluster-inventory/v1`, observed_at, valid_for_seconds | 最多300秒，未来/过期拒绝；可信宿主当前探测，不猜历史机器 |
| 宿主 | host_id, cpu_slots, ram_bytes, disk_bytes, capabilities | 剩余可规划容量，已扣外部作业/系统余量；快照不是租约 |
| 卡 | uuid, model, usable_memory_bytes, available, fabric | 全局唯一整卡UUID；单卡显存适配；MIG不支持，不能重复计算父设备 |
| 链路 | source, destination, bytes_per_second, latency_seconds, transport | 有方向且实际测量或明确估计；不推断反向速度 |
| 输入 | artifacts[id]={sha256,size_bytes,source_hosts}, host.cache[id]=sha256 | 源cache必须匹配hash，正确目标cache才免传输；实际字节与可读性由发送/接收端复验 |
| 请求 | nodes, gpus_per_node, gpu_models, gpu_memory_bytes, gpu_fabric | 每节点同卡数、同卡型/fabric；跨机须全部distributed能力与每对双向RDMA达阈值 |
| 容量与估计 | 每节点CPU/RAM/scratch、required_capabilities、artifacts、runtime_seconds、startup_seconds | 显式每卡内存；按模型/形状/dtype/软件/宿主校准运行估计；无宿主估计不放置；暂存另扣磁盘 |
| 就绪 | task_id, depends_on, priority；外部verified_task_ids | 可信控制器给出已验收可消费的ID，不能用工作节点自报pass产生此集合；已完成ID不再调度 |

CPU-only当前单节点；多卡整组可行后才扣波次资源，失败不占半组。GPU UUID在本波次最多分配一次，CPU/RAM/磁盘总量检查。两张24GiB不能相加成单卡48GiB。清单限32宿主、每宿主64卡、256任务/输入。

任务按priority降序、ID排序；每宿主同型号/fabric组选首批适配UUID，再比较有限宿主组合。候选超限返回 `search-limit`，区别于 `no-feasible-candidate`，不拿截断搜索宣称不可行/最优。没有完整GPU内互联搜索、公平等待保证或全局关键路径优化。大规模使用专门后端，不能无限提高枚举上限。

两个规划进程可能建议相同卡：可信后端必须重新核验并**原子准入整组**，回读实际UUID/reservation/job ID后才启动。逻辑资源和CUDA_VISIBLE_DEVICES不能单独证明物理性能隔离。planning lease、Engine节点lease和实际GPU作业lease各有语义，不能控制lease到期便释放仍运行的卡。

## 数学模型与边界

先检查依赖和硬容量约束，再排序可行候选。就绪任务i在H_i上，每宿主g_i卡；并发CPU/RAM/暂存总需求不超清单余额，每卡可用显存≥单卡需求。整组还需卡型/fabric/能力和每对有向链路适配。不能将不满足显存或互联改成排名惩罚。

当前耗时代理为

\[
\widehat T_i(H_i)=\max_{h\in H_i}\widehat t_{ih}+t_i^{start}
+\sum_{(a,s,h)\in\mathrm{missing\ inputs}}(\ell_{sh}+B_a/b_{sh}).
\]

每个缺失输入选估计最快已登记源，staging按串行估计，cache命中免传输。量纲是秒；未建模跨任务链路争用、协议/I/O、GPU collective、排队，**不是完整makespan或延迟证书**。同波次共享输入未预测去重，可能多算磁盘/生成重复转移意图；真实cache发布后须刷新下一轮快照。只支持点对点文件意图，张量切片/reshard交给专门后端。

已读取 `math.discrete-budget-allocation@1`，拒绝其精确DP保证的直接迁移：共享卡/网络和整组条件破坏固定可加菜单。反例：将通用任务先放到唯一适配大模型的卡，会阻塞只适配该卡的任务；每次选最快不等于全局最优。可行性通过仅支持快照内约束，不证明真实性能或精度提升。

## 三种通信平面

| 平面 | 通道/内容 | 验收责任 |
|---|---|---|
| 控制 | 可信后端API：任务版本、job ID、lease/fence、取消和心跳 | 主AI唯一DAG；消息认证/幂等；SQLite/Mailbox只本机，不放共享NFS充当跨机服务 |
| 文件 | 后端对象存储/共享只读存储/明确授权点对点传输；manifest/hash | 传前权限检查；接收端暂存→大小/hash→原子不可变发布；半文件不入cache；hash不替代身份/权限 |
| 张量 | 作业内torch.distributed/NCCL等，显式world_size/rank/rendezvous/backend | 全组启动/失败协调、collective顺序和数据划分检查；不经Agent消息传权重/KV/张量正文 |

主AI只读紧凑候选、blocked原因、任务/快照hash与必需结果ID；大模型/数据和每rank长日志不进入对话。沿用Mailbox.prepare_context消费者依据闭包和真实tokenizer硬限，变化事件合并，稳定poll不调LLM。省长度不能删必要假设/反例；本轮未实测模型token或质量收益。

## 执行、恢复和实际实验

以下是宿主适配要求，**尚不是已实现跨机执行API**：

1. 宿主采集UUID/驱动/框架/容器digest、余量、在途作业及网络/互联证据；冻结模型/数据/形状/dtype/种子/分片。主AI仅使用当前授权机器。
2. 实际任务链的审核/授权仍有效；按 `(run_id,task_id,plan_hash)` 幂等整组预留，回读物理分配和job ID。实际分配改变须核对已审核弹性范围；建议不是allocation。
3. 校验暂存输入后全组submit，随后poll同一job；提交超时unknown先reconcile，不启动副本。取消只作用自有作业；失联不等于终止，确认全组退出才释放。
4. 输出固定manifest/分片覆盖/版本/样本数/原始日志，producer→独立verify_experiment_result→consumer；join缺一份保持未完成。OOM不能默改dtype/长度/样本，失败只重试受影响分支；GPU利用率100%不证明进度。

选择已有后端：Slurm沿用allocation/job状态；Ray考虑placement groups；Kubernetes多集群考虑MultiKueue，跨基础设施考虑SkyPilot。锁定版本/权限后验证，不自动安装、迁移现有作业或授予云权限。已有后端真正支持的API才进入adapter，不能把本节步骤包装成已部署接口。

真实验收依次单卡→同机两卡→两机组→网络中断/unknown提交/重启；检查物理UUID、每rank样本/collective次数和结果等价。固定模型、工具、任务与资源预算，对比原顺序策略、后端原策略和新规划，记录排队/加载/暂存/计算/验收/makespan、GPU-hours、字节、失败重做、主AI实际tokens及质量。吞吐与排他单作业延迟分开，不以模拟清单宣传多机加速。

## 调研和本轮证据

检索2026-10-08，版本/发表状态/实际阅读范围见 [sources.json](../agent_doc/results/cluster-planning-20261008/sources.json)。

- [NCCL M2N v1](https://arxiv.org/html/2610.07516v1)，2026-10-05预印本：源/目标布局与拓扑共同决定字节路由；采用布局/传输分层，未复现其256GPU结果或安装其API。
- [Multi-Model LLM Schedulers v1](https://arxiv.org/html/2605.19593v1)，2026-05-19，正文列MAIN2026：单请求offload/preemption启发按模型/硬件校准；不能推断本项目并发机群重载瓶颈。
- [SkyPilot官方Agent博客](https://skypilot.ai/blog/agent-skill)，2026-04-09：统一机群清单/专业后端；不采用自动凭证/云启动行为。
- [Ray当前资源文档](https://docs.ray.io/en/latest/ray-core/scheduling/resources.html)、[MultiKueue当前文档](https://kueue.sigs.k8s.io/docs/concepts/multikueue/)：逻辑资源、manager/worker准入和状态边界；页面版本可变。
- [NVIDIA拓扑博客](https://developer.nvidia.com/blog/nccl-deep-dive-cross-data-center-communication-and-network-topology-awareness/)，2025-07-14，是较早工程依据，未标2026新论文。

本轮CPU合成检查与独立审查保存在 `agent_doc/results/cluster-planning-20261008/`。不证明远程部署、GPU通信性能、模型质量或节省token。既有独立科研入口未重复加载此全文；本次接入实际通用主入口 `prompts/orchestrator.md`，需要时按路径读取。
