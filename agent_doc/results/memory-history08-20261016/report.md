# MEM-HISTORY-INDEX-08：按条目索引完整审计事件

基线 `c854e274fea7e72a574bf1377d7f38679832812d`，最终源码SHA256
`3ab5bf98029e56ed98f1702bc0ee0fba19ef1176284fe440705b04b073d0422c`。
仅在 `agent_runtime/project_memory.py:97–98` 的create=True初始化脚本增加
`CREATE INDEX IF NOT EXISTS memory_events_entry ON events(entry_id)`。
`history`与其他公开API的代码、查询和返回契约保持不变。此为现有审计入口的工程索引优化，
不将SQLite索引称为新的论文算法。

## 实际入口与根因

CLI `history` → MemoryLedger.history → 完整_get条目 →
`SELECT * FROM events WHERE entry_id=? ORDER BY sequence` → 完整packet。
此前未索引entry_id，实测EQP为`SCAN events`；候选为`SEARCH events USING INDEX
memory_events_entry (entry_id=?)`。两臂都没有临时排序，不声称消除了基线排序。
sequence是INTEGER PRIMARY KEY，普通索引隐含rowid作为同键顺序；保留显式ORDER BY。
SELECT *仍需回表，因此不是覆盖索引。[SQLite官方依据](https://www.sqlite.org/queryplanner.html)
于2026-10-16读取。未发现内部agent_runtime历史消费链，仅有现成public API/CLI审计入口，
不能外推整个Agent运行时间。

本轮定向阅读TallyMem与CogMem的方法/实验及选读成本/失败分析，coverage和adopt/defer
见[research.md](research.md)。采用“来源事件保持完整、先核对实际消费者”的约束，
未加入模型生成DSL、语义图重写或摘要压缩。原有[12篇矩阵](../memory-storage-20261015/research.md)
保留历史身份，不重复计为本轮新精读。新索引不认证自然语言事件或科学真值。

## 冻结基准与全部代价

本地AMD EPYC 9V74容器，Python3.12.14、SQLite3.53.1、Linux6.18.44，未锁频。
单CPU进程，生产与独立复测串行；同一冻结fixture的两份新副本，21对AB/BA随机顺序
(seed81601)，每臂3次独立副本热身。计入完整公共API路径/连接/事务/JSON装配/全部行/
提交/返回；create=False对象在计时外，复制/DDL/对称预检/快照比较不计。只支持合成温缓存。
输入hash、完整packet及全部业务表的hash、原始时钟、schema/pragma/xinfo/EQP和顺序均保留；
完整对象在运行时逐字段比较，raw保留其hash而非全部对象实体。

| 完整API场景 | 主测耗时下降 | 独立下降 |
|---|---:|---:|
| history，50000事件首条目 |82.36%|72.81%|
| history，同图末条目 |82.71%|69.38%|
| history，16事件小库 |−8.16%|−2.28%|
| history，单条目512事件 |−6.20%|−2.71%|
| add，既有50000事件 |−2.51%|5.43%|
| correct，同规模15后代 |−3.38%|−2.91%|

首尾为同一类图的两种固定查询，不是独立用户群。单条目512事件为明确标记的schema-valid
重复事件压力fixture，不冒充public API自然生成的实际轨迹。两项主场景各≥30%、
其他每项退化≤15%的冻结门槛均通过；不平均掩盖退化、不删样本、不更换索引调参。
主测首查询2.729956→0.481665ms，末查询2.801913→0.484450ms；独立绝对时间不同，
只分别解释各轮配对比较。门槛通过不等于所有机器/负载有统计显著收益。

实际生产源码另测完整CLI main(add)，包括argparse、create=True初始化、add事务、
JSON格式化与对称StringIO输出；不含Python进程启动。seed81602、21对、3warmup，
同一50000事件add fixture，旧源码在独立module globals内执行。

| 实际入口 | 基线中位ms | 候选中位ms |
|---|---:|---:|
| 已装索引的稳态CLI add |2.378972|2.526353|
| 旧库首次升级并CLI add |2.437768|10.249791|
| 仅首次构造器升级 |0.862812|9.440863|
| 仅重复初始化构造器 |0.818416|0.836602|

稳态CLI退化6.20%，通过15%控制；首次CLI升级额外约7.812ms（约320%退化），
首次构造器额外约8.578ms。这些是保留的真实代价，不能用稳态history收益称首次调用净加速。
单列直接索引DDL含connect/commit/close，50000事件主测中位7.58–8.61ms。
账本15310848→16031744B，增加720896B（704KiB）；小库+4096B、512事件+12288B。
未测RSS/峰值内存、真实生产访问频率/吞吐、模型KV、QA、token或TTFT，不声称整体Agent提速。

## 兼容、独立验收与保留失败

create=True显式升级；现有CLI add原本就初始化，因此业务校验失败前可能已安装索引。
普通构造/history等读取不装新索引。旧条目/事件/文档绑定/sqlite_sequence和时钟完整保留，
重复初始化幂等；不承诺既有executescript全程原子。未知同名索引不被drop/rebuild，
错误结构不适用性能结论；table同名碰撞按真实MemoryError失败并保留业务行。

新增6项真实SQLite测试修前4fail、修后6pass，覆盖索引键、非空文档旧库升级、负sequence/
乱序插入/间隙/倒退时钟和大小写条目、失败CLI初始化副作用、未知同名对象。
独立诊断覆盖完整21对复现、七类hydration/error边界、完整packet/时钟负向检查、
public图的前置与写后回滚、superseded和stale历史。生产阶段另独立验证实际schema/xinfo
与诊断一致、非空文档升级、真实CLI及回滚；据此仅复用本轮已装索引后的未变API数据。
CLI21对原始数据另经独立重算，未声称CLI性能另做完整独立21对复测。
人工限定范围usable-with-scope，不是managed回执或已安装模型服务。

最终全库/Reader/-O结果及实施验收以verification.json和reviewer/implementation-result-review.md
为准；远端发布以实际SHA/tree读回为准。父MEM-STORAGE-01保持未完成。

## 复现与证据

raw.json.gz与reviewer/raw.json.gz为无损压缩原始数据，compression.json给出解压前后哈希。
所有计时、顺序、时钟、退化与schema保留；未改写既有实验记录。
`measure.py`及独立诊断在**基线c854e27的独立checkout工作目录**运行，从cwd导入旧源码；
不得在已装新索引的当前源码下运行后冒充基线。复制脚本及plan到临时目录防止覆盖冻结数据。
`integration.py`在最终源码工作目录运行，使用旁边baseline.py的独立模块和measure辅助函数；
seed显式使用旧类。重现环境、文件与执行/原始结果的绑定见manifest与独立报告。

最终冻结回归：1224项运行、8跳过、零failure/error（63.681s）；Reader3项通过
（1.558s）；`python -O`记忆专项42项通过（明确TestResult JSON）。生成引用检查与
git diff --check通过，最终生产源码仍为3ab5bf98。独立实施审查见对应报告。
