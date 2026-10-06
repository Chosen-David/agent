# EXP-1 合成延迟结果 v2

run_id: communication-live-20261006T1432；input_version: synthetic-v1。
修订对应 review seq=2、finding_id=EXP-1-SAMPLE-DISPERSION-001。
已实际运行 calculate_v2.py；此修订补充证据，原发现等待 reviewer 独立复验关闭。

| 指标 | baseline | candidate |
| --- | --- | --- |
| 样本数 n | 6 | 6 |
| 总延迟 | 612 ms | 534 ms |
| 平均延迟 | 102 ms | 89 ms |
| 离均差平方和 | 118 ms² | 42 ms² |
| 样本方差（ddof=1） | 23.6 ms² | 8.4 ms² |
| 样本标准差（ddof=1） | 4.857983120596447 ms | 2.898275349237888 ms |

原输入为6对观测，共12个延迟值。均值 mean(x)=sum(x_i)/n。
样本标准差 s=sqrt(sum((x_i-mean(x))²)/(n-1))；ddof=1，分母为5。
故 baseline s=sqrt(118/5) ms，candidate s=sqrt(42/5) ms。

加速比仍定义为 mean(baseline_ms)/mean(candidate_ms)=102/89=1.146067415730337 倍（无量纲），不是各配对比值的平均数。

数据仅为通信验证而合成，并非系统实测性能；不得由此声称真实系统收益。
标准差描述这两组合成样本的离散程度；未计算置信区间或推断检验，不声称统计显著性。

复算：python /workspace/scratch/4f9639d1bad2/agent/.agent-runs/communication-live-20261006T1432/implementer/calculate_v2.py
支持 --input 和 --output 参数。默认输入为原始 input.json，默认输出 results_v2.json。

原始 v1 文件和已发布 SHA-256 引用全部保留。本次交付范围为描述性离散度补充；实现者不代替 reviewer 验收或关闭发现。
