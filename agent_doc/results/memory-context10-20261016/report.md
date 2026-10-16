# MEM-CONTEXT-10：完整记忆上下文闭包一次打包

基线 main `4a19ee121eb283a5364bf8fff4aa146c8f5deec8`。问题位于
`agent_runtime/handoff_basis.py:274–292`：每代 pending 都调用会完整遍历祖先的 check，
长链重复读取/JSON解码接近平方级。32节点修前专项记录528次 hydration（门槛160）失败。
修复在 `project_memory.py:160–199,313–332` 用既有严格遍历返回完整有效闭包，
只在内置 ledger 的上下文打包路径使用，一次 SQLite 只读事务覆盖闭包；不保存跨调用缓存。
普通 check 仍仅保留请求根，初始验证、known IDs、状态/document gate、排序、完整内容和预算保持。
定制 public check/get/check/walk/connect、document checker、SQLite connector/Row 及替换 ledger
回退原有逐代调用路径；两项追加兼容保护后的正式源码与测试见归档及 manifest 哈希。

## 实测与验收

实际完整 basis_context CPU wall（包括连接、检查、hydration、JSON打包），同数据库/输入hash、
max_chars=200000、3对warmup、21对随机AB/BA（seed81610），每次完整packet逐字节等价检查在计时外。
输入是合成96节点链/每节点依赖前两个节点的共享图；原始输入/输出hash逐样本见raw。

|场景|主测baseline→candidate中位ms|下降|独立baseline→candidate中位ms|下降|
|---|---:|---:|---:|---:|
|chain96|63.118499→3.627724|94.25%|63.245211→3.743069|94.08%|
|shared96|33.681154→3.770626|88.80%|34.845736→3.811772|89.06%|
|small3|1.467878→1.213190|17.35%|1.514331→1.282018|15.34%|
|no_memory|0.020420→0.020311|0.53%|0.020931→0.020941|-0.048%|

冻结主测门槛各≥25%、每控制退化≤15%全部通过；无trim、未改变预算/选集。
首版v1及独立preguard计时保留为superseded，不作为最终候选接受依据。
首次专项4项修前1fail、修后4pass；补守卫后6pass，已有handoff20pass。
独立差分包含35随机DAG、多根/重复共享/known ID、selected claim、文档变化、损坏/缺失/
required precedence/预算/自定义接口等；实际检查范围和最终源码绑定以 result-review.md 为准。
最终全库1235项运行（8跳过）、Reader3项通过，-O专项6项通过；源码前后hash相同。
实际原始结果见 final-regression.json。

## 边界与研究应用

采用记录依赖闭包的局部计算思想，参考已阅读的[ATR](https://arxiv.org/html/2609.08015v1)，
保留其适用前提：依赖必须完整、验证器必须可信。这里仅消除重复计算，未复制论文系统/数字，
未放宽旧记忆失效规则。历史12论文矩阵继续保留；本轮不冒称新增精读10篇。

等价性范围是不可变同状态；闭包的单次SQLite快照更一致，但完整basis_context包含之前的
根检查、known-ID检查和文件文档读取，不能声称跨这些步骤/外部文件/并发writer的全局原子性，
也不声称复现旧多事务的所有并发交错。无跨调用复用，后续调用继续检查stale。
未测峰值RSS；完整payload本来就需保留闭包，新增遍历返回列表/映射有临时内存成本。
没有JIT、CUDA kernel或GPU驱动参与；环境见environment.json。
本轮不是LLM KV tensor缓存、模型QA、真实请求TTFT/吞吐提升；没有真实模型后端新结果。
旧性能实验数据不改写；重测范围仅本功能及全库回归，父任务MEM-STORAGE-01保持打开。

脚本为实际私有run内执行版本（ROOT按.agent-runs层级定位）；复现时将本目录脚本与baseline
复制至仓库.agent-runs/<run>/再执行measure.py。独立脚本需恢复子目录结构：
reviewer-measure.py、reviewer-verify.py、reviewer-boundaries.py分别放入
.agent-runs/<run>/reviewer/measure.py、verify.py、boundaries.py；独立计时结果写在该reviewer子目录。
勿直接在结果目录运行。
所有验证为人工独立上下文的有界复核；未伪造受管ReviewSession/host supervisor。
