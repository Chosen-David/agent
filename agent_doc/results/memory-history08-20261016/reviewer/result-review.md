# MEM-HISTORY-INDEX-08 诊断独立结果核验

**结论：usable-with-scope，仅限本轮固定源码/六fixture的临时schema诊断。** 已向父执行者明确可进入事先批准的条件式实施阶段；这不是生产源码、迁移或发布验收。人工另行派发的独立审查，无managed receipt、受管ReviewSession或自动信任声明。范围仅Agent的public history/CLI history审计接口，不代表内部runtime检索或模型KV。TwoLevel暂停。

## 固定身份与实际工作

基线`c854e274fea7e72a574bf1377d7f38679832812d`，诊断源码SHA256 `7df8e23ecee946e996b828fb702258e03dabe2306b42c63a3daadf15008d950e`，已保存diagnostic-source.py。原measure.py逐字节另存producer-measure.py；计划、原始/复现数据、代码/环境及独立探针绑定在evidence-hashes.json。父在诊断接受前未改生产源码。本审查者只写分配的reviewer目录，未改源码、测试、计划、文档或guide，未调用模型/GPU/API/网络。

实际读取plan、plan-review、measure.py、基线初始化/_get/_connect/history/CLI入口、原raw/measurement.log、环境、真实prior/knowledge检索结果。历史检索partial/error和不匹配知识均不用于新性能接受；旧反向索引轮数值未复用。论文动机/阅读量不是本次代码数据审查认证的对象。实际source搜索未见内部runtime对MemoryLedger.history的调用；结论只限定公开审计接口，不能证明所有外部消费者不存在。

