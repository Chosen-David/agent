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

### 实际验证记录（2026-10-03）

在 `ec13603` 实现合并远端 `93c5823` 后的 `6aeaaa0` 上：

- `python -m unittest discover -s tests -v`：**173/173**；[完整日志](experiment_evidence/tests.log)。包含原有静态契约与运行时测试，新增实验专项 10 项。
- `python -m unittest discover -s apps/paper-reader/tests -v`：**3/3**；[日志](experiment_evidence/reader-tests.log)。
- `python scripts/sync_plugin_references.py --check` 与 `git diff --check`：通过。
- 独立 CPU fixture：2 workers、16 samples，**16/16 exact integer match**；[原始 receipt](experiment_evidence/cpu-accuracy.json)。
- CPU performance fixture：20 组配对 raw ns，未独占，仅流程演示；[原始 receipt](experiment_evidence/cpu-performance.json)。不据此宣称科研系统性能提升。
- 独立审查修复后通过；审查者再次核对五个 checkout、16 文件 SHA256 与采用依据一致。未执行这些上游代码。

合并后采用新 supervisor 核心在私有 scratch 建立只读 release-evidence DAG，四个已有日志/receipt 的字节校验均 done；这仅核对已运行证据，未伪称核心启动实验。scheduler capabilities 为 `ready=false`（无 live serve/cloud adapter），没有启动或遗留 monitor，不影响当前会话完成发布。

## 可选 GPU runner 收尾（a223ffc 之后）

在原有 CPU fixture 外新增 `scripts/gpu_adapter.py`，保持原接口不变：CLI 根据快照与请求给出设备分片 dry-run，或生成默认阻塞的项目 adapter；可信宿主显式调用 API 后可用真实 runner 执行。无需安装 torch/CUDA/后台服务，不自动加载 JSON 指定的代码。

已实现准确率多设备 worker、稳定样本种子、批量 OOM 回退、覆盖检查；性能单设备顺序交错、同步计时和正确性回调；协作 flock、取得锁后再检查、运行前/中/后完整准入和撤销检查。runner ID 与 protocol SHA 必须匹配；完整资源可见性与性能排他调度器由可信宿主提供，并在回执中保留检查证据。计算进程快照和本地锁都不能证明空卡或独占，探测间隙仍可能漏掉外部活动。

独立审查发现并修复 CSV 无表头/空输出/未知单位被误作可用资源的问题，以及 compute-only 查询不足以证明无外部进程的问题；复审通过。新增 **14 项 CPU/mock 测试**覆盖分片、种子不漂移、OOM、协作锁、授权撤销、晚到进程、最终调度器撤销和协议不匹配。全套 **187+3** 通过，[日志](experiment_evidence/gpu-adapter-tests.log)；离线同步与 diff 检查通过。实际执行 CLI 的 mock plan 与生成 scaffold，前者正确分片，后者明确 blocked，未探测/运行 GPU。

真实 GPU/model 验证仍 `notrun`。剩余依赖：获准 UUID 与预算、项目模型 runner/冻结评测协议、完整进程/配额/内存准入 provider；性能还需实际排他调度器。宿主 adapter 负责线程安全、有限调用期限、取消、指标计算与回执落盘；本层不提供多机调度或模型断点恢复。不是新的平台框架，也没有把 CPU 合成通过改写为 GPU 通过。sglang 保持未修改/未执行。
