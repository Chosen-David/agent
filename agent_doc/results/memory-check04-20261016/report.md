# MEM-CHECK-04：缩短祖先内容驻留并解除校验深度限制

基线 main `2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10`；
`agent_runtime/project_memory.py:135–179` 的 `_check`，候选源码 SHA256
`c3f41593b64b09d2af190d9ddcb64bbf784720083f4b718a5bdaf5318109f159`。

## 问题与修复

依赖递归期间，每层 visit 的局部 entry 包含完整祖先 content，只有回溯才释放。
对深依赖且内容大的账本会同时保留大量不返回内容；有效1200层链还会触发解释器
RecursionError。无持久数据被修改或丢失；历史深链校验可能报错，不能把它解释为
记忆已失效。既有测量保留，不回写历史结果。

改为显式依赖迭代器帧，保持深度优先读取顺序；校验后只保留请求根，del局部entry。
没有提前展开宽图全部邻接节点；checked仍在访问父节点前设置，因此也保留损坏库
中原有cycle处理。refs校验、首错、来源文档检查、事务、schema及完整返回不变。
不跨调用缓存，不省略任何祖先验证。结构仍需O(V+E)，请求根全部内容仍需保留；
只是非返回祖先内容不再随调用栈累计，不能称为总内存O(1)。

## 固定实验与主测

方案v1经独立复核要求明确fixture/计时/GC/聚合，冻结config后v2 adopt才实现。
Python3.12.14、SQLite3.53.1、Linux6.18.44 x86_64/glibc2.39；本机CPU合成温缓存
SQLite，无GPU、编译器/kernel/模型配置。详细输入hash、每次AB顺序和原始样本在
`raw-primary.json`；建库和相等检查不计时。真实入口包括路径检查、连接、BEGIN、
全部读取/验证、返回和事务关闭。各臂warmup3，21对未tracing wall，另7对tracemalloc，
种子41016；每次GC在计时外。按各臂中位数比值计算，不挑最小值。

| 固定场景 | wall前→后 ms | Python峰值前→后 bytes | 峰值降低 |
|---|---:|---:|---:|
| 256层×16KiB内容 | 3.808→3.568 | 4522288→119862 | 97.35% |
| 单条小内容 | 0.316→0.319 | 8456→8095 | 4.27% |
| 64层短内容链 | 0.818→0.856 | 99760→40832 | 59.07% |
| 一个根的512个依赖 | 4.271→4.369 | 93682→93538 | 0.15% |
| 128个请求根 | 1.340→1.361 | 242517→242365 | 0.06% |
| 32层×4共享依赖 | 1.435→1.437 | 72904→48522 | 33.44% |
| 256层短内容链 | 2.420→2.295 | 353856→87222 | 75.35% |

预定主峰值下降≥70%通过；七场景wall退化≤15%通过，主测最差4.65%。
小库、宽图、多根没有可靠内存收益，也不主张通用吞吐加速。tracemalloc只观察
Python分配，不能代表RSS、SQLite原生内存、磁盘大小、GPU KV、任务QA或TTFT。

## 正确性、独立核验与复现

修前在固定基线加载新8项check测试：1项1200层链RecursionError，其余通过；
候选8项通过，20项memory相关通过。独立7733个差分比较完整返回或异常类型/文本
及_get顺序，另1024/1200层可靠性通过。独立原始数据/脚本和结论见同目录文件。
独立同协议复测主峰值下降97.35%，七场景wall最差退化2.33%；主内容链wall改善
3.98%，不把这点当通用速度收益。4例文档调用顺序及独立重建fixture/hash/随机顺序
复核通过；结论usable-with-scope，为手动新上下文复核，不是自动受管可信证明。
全库：1202项运行，8跳过，OK；`-O` memory20项通过，Reader3项通过。
缺真实模型服务的质量和KV实验证据保持未验证。

复现：

```bash
PYTHONPATH=. python scripts/bench_memory_check.py --config agent_doc/results/memory-check04-20261016/config.json --output /tmp/memory-check04-raw.json
python -m unittest discover -s tests -p 'test_memory_check.py' -v
python -m unittest discover -s tests -v
```

测试依赖对照commit可在本地git解析。此轮实际经典DFS生命周期修复，不冒称新论文
算法应用；新增两篇方法/实验阅读及拒绝直接迁移的原因见research-delta.md。
MEM-STORAGE-01的模型KV/真实任务质量阶段仍未完成。推送与远端字节核验由私有
发布检查点记录实际SHA，不在commit产生前虚构提交链接。
