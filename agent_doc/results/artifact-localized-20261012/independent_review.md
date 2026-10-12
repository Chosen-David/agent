# ART-LOCAL-01 独立结果验收

## 结论

**FAIL，不可消费。** 候选实现的精确恢复与性能改善在本次范围内均得到复核，但冻结验收条件还要求“最终 wire 相比基线不增大”。独立的 3,016 个案例、两种选择模式共 6,032 次完整入口检查中有 16 次 wire 增大，因此该结果不能标记为 `usable-with-scope`，也不能据此合入或发布性能结论。

本结论只否决当前版本及当前验收合同，不表示首尾裁剪思路不可修复。原始生产测量和本次失败证据均应保留。

## 绑定与执行对象

- 基线提交：`71496c7b1f42b94616343683c7671b6a0e6e8a3b`
- 当前候选源码 SHA-256：`21636fec2f09f526dd1ad864f6743760331f6664047ea72c3d6e4d1298f2d6fe`
- 基线源码 SHA-256：`e533244e68e698cb95f298bd04ce5e63727dd2cf485e4f731805883191b3e30f`
- manifest SHA-256：`b7702913755d1e8e9da031a320eb7cf8c24e64723401d8fc3e2e7cf1d200f1fe`
- validation plan SHA-256：`86e1c2c815ade3a8a59c83a6500c35b4f377ed7a540e6689969fc6a2c6a1323e`
- 生产测量 SHA-256：`350d899b68172b28bd715d9ec6c9b993404744140d429b4fe84c7ba52c5d21bb`
- manifest 引用的 9 个文件逐一重算，0 个哈希不匹配；scope 与 validation plan 一致，metrics 与 `measurement.json` 一致。

## 六项验收

| 检查 | 结论 | 证据 |
| --- | --- | --- |
| implementation | pass | 阅读真实 `compare_artifacts` 入口和 `_edits`；前缀 offset 通过 `start + a` 保持为完整 base 坐标，插入片段使用 `new[start+c:start+d]`，首尾扫描不重叠；65,536 字符与 2,048 行边界仍保留原回退。 |
| reference_boundary | pass | 独立 applicator 未调用 `restore_comparison`；覆盖空文本、无尾换行、CRLF、Unicode、头/尾/中间插删、重复行、阈值内外及随机修改，6,032 次均恢复到目标 SHA。 |
| data_integrity | pass | 生产 seed `8675309`、2,008 案例、4,016 检查、7 组配对样本与代码/工作负载哈希一致；独立 seed `190823`、3,016 案例、6,032 检查，无缺样本。 |
| numerical_sanity | pass | 生产样本均有限且非负；重算中位数为 619.523861 ms 与 1.868739 ms，降幅 0.9969835883367211，与记录逐值一致。 |
| measurement_validity | **fail** | 独立完整入口计时仍显著改善，但 16/6,032 个 packet 大于基线，违反“wire never exceeds baseline over at least 2,000 cases”。 |
| reproducibility | pass | 10 个聚焦测试通过；冻结生产脚本在不覆盖原始 JSON 的输出重定向下重新执行并通过断言；独立交替顺序 7 对计时通过阈值。 |

## 关键观测

### 语义与边界

独立 applicator 对 `full`、`identical`、`splice`、`edits` 四种表示分别校验 source SHA、行坐标、删除范围、非重叠次序和最终 target SHA。候选与基线的全部 6,032 个 packet 都恢复出准确的 `(before, after)`。

这说明当前失败不是数据损坏或 offset 越界，而是候选选择的非退化条件失败。

### wire 回退反例

重复行会使 `SequenceMatcher` 的对齐不唯一。裁掉共同首尾后，matcher 被约束到一个不同的合法对齐；该 patch 虽然能精确恢复目标，但可能比未裁剪基线更长，甚至改变最终表示选择。

- 案例 26（before SHA `da0ed9...3c69`，after SHA `56ea7c...e44`）：基线与候选都选择 `edits`，但插入锚点由 9 变为 10，最终 wire 从 1,010 增至 1,011 bytes。
- 案例 567（before SHA `bd5dd9...7235`，after SHA `d880ea...51b1`）：未计数路径从基线 `edits` 1,181 bytes 退化为候选 `full` 1,254 bytes；计数路径的候选 `edits` 为 1,205 bytes，仍大于基线 1,181 bytes。

独立语料共记录 16 次增大。`independent_raw.json` 保存前 10 次的稳定案例索引、输入 SHA、模式与字节数。

### 性能复核

生产记录重算：

- 基线中位数：619.523861 ms
- 候选中位数：1.868739 ms
- 降幅：99.69835883367211%

独立交替顺序 7 对计时：

- 基线中位数：591.336752 ms
- 候选中位数：1.649982 ms
- 降幅：99.72097421741174%

冻结生产脚本的保留输出重跑得到 584.662219 ms 对 1.701347 ms，断言通过。三组数字只支持指定的重复行局部单行变更 CPU 工作负载，不支持模型、token、成本、GPU 或端到端收益。

## 命令

```bash
python -m unittest tests.test_artifact_context tests.test_artifact_localized_diff -v
git diff --check
python agent_doc/results/artifact-localized-20261012/independent_check.py
```

冻结生产脚本还通过 `runpy.run_path` 在新进程执行；仅将 `Path.write_text` 对目标 `measurement.json` 的写入重定向，以避免覆盖已冻结原始测量，脚本主体、断言、入口与输入未改。

## 建议修复与重验

1. 当前候选不要提交或用于完成声明。
2. 优先把快速路径限制到能证明不会改变 matcher 选择/候选大小的输入子集；若要允许少量 wire 增长，必须先版本化修改 validation plan，不能在看到失败后静默放宽。
3. 修复后用新 result/run ID 重跑生产测量，并保留当前失败记录；独立复验应保留本次重复行反例及不少于 3,000 个随机案例。
4. 重新要求：独立 applicator 全部精确恢复、最终 wire 增大为 0、7 对交替计时满足既定 2x 阈值、全部聚焦与全量回归通过。

## 限制

- 仅 CPU、合成文本与当前 Python/Linux 环境；未使用模型、真实用户语料、GPU 或外部服务。
- 随机与构造检查不是全状态穷举；结论仅限当前源码哈希、manifest 和冻结 scope。
- 性能计时存在共享 CPU 噪声，但候选与基线差距远高于噪声；这不抵消 wire 非退化失败。
