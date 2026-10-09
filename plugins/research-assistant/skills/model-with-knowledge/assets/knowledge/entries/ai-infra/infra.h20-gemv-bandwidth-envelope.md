# H20-3e 硬件包络与带宽受限 GEMV 的 roofline 推导

## 问题触发

在 NVIDIA H20-3e 上优化 GEMV（`y[M] = a[1,K] · B[M,K]`，B 行主序 half）或类似"每元素只用一次"的归约型算子时，需要判断瓶颈是算术还是访存，并据此选择优化方向。

## 精确结论（本地探测事实 + 推导）

**硬件包络**（2026-10-09 本地 `cudaGetDeviceProperties` 探测，H20-3e，sm_90，CUDA 12.9）：

| 参数 | 值 |
|---|---|
| SM 数 | 78 |
| 总显存 | 139.7 GiB |
| 显存总线 | 6144 bit |
| L2 | 61440 KiB（≈60 MiB） |
| smem/SM（optin 上限/block） | 233472 B / 232448 B |
| 寄存器/block | 65536 |
| L2 persisting 上限 | 39321600 B（≈37.5 MiB） |
| asyncEngineCount | 3 |

（`memoryClockRate` 字段在 CUDA 12.9 头文件已标 Deprecated，探测值 3.201 GHz 仅作参考；由总线宽 × 时钟直接推出的 2.46 TB/s 只是单沿算术下界，HBM 的 DDR 倍率未在本次核验范围内，**不可当实测带宽引用**。）

**Roofline 推导**（前提：B 每元素仅读一次、A 复用于每行）：

- half B 每 2 字节支撑 1 次 FMA → 算术强度 ≈ 0.5 FLOP/byte，远低于任何现代 GPU 的机器平衡点 → **纯带宽受限**；
- 最优时间下界 ≈ 必读字节数 / 可达带宽。忽略 A（2K 字节）与写出的 y；
- 优化目标排序：① 减少必读字节（无冗余读、合并访存 16B/线程/次）；② 提高访存并发与隐藏（寄存器/smem 缓冲、无 barrier 串行化、足够 warp）；③ 保护 L2 中复用数据（流式 B 用 `ld.global.nc` + `evict_first` 类提示，避免冲刷常驻的 A 与活跃行）；
- 占用率视角：warp-per-row 布局下 M 行 → M warp；M < 78×64 时 SM 吃不满，split-K 增加 K 向并行是正确杠杆。

## 推导范围

roofline 推导只对"B 每元素读一次"的算子成立；若换 GEMM（B 跨行复用）则算术强度上升，结论不迁移。硬件包络为本机本卡实测，迁移到其他 SKU（H20 非 3e、H100/H200）需重新探测。

## 算得出的例子

M=4096, K=16384, half：必读 B 字节 = 2·M·K = 134,217,728 B（128 MiB）。
按下界 2.46 TB/s：≈ 54.6 µs；若实际可达带宽为 b，最优时间 ≈ 134.2 MB / b。任何显著高于 bytes/b 的耗时都提示存在冗余流量或并发不足，而不是算力不够。

## 失败/反例

- A 不复用（每行重读 A）在 K 大时引入 2×A 流量——K=16384 时约 64 KiB×M/复用组，量化后才知是否显著；
- 用同步 smem 暂存 + `__syncthreads` 分离搬运与计算：字节数不变，但 barrier 串行化降低访存并发，实测可能慢于无 barrier 寄存器方案（见 CUDA-Triton-Learn GEMV 项目 gemv_kstages 与 agent 无 barrier 变体的对照，实测待空卡完成后归档）；
- M 极小（如 M=8）且 K 极大时瓶颈可能转向单行归约延迟而非带宽，split-K/多 warp 分摊 K 才有效；
- 把 2.46 TB/s 下界当实测带宽使用是错误——必须用 STREAM 类实测校准。

## 任务映射

- 写/优化 GEMV、decode 阶段 per-token GEMV、量化点积归约前，先用本卡包络做字节计数与时间下界估计；
- kernel 候选设计按"字节数 → 并发 → L2 保护"排序评估；实测对照下界判断优化空间；
- 占用率计算用 78 SM × 2048 线程上限（sm_90 每线程块 64K 寄存器约束下按实际寄存器数核算 block 数）。

## 来源定位与尚未验证项

- 字段语义：官方 CUDA 文档 URL 见 JSON sources（外网当日不可达、source=unverified）；实际核对的是本地 CUDA 12.9 `driver_types.h` 上述行号；探测程序与原始日志：`CUDA-Triton-Learn/.agent-runs/gemv-s1s2/device_probe.{cu,log}`；
- 未验证：H20-3e 实际可达 HBM 带宽（需 STREAM/triad 实测）；HBM3e DDR 倍率与官方标称带宽（外网当日不可达，未引用任何记忆数字）；L2 evict_first 提示的实际收益（需 A/B 实测）；
- 本卡不含任何性能实测主张；GEMV 优化对照数据见项目 `agent_doc/results/`（待空卡门禁后归档）。