独立复现命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-history-20261016-1601/reviewer/measure-independent.py`。仅改输出目录、plan读取路径与临时目录，输入/调用/顺序/阈值/代码算法不改；同原计划21对seed81601随机AB/BA、3对新副本warmup、每样本一次完整public API，完整附加rollback验证也执行。未另试候选/调参数。父暂停测试/计时，独立计时开始08:08:58 UTC，脚本约133.01s，结束后发送timing-done；随后才做数据及语义探针。生产脚本约127.33s。二者均在本次约08:04准入起的25分钟本地预算内完成。未绑核/锁频，其他宿主干扰不能完全排除。

## 计时范围、输入和原始数据

全public API包含路径校验、连接/事务、完整entry hydration、events读取/写入、commit/返回；create=False实例构造在计时外。copy、额外schema/EXPLAIN、DDL和完整快照相等检查在计时外且两臂对称。预检完整逻辑数据使两臂为温缓存，候选DDL另测connect→execute→commit→close。不是SQL微基准、冷盘、CLI/进程启动或初次迁移净收益计时。

data_verify.py独立用Python数据结构再生成六组完整预期输入：entries、dependencies、document_dependencies、events、sqlite_sequence及固定旧时钟，生产/独立input_hash全部匹配。两个50000场景为同类型单created-event账本的首/尾entry，不是两个独立用户群。many512为一个stale entry、一次created与511次重复stale的schema-valid压力fixture，未称为公开API自然生成历史。correct仅首16节点为链、其余隔离，预期exact affected n00001..n00015；add无依赖，调用参数符合冻结计划。

原始/独立两次合计504个计时样本（每次6×42）全部保留。独立检查每fixture恰好21个pair×双臂、warmup消耗后的RNG顺序、正有限ns/API、精确中位数/比值和门槛；每pair完整output/state SHA一致。所有表及sqlite_sequence均参与状态比对，history每臂API前后DB物理字节不变、state==old，返回events精确等于目标entry的固定旧事件列表。这些完整运行期断言在独立重跑实际通过；原raw仅保存输入/输出/状态hash，不含每样本完整packet/物理前后hash，不能说原raw保留了这些实体文件。

仅new-entry/revision及seed最大sequence之后新event的created_at被规范化。独立检查每个原始新时钟严格SQLite UTC格式/可解析、确切新身份、新event sequence完整连续且数量正确（correct共18个新事件，加一个新entry时钟）；旧时钟由harness逐行精确校验。sequence、action/source/reason/related_id等字段均未忽略，constructor升级数据以后必须全部精确保持，不适用本诊断新业务clock规则。

## 实际机制及参考边界

生产/独立实际EQP一致：baseline `SCAN events`，candidate `SEARCH events USING INDEX memory_events_entry (entry_id=?)`；两者均无临时排序B-tree。原sequence INTEGER PRIMARY KEY AUTOINCREMENT是rowid别名，索引xinfo精确为entry_id键+BINARY升序，以及隐式rowid辅助项；非唯一、非partial。**SELECT *不是covering index查询；未消除一个不存在的baseline排序。** 全部sqlite_master差异仅为`CREATE INDEX memory_events_entry ON events(entry_id)`，原reverse-dependency索引保留。automatic_index=1、journal delete、4KiB页与关闭后的单DB文件状态已核对。

semantic_verify.py另用真实public-created图和非计时边界数据验证：

- 事件sequence按19,-5,100,77(其他entry),0,4乱序插入，含负值/零/间隙和倒退时间戳；完整目标packet在两个schema臂精确相等，输出sequence严格[-5,0,4,19,100]，其他entry事件不混入。DB逻辑/物理数据均未变。
- stale entry及真实document snapshot仍完整hydrate；随后改TASK文档，history仍返回审计原packet。这符合history现有审计语义，不能擅自把它变成check()的有效性门禁。
- 双臂真实a→b/c图、b先superseded成b2；lineage插入前拒绝与c的stale事件写后注入错误均完整回滚；正常修正后a/a2/b/b2/c状态、superseded保护和有序created/corrected/stale事件符合预期。独立代码实际确认注入命中c，没有沿用旧轮无active后代的错误oracle。
- 七类错误/水合边界对比：unknown ID、坏scope JSON、坏document snapshot JSON、目标event UTF-8损坏、其他entry event UTF-8损坏、缺events表、unknown ID同时缺events表。两臂完整错误类型/文本或稳定packet一致，unknown先于events错误，完整_get未被跳过。

所有独立语义组通过，semantics.json/log保留实际观察；不是仅凭producer pass字段或输出hash接受。诊断并未修改生产DDL，因此最终init-generated索引属性、旧库/CLI副作用、同名对象、非空文档升级与最终回归仍属于下一阶段必需门禁。

## 原冻结数值门槛

| 场景 | 生产下降 | 独立下降 | 判定 |
| --- | ---: | ---: | --- |
| history_first50000 | 82.36% | 72.81% | 主场景≥30%，通过 |
| history_last50000 | 82.71% | 69.38% | 主场景≥30%，通过 |
| history_tiny16 | -8.16% | -2.28% | 各控制退化≤15%，通过 |
| history_many512 | -6.20% | -2.71% | 各控制退化≤15%，通过 |
| add50000 | -2.51% | 5.43% | 各控制退化≤15%，通过 |
| correct50000 | -3.38% | -2.91% | 各控制退化≤15%，通过 |

不平均抵消控制退化，不删outlier，不改双主30%/逐控制15%阈值。宿主状态下绝对时间/增益幅度不同（例如tiny基线生产约0.276ms，独立约0.654ms）；这些差异和raw IQR保留在data-verification.json。门槛通过不是统计显著性或所有机器的速度保证。小库/长历史/写入控制没有统一加速，负值如实报告。

50000事件索引文件增加720896B；tiny增加4096B，many512增加12288B，均与实际page_count差额×4096吻合。50000场景生产单独DDL中位约7.58–8.61ms，独立约7.80–8.61ms；tiny约0.183/0.190ms，many约0.245/0.265ms。初次CLI和显式构造器升级包含这些额外成本，必须在生产阶段另测，不用已安装后的history收益抵扣未知首次请求时间。

## 六项标准和接受范围

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| implementation | pass within diagnostic scope | 实际同一源码、完整history/API路径、单一临时index差异、EQP/xinfo及hydration/error核验。 |
| reference_boundary | pass within scope | 独立乱序/负sequence/倒退clock事件oracle、七种异常、真实public graph失效/history/rollback观察。 |
| data_integrity | pass within scope | 全输入独立再生成、两次504样本pair/order/clock/状态hash、源码/脚本/plan绑定及保留原raw。 |
| numerical_sanity | pass | 正有限ns/API、独立中位比值/全门槛重算、DDL/file/page增长一致。 |
| measurement_validity | pass within scope | 全public API、fresh副本、对称温缓存预检、独立DDL、随机warmup/全部pair，父串行CPU计时。 |
| reproducibility | pass within scope | 冻结完整21对独立复现所有门槛通过，另做真实顺序/错误/回滚语义边界。 |

最终人工接受仅支持固定基线、一个临时events(entry_id)索引、六组合成本地温缓存完整审计/API诊断。后续只有实际生产schema与诊断等价且API路径不变，才可考虑复用本轮已安装索引后的API数据；真实CLI/init控制、最终源码/文档及完整回归另经独立验收。父MEM-STORAGE-01继续开放。无模型KV、QA、token、TTFT、RSS/GPU、生产吞吐或内部runtimeconsumer收益主张；hash是内容绑定，不是managed身份凭据。
