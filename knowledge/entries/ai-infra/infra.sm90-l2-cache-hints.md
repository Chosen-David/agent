# sm_90 上 L2 evict-first 提示的真实生效编码：__ldcs，而非 createpolicy+L2::cache_hint

## 问题触发

带宽受限算子（如 GEMV：流式 B 每元素读一次、小 A 常驻复用）想让流式 load 不冲刷 L2 中的复用数据。PTX ISA 提供多条路径（createpolicy+`L2::cache_hint`、`ld.global.nc.L2::evict_first`、`__ldcs` intrinsic），但在 H20-3e (sm_90) 上哪条真实生效？

## 精确结论（本机 SASS 实测，CUDA 12.9 / nvcc V12.9.41）

| 路径 | 编译 | SASS | 生效？ |
|---|---|---|---|
| `createpolicy` + `ld.global.L2::cache_hint` | ✅ | 与普通 load **逐字节相同** | ❌ 策略被丢弃（单次与循环上下文双验证） |
| `ld.global.nc.L2::evict_first`（v4.u32） | ❌ ptxas 报 requires `.v8.b32/.v4.b64` | — | ❌ 256-bit load 是 sm_100+ 能力 |
| `__ldcs` | ✅ | `LDG.E.EF.128` | ✅ **唯一确认生效** |

附带事实：`const __restrict__` 指针已免费生成 `LDG.E.128.CONSTANT`（.nc 语义），无需额外 hint。

## 推导范围

- 硬件/工具链限定 sm_90 + CUDA 12.9；sm_100+（Blackwell）的 256-bit evict_first 与 cache policy 行为需另行验证；
- "SASS 编码生效"只是机制证据，不构成性能收益主张——小 A（≤32KB）对 60MB L2 的冲刷效应本身微弱，净收益需 A/B 实测；
- 未测 `__ldlu`（last-use）与 persisting L2 window（`cudaStreamSetAttribute` accessPolicyWindow）路径。

## 算得出的例子

GEMV M=4096、K=16384：A=32KB（常驻候选），B=128MiB（流式）。B 若以普通 load 混入 L2，60MB L2 在最坏情况下被 B 持续冲刷；A 每 warp 重读需回 HBM（32KB × 重读次数的额外流量）。evict-first 让 B 优先被逐出。但 A 总驻留需求 ≈ 32KB ≪ 60MB，故收益上限小——这正是"机制生效 ≠ 值得开"的典型例子，用 A/B 判定。

## 失败/反例

- 以为写 PTX createpolicy 就生效：SASS 与普通 load 逐字节相同，静默无效（本卡核心反例）；
- 在 sm_90 上追 256-bit evict_first 向量 load：ptxas 直接报错；
- 把编码生效当性能收益宣称：未经同条件 A/B 不得下结论。

## 任务映射

- 任何"流式数据 + 常驻复用数据"的带宽受限 kernel（GEMV/GEMM 分块、解码投影、量化点积）在 sm_90 上用 `__ldcs` 做流式侧提示；
- 先 `cuobjdump -sass` 确认目标 kernel 的 LDG 编码含 `.EF` 再相信 hint 生效；
- 迁移架构/工具链时重跑 probe 并 diff SASS。

## 来源定位与尚未验证项

- 证据：`CUDA-Triton-Learn/.agent-runs/gemv-s4-round2/evict_hint_probes/`（4 个 probe 源码+SASS+EVIDENCE.md）、`sass_v2.log`（2026-10-09 本机实测）；
- PTX ISA 官方文档 URL（外网当日不可达，source=unverified，candidate 待核验后升级）；
- 未验证：sm_100+ 行为、`__ldlu`/accessPolicyWindow 路径、evict-first 的 A/B 净收益（空卡后归档）。
