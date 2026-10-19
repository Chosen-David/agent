# PROMPT-SCAN-69：精确行首扫描，降低提示词完整装配开销

日期：2026-10-20。基线 `38a6451306dba93fcf40d4c23391876471682891`。

## 发现、方案及边界

`agent_runtime/prompt_context.py:31–32` 在每个字符位置执行Python `startswith`。
真实调用 `scripts/prompt_context.py → compose_entries → _read/_span` 中，默认三个入口
加canonical共四次扫描；文本没有marker的绝大多数位置也执行Python调用。
改为 `re.finditer('^' + re.escape(MARKER), text, re.MULTILINE)`，仍收集全部命中。
后续Markdown fence/comment、歧义拒绝、内容/hash、去重与字符预算逻辑完全不改。
这是线性扫描的常数开销优化，不是新的压缩算法，也不改变LLM输入或预算。

新增测试修前：`Ran 3 tests; FAILED (failures=1)`，明确失败为
`AssertionError: per-character Python startswith remains`；其余两项语义测试通过。
该失败是性能结构哨兵，不是声称原实现产生错误内容。收益以完整装配实测为准。
修后提示词普通/`-O`各20项通过，Reader3通过；全库及独立验收见下方最终记录。

## 同机完整装配对照

CPU AMD EPYC 9V74，KVM，9个可见逻辑CPU；Linux6.18.55 x86_64/glibc2.39；
CPython3.12.14（Clang22.1.3）。不锁频/绑核，无GPU/模型调用，不测峰值内存。
单进程顺序交错对照，基线通过固定SHA加载完整生产模块，候选加载当前源码。
5次预热，7轮×20次，`perf_counter_ns`，包含文件读取/hash/选择扫描/装配及拒绝路径；
不含CLI启动、fixture创建、结果比较。使用热页缓存，未声称冷盘性能。
每个原始样本是20调用批次的每调用均值；表中median是7个批次均值的中位数，非单次延迟分位数。
两侧同 `max_chars=1000000`（非默认100000），默认三个entry、dedup开启。
放大场景每个文件添加50000个ASCII字符和LF，实际55174/64150/64652字符；
无通过放宽一侧预算换收益。文件hash、长度、候选源码hash、全部7轮原始值见
[benchmark.json](benchmark.json)，复现命令 `python scripts/benchmark_prompt_scan.py`。

| 场景 | 基线median ms | 候选median ms | 降低 |
| --- | ---: | ---: | ---: |
| 仓库真实三入口 | 3.646024 | 1.097385 | 69.90% |
| 每文件加50K字符合法前缀 | 16.693009 | 2.868701 | 82.81% |
| canonical无marker拒绝 | 0.464806 | 0.127587 | 72.55% |
| canonical重复marker拒绝 | 0.458935 | 0.132520 | 71.12% |

预先设定真实入口≥10%改善，所有场景退化不得超过max(5%基线,50µs)，四项通过。
300次完整返回值/异常类型及消息差分通过，涵盖全部非空entry排列、dedup开关、
合法输出字符边界-1/等于/+1。测试另覆盖LF/CRLF/CR/NEL/U+2028/U+2029、NUL、emoji、
内联/重复marker、Markdown fence和注释。原始时延有调度噪声，不作统计显著性或
跨机器保证；不宣称端到端请求、token、内存、质量、GPU性能收益。

## 研究与历史复用

本轮使用research-implement-optimize技能要求的完整路径同预算实测，避免仅报告局部扫描。
2026-10-20定向重读 [AgentMemoryBench](https://arxiv.org/html/2606.06448)
v2（2026-09-22）§2.1/§3：分开记忆构建、检索、prompt装配与生成测量。
只迁移阶段归因方法，不采用其任务适配或借用其硬件/质量收益；本轮不是整篇新精读。
[Python3.12 re官方文档](https://docs.python.org/3.12/library/re.html)核对MULTILINE的
`^`仅对应字符串开始或LF后；非LF Unicode分隔符不可扩展成marker行首。

此前十篇精读保留于 [research_a.md](../read-boundary56/research_a.md) 与
[research_b.md](../read-boundary56/research_b.md)：AgentChaos、ACON、AgentFold、AgentFly、
Reflexion、MemGPT、Mem0、MemoryBank、A-Mem、MEM1。本轮复核这些记录，不冒称新增十篇。
未采纳有损摘要/自主记忆写回，因为会改变本路径逐字保留契约，且没有本库质量证据。

实际历史查询 `result_store.py search 'prompt span marker scanning' --limit 5 --max-scan 200`
返回scanned199、partial=true及缺record错误，非穷尽检索；候选不支持本扫描结论。
已读prompt-read67与content-copy60报告：前者证明拒绝读取分配，不证明扫描速度；后者是另一装配路径。
知识查询`exact text semantic preservation context overhead`仅得GPU/近似卡，不适用；knowledge_refs=[]。

## 独立验收与未完成事项

独立上下文prompt_scan69_review先完成七项方案审核，后签发
[usable-with-scope验收](independent.md)：10045个held-out差分通过，12输入hash与全部原始median核对。
独立串行复测真实入口3.399→0.829ms，四场景门槛全部通过；原始值独立保存在
[independent-benchmark.json](independent-benchmark.json)，不覆盖初测。全库1310（8skip）其余通过，
Reader3、提示词普通/-O各20通过，原始短日志见[tests.txt](tests.txt)。发布需另核最新main及远端树。
guide保持只读；没有tmux/受信长期host adapter，不声称部署持续监督DAG。
模型任务质量保持集、冷启动/冷缓存、内存峰值和其他主机复测均未执行。
