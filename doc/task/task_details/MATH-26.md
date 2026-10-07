# [MATH-26] 维护按需检索与学科/结构索引和引用成本，执行相关回归，刷新main直接发布并远端核对

Task-ID: MATH-26
Date: 2026-10-07

## Plan

维护按需检索与学科/结构索引和引用成本，执行相关回归，刷新main直接发布并远端核对。

## Progress

- 已同步 main ed6b7a2c，启动时干净且无本地同任务运行；按结果存储建议将新实验存 doc/results/，不移动旧证据。
- 本轮验证协议和 producer→独立verify→消费者 DAG 已在首次测量前冻结。见 `doc/results/math-softmax-20261007-v2/`。
- 未改生产检索/通信/attention算法，未改SGLang；模型与GPU验证不在本轮范围。

### 本轮证据

数学/来源、416+12有限验收、双后端4题、21旧题对照、66相关回归与限制见 [报告](../../results/math-softmax-20261007-v2/report.md)。发布前状态为validated/pending-publication，MATH-26不提前记完成。
