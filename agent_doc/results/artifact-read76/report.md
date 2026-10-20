# ARTIFACT-READ-76：降低小文件读取的分配峰值

日期：2026-10-20；基线 `a55a3d14d8ebf0f840c4bdd9477562fdc369fe44`。

## 问题与修复

真实路径 `prepare_dispatch → _bound → _bytes`。原 `_bytes` 在已检查普通文件大小后，
仍为每个文件请求 `read(16MiB+1)`；本机CPython即使实际只有5字节，也产生约16.8MB
Python分配峰值。它是已有界读取的内存浪费，不是上下文内容错误。
修前回归 `test_small_artifact_peak` 实际失败：`16782929 not less than 1048576`。

改动限于 `agent_runtime/result_validation.py:69–82`：小于64KiB且可seek的文件先请求
`fstat_size+1`；若填满，释放探测结果，从同一已检查句柄重新有界读取。大文件或不可
seek输入保留原路径。最终长度检查、历史迁移digest、后续hash与异常优先级不变。
不提前按派发字符预算拒绝，不截断文件，不改变模型输入。

旧read74候选先读首段再拼接余段，独立复核发现1byte→16MiB增长的峰值约33.6MB，
因此未合入。新方案明确覆盖该负结果，避免同时持有首段/余段/拼接结果。
代价是小文件增长时重复读取至多64KiB；不承诺累计读取仍仅LIMIT+1，也不承诺文件
原子快照或任意并发写入交错的相同内容。64KiB是保守工程界限，不宣称全局最优阈值。

## 配对测量与独立复测

CPython3.12.14、Linux6.18.55、AMD EPYC9V74虚拟CPU（9逻辑CPU）。单位是
`tracemalloc peak bytes`，非RSS。两次预热、五次交错配对，中位数作为预先冻结的聚合；
完整函数在追踪范围内，fixture构造在外。源码、输入和输出hash见[raw.json](raw.json)。
基线从固定git SHA加载，候选为当前生产函数，不将旧负结果当本轮数据。

| 场景 | 基线中位数 | 候选中位数 | 结果 |
|---|---:|---:|---|
| 完整prepare_dispatch，527字符输出 | 16,787,810 bytes | 10,612 bytes | 降低99.9368%，对象完全相等 |
| 独立完整prepare_dispatch复测 | 16,787,810 bytes | 10,612 bytes | 同方向，五次配对均保留 |
| 主控17个稳定/增长/缩小场景 | 见raw.json | 见raw.json | 各场景median比率≤1.01 |
| 独立23个分配场景 | 见independent-raw.json | 见independent-raw.json | 最大median比率1.00102119≤1.01 |

读入文件尺寸覆盖空、5、4096、65535、65536、1MiB、16MiB；确定性fstat后增长覆盖
0/1/65535/8MiB→16MiB与16MiB+1，另有缩小场景。不隐藏回退或超限结果。
完整派发收益只适用于本机小文件fixture，不外推真实LLM成功率、token节约、wall、
吞吐、冷盘或总进程内存。增长回退的额外I/O时延尚未测量。

复现：`python scripts/benchmark_artifact_read.py`；需要本地可读基线commit。
首个测量脚本尝试因独立加载的基线异常类未被捕获而退出，无完整结果；改为捕获
ValueError并核对具体类名/消息后完整重跑。原部分观察不用于表格，生产源码未因此改变。

## 验证、研究与未决问题

- 针对测试41项；全库1314项（8跳过，其余通过）；Reader3项。顺序执行，无重叠。
  [短日志](tests.txt)、[修前](before.log)、[修后](after.log)保留；全量大日志仅本地保留，
  SHA写入短日志，不声称全部原始日志已上传。
- 独立审核读取实际代码与17行原始数据，并以额外15项精确语义对照、23个分配场景、
  正常/非法路径、FIFO、symlink、legacydigest、stalehash、nonseekable和seek失败检查
  核验边界。最终六项结论与hash绑定见[independent.md](independent.md)。
- 技能要求的修前失败、完整路径配对与非退化门槛直接影响本轮取舍，旧负结果未改写。
  [研究记录](research.md)沿用此前十篇正文阅读，并补读ACM的设计/评估段落；本轮不计
  十篇新精读，也不声称部署论文中的语义压缩策略。
- 新发现 **ARTIFACT-FD-77**：目录输入在`os.fdopen`拒绝时可能泄露fd，基线/候选均
  复现，两次调用fd计数4→6，关闭本测试拥有的两个fd后回到4。见
  [独立原始记录](independent-fd-raw.json)。本补丁未修复该旧问题，后续需单独实现与验收。

只有本项被核验，不代表整个持续优化目标完成。发布前仍需刷新main并核对候选树；
本报告中的实现/测试状态不替代实际push与远端回读。无tmux或长期可信宿主适配器，
不声称部署持续监督服务。人类guide及其他仓库没有改动。
