# 实验执行能力升级与采用依据

## 已有覆盖与缺口

基于 main `7ec6418`，复用 research-implement-optimize，未创建重复的大 prompt 或新 agent。已有 workflow §4.1–4.3 覆盖 correctness reference、kernel/end-to-end 边界、冷/稳态与同步、原始样本和统计；execution.md 覆盖 speedup 数学与证据交接。新增按需加载的 experiment_execution_contract、标准库 probe/plan/CPU synthetic run 和回归测试，补足可检查执行记录，不宣称已实现完整硬件调度系统。

## 真正读取的材料与取舍

源码 commit、逐文件 SHA256、许可证与固定链接见 [锁定来源](experiment_sources.lock.json)。以下是本次选择性阅读，未声称穷尽全部论文仓库或运行其实验。

| 来源 | 实际入口／机制 | 采用与边界 |
| --- | --- | --- |
| [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention/blob/e9515d5dee6ade134a33d6020d38d01ef0596996/flash_attn/utils/benchmark.py) | benchmark_forward/backward 使用 PyTorch Timer，backward 清 grad；benchmark 脚本固定 shape/dtype 并区分 fwd/bwd | 采用分阶段测量和固定输入；未引入 torch/CUDA。Timer 内部同步行为需对应安装版本确认，调用本身不能替代实测。 |
| [mit-han-lab/Quest](https://github.com/mit-han-lab/Quest/blob/01c1623bf9395009520874e989e29f683203b357/scripts/bench_textgen.py) | bench_textgen.py 分 prefill/decode，perf_counter 包围随机输入与模型调用；LongBench get_pred 有模型 prompt 与中间截断、question 模拟 | 采用阶段边界与任务协议锁定；该计时入口未显式 synchronize，不照抄作 GPU 计时模板。未证明下层绝无隐式同步；question 模拟等数据处理不能静默改掉。 |
| [EleutherAI/lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness/blob/d6de81643928d653435c431bae19945d41d32520/lm_eval/models/huggingface.py) | HFLM._detect_batch_size 执行探测、OOM 减批、跨 rank 最小值；evaluator 分离种子并记录 doc/prompt hash | 采用预算内批量回退、样本身份与协议指纹。当前只有 CPU fixture 进程池与注入式 MemoryError 测试，没有模型或分布式集成。 |
| [ZJtoast/kernel-profiler-skill](https://github.com/ZJtoast/kernel-profiler-skill/blob/b24a10cc3af46caab79453fc1ace583782538cd2/SKILL.md) | SKILL 的 kernel-only/script-first 路由，manifest 的 runtime/environment/stabilization/artifacts | 采用结构化 manifest、kernel 与端到端区分；不照搬 sudo/NOPASSWD 设置或安装收集器，不宣称 profiler 已集成。 |
| [intel/intel-performance-skills](https://github.com/intel/intel-performance-skills/blob/3e33aecabb956ec48526b3f842f4f70ae96d98ff/skills/linux-perf/SKILL.md) | linux-perf SKILL 的 stat/record/c2c 分流、源行映射与权限；flow-a 的 IPC/cache/branch 启发式 | 采用按问题选证据与权限边界；固定 IPC/百分比阈值不当跨架构定律，不自动改 perf_event_paranoid 或安装。 |

只读学习，不复制或重新分发上游源码/skill/模板；新增内容独立编写。FlashAttention 根许可证 BSD-3-Clause；Quest、lm-eval、kernel-profiler 的上述许可证为 MIT；Intel 所读 skill 文件声明 MIT，checkout 未发现独立 LICENSE，故只记录观察而不扩张为全仓许可判断。第三方内嵌依赖各自许可不随根文件推定。没有安装外部 backend、守护进程、credentials，也未执行任何外部实验代码。

## 验收与限制

probe 不导入 GPU 框架；可选 nvidia-smi 是只读、超时、有 unknown 状态。plan 不占资源，GPU run 拒绝。准确率 fixture 真实启动 CPU 进程池，按固定 ID/种子计算整数平方和，用闭式 reference 检查；断点在新目录继续，runner/config/hash 变化拒绝。注入测试覆盖批量 OOM 回退与一般异常不能吞掉。只接受完整可解析且校验通过的 checkpoint，不承诺文件系统事务。

性能 fixture 顺序交错两种算法，记录 first call 与稳态 raw ns/median/stdev，固定参考不污染 candidate 额外调用；无独占租约，只作受干扰 CPU 合成观测。并行准确率不形成速度主张；真实任务吞吐、GPU同步、CUDA OOM、显存准入/租约、质量提升均未实测。affinity 不是 cgroup quota 或 idle 检测；真实工作负载需调度器或项目 adapter 完成这些检查。

独立 review 找到并修复：首次调用计时被 reference 调用污染；resume 缺 runner/schema 身份与单次读取；累计历史验证反复运行 workload 导致预算放大（改 O(1) 闭式检查）。复审 focused suite 10/10 通过，无阻塞；全套验证另留日志。不用测试全绿声称 LLM 遵从或实际科研提升。

SGlang checkout 保持只读，未运行用户 GPU、未修改/推送 sglang；论文和图形留给并行任务。建议固定默认/可选分支与 near/far/gate 配置，准确率协议不变，prefill/decode/indexer阶段/最终attention分层测量；这些仍是计划。
