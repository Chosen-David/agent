# 单卡独立任务扫描的多机多卡编排（embarrassingly parallel sweep）

适用：大量互相独立、每个只需一张 GPU 一部分资源的实验臂/job（超参扫描、基准评测、消融），跨多台授权主机运行。先读 [多机多卡编排](cluster_orchestration_workflow.md)——本文是其**场景补集**：那里解决 gang job（多机同构整组 + RDMA），这里解决单卡分数槽打包。建议落地后的接机、派单、回传与收口见 [GPU 资源池运维 playbook](gpu_pool_operations_playbook.md)。身份、授权、独立验收仍由既有任务链控制，不增加后台调度服务。

## 已实现入口

`agent_runtime.ep_packing.plan_packing` 与 `scripts/plan_ep.py`：对一波依赖就绪的独立单卡 job 给出**分数槽放置建议**（同卡多 job 共享，独占 job 整卡隔离）。与 `plan_wave` 同为 advisory-only：不预留、不 SSH、不启动、不传输；快照 ≤300 秒新鲜度；完成 ID 只能来自独立验收，worker 自报不算。

```bash
# 合成清单回放，时间1001仅用于fixture
python /absolute/agent/scripts/plan_ep.py plan --input /absolute/agent/examples/ep_packing.json --now 1001
```

放置规则：**LPT（估时降序）+ 最小投影负载优先**；独占 job 只进未动过的卡，共享 job 只进 `shared_ok` 且显存和不超的卡。三个执行端校准门（均有默认值、不设则不生效）：`max_shared_utilization`（实测利用率 ≥ 阈值的卡拒绝共享投放）、`max_share_per_gpu`（每卡共置上限，0=仅显存约束）、`contention_factor`（共置降速系数，1.0=不建模；`gpu_serial_seconds` 按 `est × factor^(共置序号)` 膨胀参与排序与报告）。`est_seconds` 是独占执行估计，**未校准时共置降速不建模**——共置档位的真实吞吐与 factor 必须由执行端实测校准（先 2/3/4 路各测一臂，再定档位）。

## 何时用哪个规划器

| 场景 | 入口 |
|---|---|
| 多机多卡整组训练/推理（NCCL、同构卡组、RDMA 阈值） | `cluster_planning.plan_wave` |
| 独立单卡 job 大群（扫描/评测/消融），允许同卡复用 | `ep_packing.plan_packing` |
| 单卡 job 但显存需求接近整卡 | 两用皆可；plan_packing 标 `exclusive: true` 即整卡语义 |

## 执行层模式：共享文件系统 claim 队列（无后端时）

没有 Slurm/Ray 的后端环境下，执行层用共享文件系统（BeeGFS/Lustre/NFS，须先逐机验证挂载一致）做调度面，**ssh 只用于一次性启动 worker 与应急**：

```
<share>/<stage>/manifest/{pending,running,done,failed}/<job_id>
<share>/<stage>/results/   <share>/<stage>/logs/   <share>/<stage>/code/
```

1. **原子 claim**：worker 循环 `mkdir running/<job_id>`（网络 FS 上原子）——消除两个执行者抢同一 job；抢到后写 `owner(host/gpu/pid)` 与启动时间。
2. **lease + 心跳**：running 目录内置 heartbeat 文件周期 touch；任意 worker 兼任 janitor，回收超期 lease 回 pending。任务必须幂等（重跑产出与首跑一致或可安全覆盖），回收才零风险。
3. **原子发布结果**：先写 `*.tmp` 再 rename；半文件永不可见。代码快照 `git archive` + SHA-256 清单（可用 `cluster_planning.verify_local_artifact` 校验），各机启动时校验不符即拒绝。
4. **完成态判定**：`done/` 只记录"进程退出码 0 + 产出契约满足（行数/schema）"；进入下游的 verified 集合必须再经独立验收（评分/对拍），worker 自报 pass 不算数——与 `plan_wave` 的 `verified_task_ids` 纪律一致。

## 扫描类负载的六个手法（tricks）

| # | 手法 | 依据与边界 |
|---|---|---|
| T1 | **分数槽复用（bin-packing）**：瓶颈互补的 job 共置（CPU/launch 瓶颈 × 带宽瓶颈 × 计算瓶颈混搭） | 显存只是必要条件；真实吞吐曲线必须先测。共置降速不建模是 plan_packing 的明示 limitation |
| T2 | **LPT 投序**：估时降序投放，长 job 先占坑 | Graham 界：贪心 LPT 的 makespan ≤ 4/3 最优；估时来自同配置历史实测，不猜 |
| T3 | **长尾投机执行（backup tasks）**：池见底后 straggler 允许第二 worker 冗余 claim，先完成者赢 | MapReduce（Dean & Ghemawat OSDI'04）；用收尾闲置槽位，要求结果幂等 + rename 原子 |
| T4 | **逐轮早停（ASHA rung）**：便宜 rung（少样本/便宜任务）全臂跑 → 置信区间剪枝 → 幸存臂才进贵 rung | Hyperband（JMLR 2018）/ASHA（MLSys 2020）；**剪枝门必须用配对置信区间**，头部差距在噪声内时全保留，不硬切排名 |
| T5 | **任务内断点**：长 job 逐样本 append+flush 并记录完成数 | 崩溃损失从整 job 降到 ≤1 样本；代价是 partial 文件必须被完成态判定正确区分（契约=完成数达阈） |
| T6 | **在线增量验收**：watcher 对每个 done 即时更新部分排名 | 末 job 完成时结果立读；且 T4 的 rung 决策可飞行中执行 |

## 通信与验收纪律（沿用 gang 篇，此处再强调）

- 控制面：SQLite/Mailbox 只本机，不放共享 FS 充当跨机服务；跨机只有"启动 worker / 应急 kill"两类 ssh 动作。
- 文件面：暂存 → 大小/hash → 原子不可变发布；hash 不替代身份/权限。
- 快照：worker 启动前重新探测本机 GPU 实际占用（`nvidia-smi`），快照不是租约；两个 dispatcher 建议同一槽位时，mkdir claim 即原子准入裁决。**快照应带 `utilization_percent`**：显存只判能不能塞，利用率才判该不该塞（实测教训：85% util 的卡按显存仍可塞 3 个 job）。
- 灰度：单卡单 job → 单卡多 job → 单机多卡 → 多机 → 注入 worker 死亡（验证 lease 回收）→ 注入长尾（验证投机）。
- 报告：吞吐与单 job 延迟分开记；共置档位、剪枝门、投机命中数全部入 manifest；不以合成清单宣传加速。

## 调研锚点

- Hyperband: Li et al., JMLR 2018（arXiv:1603.06560）——rung 式资源分配与理论保证。
- ASHA: Li et al., MLSys 2020（arXiv:1810.05934）——异步逐轮早停，500 worker 实证线性扩展。
- MapReduce: Dean & Ghemawat, OSDI'04——backup tasks 治 straggler。
- LPT: Graham 1969——估时降序贪心的 4/3 makespan 界。

以上为文献机制引用，本仓库未复现其数字；T1-T6 的收益声明一律以本项目实测为准。
