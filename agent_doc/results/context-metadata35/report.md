# CONTEXT-METADATA-35：导航元数据与全文物化分离

日期：2026-10-19。基线：`24c892a721d0d511c0b38704ad5093fabfce5433`。本轮仅优化合法 JSON 知识库的 CPU context 装配；不更换检索/选择算法，不增预算，不宣称 LLM 任务质量、token 成本或完整请求提速。

## 实现与触发条件

`agent_runtime/knowledge.py:220` 新增私有 `_metadata`，`:273` 的 `related` 与 `:319` 的 context seed 使用它。原路径调用 `get` 只为读取关系/依赖闭包，却先对全文 JSON 序列化及反序列化；超条目预算的 seed 也付出全文复制成本。本次保留 ID、published、依赖闭包及排序检查，最后入包的 payload 仍调用原 `get` 深拷贝。公共 `get` 不变，实例/子类自定义 get 回退原钩子；无跨请求缓存。standalone mirror 字节同步。

原源码 SHA-256：`32e4f301463d9cd57e4ced59ed3504f24778c9d1358fda242deb2f1f09091064`；生产实现：`49bfa49d94fb12a5236de094baf7d8c1eda6df03d6e09c67a8369f7b584ba870`；复现脚本：`2688348729cca3510f6f1f5b11d3953adeba539054ddf2d0b249eaee675697a5`。生产基准从固定 Git SHA 加载独立旧类，`--production` 明确选择当前实际类，避免把候选结果冒充生产结果。

## 固定协议与实测

同机、同 corpus、同查询/条目及字符预算、完整返回严格相同。16 场景：4 查询 × limit 5/20 × context/fresh；每场景 2 warmup、11 个交错 AB/BA 配对，全部样本保留。目标 matrix/5/context 预设至少降低 10%；其他场景不超过 max(基线110%, 基线+0.2ms)，峰值不超过 max(基线200%, 基线+65536字节)。每阶段只跑一次，不挑样本，不依据结果重设门槛。各轮16场景均过门槛。

| 阶段 | 目标旧→新中位数 ms | 降幅 | Python 跟踪峰值字节旧→新 |
|---|---:|---:|---:|
| 候选主测 | 6.590888 → 4.019058 | 39.02% | 116565 → 97034 |
| 候选独立复跑 | 10.648281 → 5.237379 | 50.81% | 116565 → 97034 |
| 实际生产类 | 6.679570 → 3.608697 | 45.97% | 116565 → 97034 |

context 不含 store/search；fresh 含构造、全语料校验、search、context，但不含 Python 进程启动，不清 OS 缓存。完整结果保留至计时结束，比较/释放与 journal 写入在计时外。独立 tracemalloc 每场景一次，不是 RSS/显存。共享宿主未独占，噪声显著：独立旧目标样本约6.100–26.182ms。实际生产 matrix/5/fresh 反而从97.268924升到100.008687ms（+2.82%），matrix/20/fresh 跟踪峰值1579858升到2003782字节，均在预设容忍内；不宣称每个场景加速或省内存。

环境：Linux6.18.55 x86_64/glibc2.39，Xeon Platinum8573C，Python3.12.14/Clang22.1.3，affinity0–8，GC启用(700,10,10)，CLOCK_MONOTONIC 1ns；纯标准库 CPU 工作，无GPU/kernel/JIT测量。语料 snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`，全部输入文件 hash 在本地 raw bindings；目标完整输出 hash `ba2637f8121a8ff421c765c49906f971a27f3366428089abec3fbb3f98b0cb04`。

## 证据、复现与边界

入口：`PYTHONHASHSEED=0 timeout 120 python scripts/benchmark_context_metadata.py --production --out <不存在的输出目录>`，需基线 Git 对象可读。`summary.json` 是三轮全部场景的派生摘要，不包含全部原样本，不能单凭它复算全部统计。大 raw/JSONL/完整回归日志仅保留本地；以下 hash 指向当时真实原始证据，不意味着远端附带文件。

- 主测 raw `cc897af8bf664740eb193cddae57125779501e839180798da0fce4e0546f7a9e`，progress `355bb3710f86a6ec6f115b67192a0fac9b1ec1c70bf1feca5b6d6627bec23e6d`。
- 独立 raw `564f264817674abf7a1037725e716ebf0fa8aec2a4a2a2842025ac7ca4b38884`，progress `57379e9d815eb079eebc42c166eecbe4e9fde21457cc5117fe883f28d99c724a`。其完整结束标记已核验，但原工具会话最终 shell exit 状态未保留，不能补称 observed exit0。
- 生产 raw `8fe68854109fd2367c6ee729e2505bc7ce55f0b1bdfc6cf6c6398c3934fd469b`，progress `f30182d528e07bac24b82d5a3371ceafd627094b64f653ed152ce7b9a290f2df`，实际观察 exit0。
- 历史脚本/计划按原字节保存为 `frozen-benchmark.py` / `frozen-plan.md`，分别绑定 `400f147cca2c768fb6433801986ea3d7b865a6add11fed64316018aafa757f66` / `23f75430d7de89b9e13da92e04237f551a5c4cf51c30ab5caca9d00e58f429b7`；旧 raw 中原路径应映射到这些快照。原脚本依赖旧源码，不能在新版 checkout 直接当现行复现入口。
- 构造器依赖 knowledge_reuse.py：`1849dd50105b1ab741407a4ec76b804ef90675f724191bab0dd7e30f7685f9b7`，旧实验原绑定遗漏由独立复核补查；现行脚本显式绑定。

独立候选核验1505项输出/异常对照，覆盖全部110 published ID、预算/字符边界、未知/未发布/旧snapshot、重复/空请求、嵌套污染、有效records变更、实例/子类get钩子。损坏内部状态（例如手工注入不可JSON序列化对象）可能在仅导航/拒绝seed时不再报原序列化错误；不属于本性能等价范围。任意并发修改records不作保证。

新增结构回归先在旧实现出现2失败，再集成后通过；失败说明无用序列化存在，不是捏造旧功能错误。完整回归/集成独立验收记录见 `testing.log` 与 `review.md`。无原生 ReviewSession/tmux/常驻适配，本次是用户授权的有界人工维护，不声称受管监督发布门禁已经部署。

历史缓存候选31未达10%门槛，保留负结果，不重新包装为本次收益。研究映射见 `research.md`：复核既有12篇矩阵，新增TallyMem原文机制/限制阅读；仅采用阶段分离的工程思路，不声称复现论文算法。下一步仍需真实Agent任务质量/端到端成本验证，局部优化完成不关闭持续任务。

发布状态：全回归、Reader3项及最终独立六项集成验收已通过（usable-with-scope）。报告冻结时尚未更新远端ref；主控随后fresh fetch main、普通非force发布并回读SHA/tree/关键内容，此文件不预先签发发布回执。独立集成JSON保留本地；其中复用模板的“no production integration”注释不符本阶段，review.md明确勘误：实际生产代码已经集成并验证，尚未远端发布；不修改历史原始文件/hash掩盖该注释错误。
