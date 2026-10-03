# 测量证据、噪声审查与补实验契约

review、implementation 和主调度共同使用；不增加新角色。图表消费者读取相同结论状态。现有 [实验执行契约](experiment_execution_contract.md) 负责执行与资源，本契约负责“数据允许什么结论”及下一轮判别实验。

## 先定位差值的来源和推断范围

小差值可能是真实有限数据差异、计时噪声、模型/解码 seed 波动、数据抽样或系统混杂；不能仅凭大小认定噪声，也不能凭正负认定优劣。固定数据/确定性 scorer 的差值可以是确切描述，同时无法证明新样本、模型 seed 或部署环境上的普遍改善。

定义 measurement unit、独立实验单位、配对键、嵌套/聚类层次和 estimand。一次进程/session 中成百上千次 timer loop 不等于成百上千个独立 model trial；同一文档的问题、同一用户/任务的样本可能相关；不同 seed × 相同样本是交叉结构，不能随意摊平。重采样/统计模型要覆盖声称的随机性层次；不机械套 t-test 或 bootstrap。样本级 paired resampling 要求合理抽样与配对；聚类 bootstrap 要按合适的独立 cluster 抽样，层级/交叉、多任务/非线性指标另设计分析。数据集固定枚举且没有抽样目标时只作描述，不编造总体 CI。

先报告 effect size 与单位：分数绝对点、percentage points、relative percent、ratio/speedup 不能混写。CI 表达估计精度，不是效果真实概率；非显著不等于等效，两组边际 CI 重叠不等于配对差异检验。只有一行汇总不能反推出方差/CI。预设实际意义、非劣或等效界限及依据，不事后用看到的 delta 定界。

## 冻结证据包，再看结果

最小包：claim_id/源位置、代码/数据/模型/环境/配置指纹、raw paired outputs/timings、ID/cluster/session/seed、测量单位与方向、scorer/metric 聚合规则、研究对象/抽样方式、缺失/失败记录。区分原始执行证据、由记录推导、静态声明、合成测试和未知。

预先固定主要比较、完整比较族、候选选择/调参历史、holdout、outlier 规则、样本量/停止规则和 precision/power 计划。多种模型/任务/形状/超参挑最好者不能按单个 primary comparison 宣称确认性证据；说明多重比较校正或新确认集。不用 test 选超参再在相同 test 上验证；不边加样本边看到显著就停。合理序贯设计可以使用，但必须用相应推断而非固定样本 CI。

precision 计划先说明期望 CI 半宽与最小实际差值，依据独立 pilot 或可信历史方差、聚类相关和每独立单位成本决定固定样本量；或用与分析匹配的前瞻 power/simulation 计划。样本/预算不足时保留 inconclusive，不给所有任务统一“跑三次”“n≥30”“80% power 就够”的魔法数字，不用观察到的 effect 算 post-hoc power 来证明结果可靠。

## 性能与准确率的不同采样计划

- 性能：匹配硬件/软件/shape/长度分布/batch/precision/layout/线程，记录 warmup、编译/autotune/cache、同步/stream/graph、计时边界。冷启动与稳态分开；performance exclusion 依实际调度器证据，不由 idle 快照证明。基线/候选随机化或交错配对控制漂移，跨独立 session/条件重复，保留分布与预定异常值处理；不能只给最小值、只丢候选慢点，或者把不同工作量计时混比。计时单位、timer resolution 与 loop/session 层级明确。
- 准确率：保留相同 example 的 paired outputs、seed、解码、prompt/截断、数据与 scorer 版本。按数据层次选择配对/聚类分析，保持 metric 的原聚合定义；macro 任务平均不等于 micro 例子平均。若主张涵盖 seed 泛化，采集独立 seed trial；若只涵盖固定模型在目标数据分布，不能把 seed 方差与 example 方差相互替代。
- 可视化：微小 delta 不靠截断轴、夸张面积/颜色宣称明显提升；必要时用明确标注的差值 panel、零线、界限与不确定性。图注说明单位、n 的层级、CI 算法及重复来源；未有 CI 不画虚构误差棒，未建立提升不标胜出星号。设计美观与统计可信分别验收。

普通任务只检查当前证据；完整合成 benchmark、模型盲测和全套回归只在开发/优化或用户明确评测时运行，不因使用本契约自动触发。

## 可执行审稿检查与有界分析

review skill 自带 `scripts/measurement_review.py`，同步到 implementation 和主调度 skill，离线可调用；同包 example 是公开合成数据。skill 根目录：

```bash
python scripts/measurement_review.py references/measurement.example.json
python scripts/measurement_review.py references/measurement.example.json --analyze --output measurement-result.json
```

默认只用标准库检查声明、原始行/ID/cluster、协议与计划字段，并输出可交接 redesign_tasks。字段齐全仅 `contract_ready_not_verified`，不是实测真实性或独立性证明。未知/不适用设计返回 needs_redesign，缺原始数据不产生 CI；畸形 JSON/非有限数拒绝。输出不覆盖已有文件。

`--analyze` 仅支持**单个预设主要比较、固定采样、独立 cluster 等权配对均值差**：先每行 candidate−baseline，再每 cluster 内求均值，再 cluster 等权平均，按独立 cluster 差值用 SciPy BCa 重采样。它不是任意任务 metric、加权/比例/中位数、时间序列、交叉 random effects 或多重比较分析器；配对与独立性的证据由审稿人核验，写 true 不能创造证据。

依赖已有 NumPy/SciPy（需要 bootstrap rng 接口，SciPy≥1.15；本轮实测1.17），不自动安装。固定9999 resamples、seed42、batch64、双侧95% CI；3 clusters 仅为数值下限，不是充分样本量。相同/退化数据与非有限区间拒绝，不把零方差合成复制值变成确定性结论。小样本 BCa 也可能覆盖不佳，应按分布/设计做敏感性或专门模拟，不能因库返回数字就认为适用。

输出差值保留 candidate−baseline，区间则统一 positive favors candidate。`criterion_met` 仅检验该双侧区间是否满足预设条件：superiority 下界>实际意义界限；noninferiority 下界>−界限；equivalence 全区间位于±界限内。后两项是保守的预设95%区间判据，不自称标准90% TOST 或万能显著性检验。另输出 `precision_met`；任一不满足则建议单独冻结的新确认实验或缩小主张，不能反复跑到满足。工具不输出 p-value 或“论文已证明提升”。

## 审稿 → 代码 → 回归复查

每条 REV 噪声问题输出：问题与主张位置 → 需要的 raw data/层次/配置 → 可排除的替代解释 → 配对/聚类/precision 分析方案及适用假设 → 独立单位数、资源/成本估算与停止条件 → CODE 脚本任务 → **采集前**的 acceptance criteria → 回传 receipt/失败样本 → 同 ID 复查。

只缺原始数据时先索取/恢复日志；无法恢复就降级为“此固定设置的观测差值，尚不能建立可泛化提升”，不凭汇总猜 CI。已有授权内可分析已有数据；新训练/模型评测/GPU session 仍需资源授权，审稿建议或生成计划不代表已执行。代码角色复用 experiment/gpu_adapter 的 manifest、资源准入、固定种子、不可覆盖输出，不擅改 metric 或测试集。审稿人独立检查实际执行与预案是否相符，允许撤销原意见和接受负结果。
