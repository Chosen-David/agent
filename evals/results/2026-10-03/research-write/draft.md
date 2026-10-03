# 通用工作稿：选择性执行

本稿仅描述输入中的合成测试材料（synthetic fixture），不代表真实系统的实测研究结论。未指定投稿 venue；未增加文献或实验。

## 中文结果段落

在所提供的合成测试材料中，替换选定内核后的端到端表现随工作负载而异。材料说明所有计时使用相同的 CPU 进程和输入配置，每个数值仅代表一次运行。small 工作负载的端到端耗时由 100 ms 降至 80 ms，耗时减少 20.0%，对应 1.25× 加速；medium 由 120 ms 降至 100 ms，耗时减少约 16.7%，对应 1.20× 加速。large 则由 200 ms 增至 220 ms，耗时增加 10.0%，对应约 0.91× 的速度比，表明该配置出现性能退化。因此，这些记录不支持原稿中“所有工作负载均有 2× 端到端加速且无退化”的表述。

独立计时的内核耗时由 20 ms 降至 10 ms，即耗时减少 50.0%，对应 2.00× 的内核级加速。该内核计时部分已经包含在端到端路径中，不能再与端到端耗时相加，也不能将内核级加速直接表述为端到端加速。现有记录展示了两个端到端配置的耗时下降和一个配置的退化，但没有独立重复运行、方差或质量测量，也没有 GPU 测量。因此，无法据此判断收益的统计可靠性、质量影响或 GPU 表现，也无法解释 large 配置退化的具体原因；结论仅限于所提供合成材料中的单次运行记录。

## English abstract

We examine selective kernel replacement using a supplied synthetic fixture with CPU timing records. Each reported value represents a single run, and the manuscript states that measurements use the same CPU process and input configuration. End-to-end latency decreases from 100 to 80 ms for the small workload and from 120 to 100 ms for the medium workload, corresponding to latency reductions of 20.0% and 16.7% and speedups of 1.25× and 1.20×, respectively. The large workload regresses from 200 to 220 ms, a 10.0% latency increase. Independently timed kernel latency decreases from 20 to 10 ms, yielding a 2.00× kernel-only speedup; this timing covers a component already included in the end-to-end paths and must not be added to them. These records demonstrate workload-dependent outcomes within the fixture and do not support universal 2× end-to-end acceleration or regression-free performance. Independent repeats, variance estimates, quality measurements, and GPU measurements are unavailable. The findings are therefore descriptive of the supplied single-run synthetic records and do not establish statistical reliability or general performance benefits.

## 主张证据表

数值口径：速度比/加速比 = baseline_ms ÷ candidate_ms；耗时变化 = (candidate_ms − baseline_ms) ÷ baseline_ms × 100%。负的耗时变化表示耗时下降。CSV 行号包含表头；所有输入版本见 writing_report.md 的 SHA-256。

| 主张 ID | 主张与判断 | 证据 ID 与位置 | 指标、适用范围与限制 |
| --- | --- | --- | --- |
| WRITE-C001 | small 耗时降低 20.0%，加速比 1.25×；在材料内支持 | WRITE-E001；measurements.csv 第 2 行 | 100→80 ms；end_to_end；单次合成记录 |
| WRITE-C002 | medium 耗时降低约 16.7%，加速比 1.20×；在材料内支持 | WRITE-E002；measurements.csv 第 3 行 | 120→100 ms；end_to_end；单次合成记录 |
| WRITE-C003 | large 耗时增加 10.0%，速度比约 0.91×；在材料内支持 | WRITE-E003；measurements.csv 第 4 行；manuscript.md Appendix A | 200→220 ms；end_to_end；明确保留负结果；原因未测量 |
| WRITE-C004 | 内核耗时降低 50.0%，内核级加速比 2.00×；在材料内支持 | WRITE-E004；measurements.csv 第 5 行 | 20→10 ms；kernel_only；不能推广成端到端收益 |
| WRITE-C005 | 内核计时独立获取，但该计时部分包含在端到端路径中，不相加；材料直接说明 | WRITE-E005；manuscript.md Results | 输入材料的计时口径说明；未独立核验计时代码 |
| WRITE-C006 | “所有工作负载均有 2× 端到端加速且无退化”不受支持，已改写 | WRITE-E001–004；manuscript.md Abstract | 三个端到端速度比均非 2×，large 退化；仅内核级达到 2× |
| WRITE-C007 | 缺乏重复运行、方差和质量测量，不能推断统计可靠性或质量影响；材料直接说明 | WRITE-E005、WRITE-E007；manuscript.md Results、Appendix A | 不进行显著性、等效性或质量不变判断 |
| WRITE-C008 | 相同 CPU 进程与输入配置，无 GPU 测量；材料直接说明 | WRITE-E006；manuscript.md Method | 仅按方法文字转述；无硬件型号、运行日志或 GPU 证据 |
| WRITE-C009 | 输入是合成测试材料，不是已发表论文；材料直接说明 | WRITE-E008；manuscript.md 开头 | 不作为真实系统实验或发表记录 |
