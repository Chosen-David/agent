# v2 结果工作稿

在提供的 measurements.csv@v2 中，small 和 medium 的端到端报告耗时分别由 100 ms 降至 80 ms、由 120 ms 降至 100 ms，对应耗时降低 20.0% 和 16.7%（加速比 1.25× 和 1.20×）。large 则由 200 ms 增至 220 ms，耗时增加 10.0%（加速比约 0.91×）。另列的 kernel-only 耗时由 20 ms 降至 10 ms，呈现 2.00× 的局部加速；该计时范围不能外推为端到端加速。因此，现有报告值显示收益随工作负载而异，并包含大规模回退。由于未提供重复测量、误差、运行配置和正确性验证，本结果仅描述当前快照，不证明统计显著性、可重复性、因果关系或其他工作负载上的收益。

| workload | scope | baseline (ms) | candidate (ms) | candidate 耗时变化 | baseline/candidate |
| --- | --- | ---: | ---: | ---: | ---: |
| small | end_to_end | 100 | 80 | −20.0% | 1.25× |
| medium | end_to_end | 120 | 100 | −16.7% | 1.20× |
| large | end_to_end | 200 | 220 | +10.0% | 0.91× |
| kernel | kernel_only | 20 | 10 | −50.0% | 2.00× |

定义：耗时变化 = (candidate/baseline − 1) × 100%；正数表示更慢。加速比 = baseline/candidate；大于 1 表示更快。未对不同 workload 或计时范围求总体加速比，未增加样本、置信区间或误差棒。

图 1（figure_v2）：v2 快照中基线与候选的报告耗时。左栏为三种端到端工作负载，右栏为 kernel-only 记录，两栏使用一致的 ms 纵轴且均从零开始。数值标注对应 CSV 第 2–5 行；每行仅有一对报告值，底层重复次数及不确定性未知。未假定 kernel 行对应左栏任何具体 workload，也未从中分解端到端开销。

证据：RES-C001→small/medium；RES-C002→large；RES-C003→kernel。图源与正文共用 metrics.csv，来源哈希见 analysis_manifest.json。
