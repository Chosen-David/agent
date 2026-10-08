# 合成编译诊断的前向执行报告

Task: KERNEL-FEEDBACK-01 / fresh-context forward exercise，2026-10-08。
PROJECT_ROOT / WORKFLOW_ROOT: `/workspace/scratch/c12f3d9f92bd/agent`。

结论：现有材料只能确认这份合成日志写了哪些资源指标，不能确认目标源码编译成功、spill 是主要瓶颈或任何加速收益。手工摘要提出的两个直接开关都不适用当前配置；最有区分力的下一步是先绑定真实源码与构建，再定位 spill 所在代码是否处于关键路径。未修改 kernel、构建、生产文件、TASK 或 guide；未安装、编译、运行 GPU、benchmark、提交或推送。

## 已观察到的材料

实际运行仓库 Skill 的 `scripts/compiler_feedback.py`，输出见 `compiler-feedback.json`。解析程序退出码为 0；这只是解析进程退出码。其 `compile_success=null`、`performance_verdict=not_measured`，全局 `parse_status=partial`。

| 字段 | case_forward | helper_unknown | 原日志定位 |
| --- | --- | --- | --- |
| 目标架构 | sm_90 | unknown/null | 1；helper 5 未给架构 |
| registers/thread | 128 | unknown/null | 4 |
| static shared memory | 32768 bytes (32 KiB) | unknown/null | 4 |
| stack frame | 64 bytes | 0 bytes | 3 / 6 |
| spill stores | 32 bytes | 0 bytes | 3 / 6 |
| spill loads | 16 bytes | 0 bytes | 3 / 6 |

helper 的显式 0 可以保留；不能把其未打印的寄存器和 smem 填 0，也不能继承前一 kernel 的架构。stack frame 不等于 spill；spill loads/stores 的静态报告字节数不等于运行总访存量。32768 是静态 smem，不包含未提供的动态申请量。128 registers/thread 是资源线索，不能单独推出 occupancy、延迟、带宽瓶颈或“过多”。两条记录不是两个可比候选，不能比较其性能。

输入 SHA256 为 `5c5bef39ca452c7ea6380cad6c57167fb175cb18bd74a47fbe4419467dfa0ef0`，354 bytes。完整输入、Skill、解析器及依赖哈希见 `input-lock.json`。HEAD 为 `9d0d05bfca88faf5c8fc57420bad4d5abf3b01a4`，工作树有主 AI 正在维护的修改，因此 HEAD 不能代替实际脚本哈希。H100 / CUDA 12.4 / -rdc=true / 动态 smem 来自题面，并未探测本机设备或真实编译器。

## 候选取舍

| 候选 | 当前决定 | 判别依据与最小检查 |
| --- | --- | --- |
| 直接启用 shared-memory spilling | reject 当前做法；改变配置后才可重新评估 | NVIDIA 正文说明 CUDA 13+、whole-program / -rdc=false，排除动态 shared memory。当前三项条件分别不满足。不得仅升级工具链就称已满足其他两项。 |
| 直接采用 Blackwell tcgen05 | reject H100 路线 | PTX `tcgen05.mma` Target ISA Notes 不包含 sm_90；变更 target 字符串不会使 H100 支持它。也不知道该算子是否适合矩阵指令。 |
| 缩短 live range / 降低展开 | 候选，未实现未测 | 若源码显示热循环内过多同时存活临时值，可先选一项修改；检查重计算或访存增加、正确性、资源变化与正常计时。 |
| tile / stages 小型比较 | 候选，先需源码和 launch 配置 | 可能降低寄存器或 smem，但也可能降低重用/并行度。先改变一个因素；若二者不可分，再预先声明小型联合对照。 |
| 强制 maxrregcount / 追高 occupancy | 不作为第一项 | 限寄存器可能增加 spill；occupancy 不是验收目标。先证实真实资源限制和时长影响。 |
| Hopper 支持的异步流水 / warp specialization | defer | 先核实实际算子、ISA/编译目标、同步边界和 smem/寄存器预算；更复杂机制不保证收益。 |
| persistent / fusion / 更换成熟库 | defer | 没有算子语义或 timeline，不知道调度、launch 或中间读写是否相关，不能据函数名猜是 attention/GEMM。 |

源码/工作负载尚缺，不能诚实给出算法复杂度、最强库基线或吞吐上限。当前没有候选胜出。launch bounds 在 NVIDIA 正文是建议，不能将页面 AI 摘要中的“required”当作额外强制规则。

## 下一步最有区分力的检查

