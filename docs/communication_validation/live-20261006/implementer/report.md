# EXP-1 描述性合成延迟结果

输入版本 synthetic-v1；run_id communication-live-20261006T1432。
本阶段已执行 calculate.py，实际输出见 results.json 和 execution.log。

| 指标 | 结果 |
| --- | --- |
| baseline 样本数 | 6 |
| candidate 样本数 | 6 |
| 配对数 | 6 对，共 12 个延迟值 |
| baseline 总延迟 | 612 ms |
| candidate 总延迟 | 534 ms |
| baseline 平均延迟 | 612 / 6 = 102 ms |
| candidate 平均延迟 | 534 / 6 = 89 ms |
| 均值之比加速比 | 102 / 89 = 1.146067415730337 倍（无量纲） |

算术平均值公式为 mean(x) = sum(x_i) / n。
加速比定义为 mean(baseline_ms) / mean(candidate_ms)，不是各配对比值的平均数。

输入明确为合成数据，仅验证通信流程，并非系统实测性能；不得推广为真实系统收益。
此阶段仅交付样本数、两组均值和均值之比等描述性结果；未计算不确定性或推断统计，不声称统计显著性。

从任意目录复算：python /workspace/scratch/4f9639d1bad2/agent/.agent-runs/communication-live-20261006T1432/implementer/calculate.py
也可用 --input 和 --output 指定输入和结果路径。代码默认读取本 run 的 input.json。

当前决策 EXECUTE；授权范围仅本阶段描述性统计与实现者交接。下游 reviewer 独立审查，不由实现者验收。
