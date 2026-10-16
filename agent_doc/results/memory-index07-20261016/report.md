# MEM-REVERSE-INDEX-07：持久反向依赖索引

基线 `a73bf13424bdd789284eeac6d5664bea5d104574`；最终实现 SHA256
`7df8e23ecee946e996b828fb702258e03dabe2306b42c63a3daadf15008d950e`。
改动位于 `agent_runtime/project_memory.py:87–88`：初始化 dependencies 后幂等创建
`memory_dependencies_parent(parent, child)`。保持原 `(child,parent)` 主键。
这是现有记忆来源/失效依赖图的工程索引优化，不是新的论文算法或模型 KV 实现。

## 触发条件、根因和边界

`impact → _descendants`、`correct → _revise → _descendants` 按 parent 找 child。
此前 schema 只有反方向主键，实测 SQLite 查询计划为起点 SCAN、递归 AUTOMATIC
COVERING INDEX；这不等于每层全表扫描。持久覆盖索引让起点和递归均做 parent 查找，
避免每次语句重新建临时索引。原始 EQP/pragma/schema 保存在压缩 raw 中。

依据 [SQLite 官方优化器 §14](https://www.sqlite.org/optoverview.html#autoindex)
核验临时自动索引生命周期；2026-10-16读取。历史研究沿用
[12篇论文矩阵及适用边界](../memory-storage-20261015/research.md)，后续 MemForest
阅读提出的来源/派生状态分离只作为约束，不将反向索引包装为其论文复现。
本轮没有新增十篇精读记录，也不重复计算既往阅读量。历史检索扫描200条且partial=true、
59项解析错误；命中无关，未复用旧性能。知识卡 maxflow/FAISS/HNSW 假设不适用，未采用。

## 冻结计量和实测

AMD EPYC 9V74容器，Python3.12.14、SQLite3.53.1，Linux6.18.44；未锁频。
一进程串行CPU，21对随机AB/BA、每臂3个独立副本热身；5000节点、128B内容、
短链16与其他不相关链、固定输入hash。计入完整公共API连接/校验/事务/全部对象装配/
提交/返回。拷贝、DDL、完整状态比对在两臂计时外；仅合成温缓存结果，不代表冷盘或真实任务质量。
每样本时间戳按新entry/event身份验证后归一化，既有值不可忽略；返回和所有业务表一致。
指标为 `1 - median(candidate)/median(baseline)`；不删异常值、不平均抵消控制退化。

| 完整API场景 | 主测耗时下降 | 独立复测下降 |
|---|---:|---:|
| impact，5000节点仅15后代 |59.72%|47.95%|
| correct，同一稀疏图 |47.03%|36.25%|
| impact，16节点短链 |−0.24%|−0.71%|
| correct，512个直接后代 |0.79%|−0.12%|
| add，既有5000节点 |−5.04%|−9.23%|

双主各≥20%、每个控制退化≤15%均通过。索引不是普遍加速：大失效集合由逐行装配/更新
主导；写入多维护一个索引，已有add的退化如表。输入hash、全样本、顺序、DDL账、
原始schema及时间戳见 `raw.json.gz` 和 `reviewer/raw.json.gz`，无损解压哈希见compression.json。

实际生产初始化/CLI另测21对（seed71407）并保留旧源码独立module globals：

| 含全部初始化的真实入口 | 基线中位ms | 候选中位ms |
|---|---:|---:|
| 已升级账本的完整CLI add |2.341841|2.348000|
| 旧账本首次升级+CLI add |2.183406|3.378342|
| 仅构造器首次升级 |0.697417|1.629011|
| 仅构造器重复初始化 |0.689905|0.669855|

CLI包含argparse、create=True、add事务和JSON输出，未计Python进程启动；稳态退化0.263%
在15%控制门槛内。首次CLI升级增加约1.195ms，不能宣称第一次请求即获净收益。
单独索引DDL连接/提交/关闭在5000节点主测中位约1.04–1.23ms；文件1773568→1880064字节
（+106496字节），不是免费缓存；没有测RSS/峰值内存、吞吐、GPU、模型KV、token、QA或TTFT。

## 升级和兼容性

实际 `MemoryLedger(root, create=True)` 添加索引；旧库普通构造/读取继续可用，不静默迁移。
现有CLI add原本就create=True，因此可能在业务校验失败前升级schema；无CLI init命令。
重复初始化幂等，条目/依赖/文档绑定/事件/sqlite_sequence不改，错误传播及业务回滚保持。
首次索引需要写锁/空间；不承诺现有executescript初始化全程原子。
未知同名索引不会被drop/rebuild；IF NOT EXISTS不验证结构，此类自定义schema不适用收益结论。

## 验证及保留失败

新增4项真实SQLite回归修前3fail、修后4pass；覆盖新库、旧库只读、重init、CLI、同名错误索引。
诊断独立验证60组含循环/共享节点的可达性oracle、完整packet/时间戳负向探针、失效传播/
superseded保护/事件历史、插入前与写入后回滚。
原probe的附加rollback fixture没有有效后代，未触发预期异常，发生在五组全部计时保存之后；
原producer/log完整保留，validate.py补充active c后代验证，未重写已测数据或放宽门槛。
独立核验脚本自身两次预期错误也保留，不把工具退出成功等同科学验收。
最终源码/集成审查、全库/Reader/-O结果见后续冻结verification与独立报告。
人工限定范围审查，不宣称受管ReviewSession、自动可信回执或模型推理收益。

## 复现

`probe.py`、`validate.py`、`reviewer/probe-independent.py` 为**旧源码诊断**入口：
在独立检出的基线a73bf13工作目录运行它们，Python从cwd导入旧实现；不要在已装索引的新源码
下运行诊断并称为原baseline。probe.py末尾原oracle失败是保留历史；独立probe只跑计时，
validate.py单独补语义检查。计划文件在脚本旁保留。`integration.py` 从同目录baseline.py加载
原实现，再与当前生产实现比较；在最终源码checkout目录运行，输出在脚本旁，请先复制到临时目录
避免覆盖冻结证据。gzip解压后的字节hash可用compression.json复算；原始路径与哈希映射供审计。

MEM-STORAGE-01继续：真实模型KV消费者、跨会话任务质量与完整请求成本尚未验证。

最终串行回归：1218项运行、8跳过、零失败/错误（63.067s）；Reader3项通过；
`python -O` 记忆专项36项通过，TestResult写入JSON避免既有测试捕获summary输出。
首次全库仅generated plugin引用不同步失败，现有生成脚本同步3份后完整重跑通过。
见verification.json、完整日志压缩件与独立实施审查。