1. **先做 CPU 证据绑定。** 请主 AI 提供真实 kernel 与 helper 源码、生成代码及版本/hash，完整且单次不交错的编译日志、实际命令、所有 flags、nvcc/ptxas 版本与可信退出码。确认该日志确实对应被分析的 kernel、架构和构建，而不是陈旧产物。没有这一步，资源解释无法归因到可修改代码。现有合成材料不能补出该绑定。
2. **随后检查可证伪的资源假设。** 补充 shape/dtype/layout、线程块/网格、warps、tile、stages、展开因子、动态 smem 每块 bytes、launch bounds、寄存器限制；阅读现有 PTX/SASS（如已有导出）及源码映射，定位 spill 访问是否在高频循环。假设 H1 为“过长 live range 导致热路径上的 spill，降低其压力可能减少时长”；反例为 spill 处于冷路径、关键路径在其他 kernel/主机、或减少寄存器却因重计算/访存增加而变慢。只靠现有静态字节数无法在这些解释间选择。
3. **GPU 证据属于未来另行授权工作，本轮未执行。** 先取得端到端 timeline，确认 case_forward 是否值得优化，再取对应 launch 的 profiler 原始导出，检查 local load/store、相关访存/停顿、寄存器和 shared memory 的实际限制与 kernel 时长；需要将 profile 开销和正常计时分离。如果它不是关键路径，应停止此 kernel 的性能改造而回到实际瓶颈。
4. **只有证据支持时做最小对照。** 固定 H100/工具链/输入/语义，保留 baseline，首轮最多一个源码候选（例如缩短 live range；若源码不支持则不强行改），先独立 reference 与尾块/布局/边界正确性，然后隔离同卡、配对的正常 GPU 事件计时。固定 warmup、重复、同步和计时边界，保存所有原始样本、失败、噪声与退化。若 spill 下降而延迟无可信改善，则否定“spill 改善足以提速”的当前假设并保留基线。不得将 profile 时长直接与未 profile 的时长比较。

最终接受条件应由主 AI 在实测前固定：正确性不退化、目标工作负载下延迟改善超过预设噪声/收益门槛、端到端必要指标不退化。当前无阈值、原始计时或有效 GPU 运行，因此 speedup 和改善幅度均 unknown，不用 0 或推测百分比代替。

## 实际执行与使用证据

- 使用仓库入口 `plugins/research-assistant/skills/research-implement-optimize/SKILL.md`，读取 workflow 第 1、3、硬件/测量/优化/交接章节及完整 Agent Prompt，以及 execution、engineering_reuse、kernel_optimization_feedback、knowledge_access、result_reuse、result_validation 参考。AGENTS、decision_review、项目文档治理、TASK 也已读取；guide 文件为空，未推断任何人类批准内容。
- 工具选择：本机 Python 文件分析和 Skill 自带解析器已经覆盖本题能力。未安装外部 kernel 工具，没有必要进行候选 orchestrator 安装/性能比选。工具源码未改动，版本由哈希锁定。
- 先查旧结果：`PTXAS H100 spill` 搜索扫描 30 个目录，无候选，但 11 个目录缺 record.json，因此 status=incomplete，不能声称完整搜索无历史。没有旧性能数据被复用。
- 知识检索：`PTXAS register spilling H100 CUDA` 返回 FlashAttention、FlashInfer、推测解码卡片，均没有本题未给出的算子前提，不采用它们作为当前优化依据。完整返回与 snapshot 保存于 `knowledge-search.json`；adopted knowledge_refs 为空，不把检索命中计作应用。
- 官方来源仅核对公开能力限制，未提交题面或 kernel 数据，见 `source-checks.json`。没有引用厂商案例数字作为本机性能证据。
- `capture.py` 实际重新捕获 6 条只读命令的 argv/cwd/stdout/stderr/returncode，见 `tool-trace.json`。它保存关键解析/查询输出供复核，不是 GPU runner，也不是独立验收器。
- 初始 cat/rg/sed 读取分批返回中过大输出曾被工具截断，随后按章节重读核心参考。解析器本次调用没有报错或歧义；partial 正确反映 helper 缺项。

## 交接、限制与可用性问题

CPU 文件解析已执行；编译、运行正确性、GPU 性能、公平 A/B、外部 runtime 集成均未执行。产物状态为 **pending independent review**，由主 AI 指派的独立 owner 核验输入、脚本哈希、实际 stdout、单位与以上推断边界，不能由本作者自填 pass。建议依赖为：本诊断产物 → verify_experiment_result/独立诊断核对 → 缺失输入收集 → 后续有授权的实验；不得把本报告用作 GPU 加速结论。

实际可用性问题：旧结果目录有未登记记录导致有界检索不完整；通用知识检索命中了无关算子卡；workflow 的早期“第一动作动态发现”较广，SKILL/execution 的按需条款才使此小任务免于不必要外部安装。新反馈参考和解析器本身可直接运行，未知字段和证据边界足够清楚。未发现需要修改生产工具才能完成本题的问题。

按父任务的单写者约束，仅在本目录写输出，无 pull/merge 或 TASK 写入。主 AI 负责接收证据、更新唯一 TASK 以及后续独立验收；本子任务不宣称 KERNEL-FEEDBACK-01 整体完成。

来源（2026-10-08 核对）：

- [NVIDIA: shared-memory register spilling](https://developer.nvidia.com/blog/how-to-improve-cuda-kernel-performance-with-shared-memory-register-spilling/)，正文功能表与 limitations（检索行 35–40、183–190）。
- [NVIDIA PTX ISA 9.4](https://docs.nvidia.com/cuda/parallel-thread-execution/#tcgen05-mma)，`tcgen05.mma` Target ISA Notes（检索行 24938–24994）。当前文档核对能力边界，不意味着 CUDA 12.4 支持其全部内容。
