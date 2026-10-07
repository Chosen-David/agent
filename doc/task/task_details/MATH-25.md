# [MATH-25] 补齐有限softmax到value加权输出误差的证明、边界和迁移；筛选近期原始研究并接受独立数值审查

Task-ID: MATH-25
Date: 2026-10-07

## Plan

补齐有限softmax到value加权输出误差的证明、边界和迁移；筛选近期原始研究并接受独立数值审查。

## Progress

- 已同步 main ed6b7a2c，启动时干净且无本地同任务运行；按结果存储建议将新实验存 doc/results/，不移动旧证据。
- 本轮验证协议和 producer→独立verify→消费者 DAG 已在首次测量前冻结。见 `doc/results/math-softmax-20261007-v2/`。
- 未改生产检索/通信/attention算法，未改SGLang；模型与GPU验证不在本轮范围。

### 本轮证据

数学/来源、416+12有限验收、双后端4题、21旧题对照、66相关回归与限制见 [报告](../../results/math-softmax-20261007-v2/report.md)。发布前状态为validated/pending-publication，MATH-26不提前记完成。

### 发布读回

实现提交 `10aa87fc2a752fbcce8f149fffd6965906512b7c` 已直接进入 main，ref与完整tree读回一致；并发SELF-SYNC修改保留。737项全仓测试中729通过、8跳过。后续receipt提交仅保存这次已核实发布，不声称部署或模型收益。
