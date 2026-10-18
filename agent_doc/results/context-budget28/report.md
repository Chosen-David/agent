# CONTEXT-BUDGET-28：不装配必定超预算的完整依赖包

基线：`5b1765cb1e228dff27794ca067171fd2f31c0d3a`。位置：`agent_runtime/knowledge.py:302–309` 与独立插件镜像。真实调用链：knowledge CLI context → 构造/验证 KnowledgeStore → search 或 indexed_search → context → get/完整依赖闭包 → payload装配/预算检查。候选仅在条目数已确定超预算时跳过后续装配，不改变检索、排序、依赖完整性、字符预算、返回顺序或skipped原因。

发布范围：大批原始样本、progress日志及全库逐项日志仅保留在执行工作区，未随git公开；下文raw.json/progress.jsonl/full.log等是原实验本地证据路径，不是本提交可下载附件。公开简报、独立审查、短测试日志及复现脚本；独立审查保留原始文件hash。缺少原始样本的第三方不能仅靠简报重新计算统计或自动复用结果，应自行执行新run。

## 根因与改变

原代码已得到未选依赖列表，却仍逐成员调用get（再遍历其前置闭包）、JSON复制、序列化，最后因条目预算丢弃。n层链上的这些额外闭包访问可达二次规模；新分支仍保留原始seed get/完整闭包，只有必定拒绝时省掉后续工作。不是对任意DAG证明总复杂度线性，也没有跳过来源/版本校验或缓存结果。

修前结构回归：21节点chain/fanout + 后续可容纳seed，共24次get；修后3次。before.log保留2个子例失败，after.log为4项通过。原程序返回内容本来正确，此项是性能浪费修复，不冒称修复功能错误。

## 公平对照

同机Python3.12.14（Clang22.1.3），Linux6.18.55 x86_64/glibc2.39，容器暴露9逻辑CPU，Intel Xeon Platinum8573C。无宿主独占保证，无GPU/模型调用。每例2对warmup、11对AB/BA；perf_counter_ns，候选中位数/基线中位数。16例及完整门槛在稳定Plan中预先固定。构造/建语料不计入context-only；load-search-context包含每次新store、校验、搜索与装配，imports排除、OS页缓存不清空，不能称磁盘冷启动。

独立复测（主控无同时测速）：

| 合成输入 | context基线→候选 | context耗时下降 | 加载+检索+装配基线→候选 |
|---|---:|---:|---:|
| 100节点、预算20 | 9.320→0.258 ms | 97.23% | 39.168→29.429 ms |
| 300节点、预算20 | 57.012→0.823 ms | 98.56% | 158.273→97.402 ms |

两目标与其余14控制在生产者、独立轮均达门槛；不以目标收益代表全部请求。真实语料混合查询context独立轮 **4.164→4.391 ms（+5.45%）**，量纲完整流+0.85%、无命中完整流+2.54%，均未超预定10%或0.2ms容限；保留全部样本，不称所有场景提速。真实语料`matrix` context两轮改善，但本轮不外推为任务总延迟保证。

独立tracemalloc另测（非RSS）：100节点579005→19214 bytes；300节点1745206→59215 bytes。输入内容hash、源码hash、快照、完整逐对样本及输出hash在producer/raw.json与independent/raw.json。progress.jsonl保留逐项差分与已完成计时对；不与计时样本混算。独立轮22.140s，timeout900；最初/usr/bin/time缺失日志保留，随后Bash time正常执行。生产者同样受timeout900限制，未另记整段elapsed，不能补造。

## 正确性与边界

每轮750项完整JSON差分、11项异常输入比较的类型/消息一致；chain、fanout、共享已选依赖、重复skipped seed、后续可装下seed、related开关及字符恰好边界覆盖。独立另选27项错误/顺序/构造器边界；源码/完整语料清单/镜像/样本覆盖和统计重算见independent/review.md与independent/extra-verification.json。

仅适用于构造器验证后的未外部篡改snapshot；任意直接records修改、猴子补丁或外部并发篡改不在契约内。原始12篇研究矩阵仅历史依据，本轮AgentIR相关章节是方法筛选，不声称新精读10篇或复刻算法。无真实Agent任务成功率、LLM质量、token/费用或服务部署收益结论。

## 复现与后续

全库回归：1281项，107.737s，OK（8 skipped）；Reader回归3项，1.626s，OK。专项4项通过，插件镜像一致及引用同步检查通过。全库短日志见full-summary.log，完整full.log留在本地；reader.log、after.log公开。这些测试不证明真实模型任务质量或宿主集成。

```bash
PYTHONHASHSEED=0 python scripts/benchmark_context_budget.py --out agent_doc/results/NEW_RUN_ID
python -m unittest tests.test_knowledge_context_budget -v
```

代码/Plan/语料改变应新run，不修改旧原始证据；原冻结版本的独立复算脚本依赖未公开原始样本，未作为直接复现命令。独立人工上下文不等于native ReviewSession或tmux部署；受管路径仍缺host adapter。本轮已完成回归，待通过用户直接授权的人工维护路径发布；发布与远端回读由主控记录于任务Progress或发布检查点。
