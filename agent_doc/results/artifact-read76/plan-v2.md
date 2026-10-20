# ARTIFACT-READ-76 冻结方案 v2

完整基础DAG、权限、接口、文件归属和资源见 plan.md v1，v1不可变保留。
本版在任何实验前澄清验收，替代v1的含糊聚合定义。无托管引擎/长期监督部署主张。

- 小文件快速路径同时要求 stream.seekable()；非seekable沿用原read(LIMIT+1)，
  不把S_ISREG自动等同可seek。可seek但后续seek失败会显式异常，不返回截断结果。
- 每种输入五次交错配对，比较同一输入的median峰值。完整dispatch candidate
  median须小于baseline的0.1倍；所有稳定/增长/缩小文件case candidate median
  须<=baseline median的1.01倍。逐次原始值全保留，任何语义失败立即不通过。
- 至少两次预热不计样本；主控和独立复测不重叠，单测试进程串行。
- 每个结果保存源码hash（baseline与candidate）、Python/platform、输入长度/hash、
  输出hash或异常类型/消息、完整dispatch request hash和排除临时根路径后的packet hash。
- 标准库unittest负责语义；独立审核者另写held-out probe，不仅运行生产者脚本。

## 六项预冻结验收

1. implementation：独立读取实际diff、_bytes→_bound→prepare_dispatch及legacy consumers；
   同fd、有界最大read、后置长度/hash检查不变；不藏额外无界读取；全部满足才pass。
2. reference_boundary：固定SHA基线与候选对同文件内容、同fstat后注入分别执行。
   空/边界/大/增长/缩小、非法路径/FIFO/符号链接、stale和legacyhash结果一致；
   exact bytes或异常类型/消息必须全部一致；新增非seekable包装器验旧路。
3. data_integrity：逐一核对输入及代码hash、5个原始样本、执行命令和fixture位置；
   无漏项/更改预算/测量区fixture构造，全部行可由脚本复算。
4. numerical_sanity：峰值是有限非负整数bytes，使用median和1-candidate/baseline；
   没有RSS/wall/模型质量/端到端推理含义，不把0耗时或局部量当全链收益。
5. measurement_validity：tracemalloc覆盖完整函数调用，不含fixture/数据构造；
   两侧同CPU/输入/预算/计时口径、预热和配对；满足上述主/非退化阈值。
6. reproducibility：独立上下文核对旧负结果与新候选，并重跑完整dispatch及增长；
   targeted/full/Reader无新增失败；任何必要项目未跑则inconclusive，阻止发布。

所有六项均适用，不允许N/A。producer → 独立verify_experiment_result → report/publish。
绑定文件：plan.md、plan-v2.md、实际源码、tests/test_result_read_allocation.py、
scripts/benchmark_artifact_read.py、raw.json、before.log、after.log、full-tests.log、
reader-tests.log及审核者独立文件；实际hash仅在文件真实产生后记录，不预填假值。
验收后改实现/输入/协议须新版本和独立复验。研究沿用已有十篇阅读，不计新增十篇。
