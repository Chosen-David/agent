# MEM-REVERSE-INDEX-PROBE-07 独立结果核验

**结论：usable-with-scope，仅限冻结临时schema诊断。** 本审查由另行派发的 agent_schema_result_verify 实际执行，是人工独立代码/数据核验，无managed receipt、受管ReviewSession或自动信任认证。不批准生产迁移、源码实施或发布；后续须另有方案、实际schema/CLI验证及独立验收。仅Agent，TwoLevel暂停。

## 绑定、实际代码与协议

读取原plan/两版计划反馈、plan-v2、完整probe.py/validate.py、原失败日志、raw.json、validation-v2、环境/生产者hash，以及实际MemoryLedger建库、_descendants、impact、_revise、_insert、correct/add/history路径。基线a73bf13424bdd789284eeac6d5664bea5d104574；诊断源码SHA256为`6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580`。原始及独立raw均绑定此源码。diagnostic-source.py从固定Git对象提取，保留可复核快照；本轮无生产源码修改。未来实施改动不自动继承诊断验收。

固定索引只有`CREATE INDEX memory_dependencies_parent ON dependencies(parent,child)`。每对使用相同seed库的两个新副本，候选DDL单独connect/create/commit/close，API开始前连接关闭；copy/DDL/逻辑快照/相等检查在计时外。21对seed71406随机AB/BA，每臂3次新副本warmup，每样本1次完整公共API。计时包含API内部路径校验、连接/事务、所有读取/更新/事件/commit/返回；MemoryLedger实例构造在计时外，符合已有ledger上调用API的范围。不是CLI或首次建库计时。

独立测量命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-index-probe-20261016-1406/reviewer/probe-independent.py`。其计时部分与冻结harness相同，仅改私有输出/plan位置与临时目录，去掉已知错误的后置oracle段；正确性另由verify.py独立验证。原harness/失败日志/原raw未覆盖。独立重跑约29.06s、一个本地CPU测量进程；父明确暂停并于timing-done后恢复测试。未绑核，其他宿主干扰不能完全排除。原raw因后置失败没有elapsed/gates字段，不能把它描述为完整脚本成功退出；本审查从全部样本重算门槛。资源实际起止仍须结合父执行记录，不用文件mtime自证可信预算。

## 原失败与时序

原probe在五组各42个计时样本、完整输入/输出/状态相等断言及raw写出后，进入全新临时验证fixture才失败。它先把b修订成b2，b保留superseded、b2不继承a依赖；a已无active后代。随后只在action=='stale'注入异常，因此不会触发，期待“write rollback should fail”的oracle错误。独立重建该原fixture确认没有stale事件、b仍superseded且b2 active，不能据此认定生产回滚缺陷。

补充fixture新增active后代c，未改计时图、源码或索引候选。verify.py独立验证双臂：依赖失效lineage在插入前拒绝且完整逻辑状态不变；写入后到c的stale事件注入sqlite异常确实触发，entries/dependencies/document bindings/events/sqlite_sequence完整回滚；正常修正affected=['b','c']，b保持superseded、b2 active、c stale，a/a2状态与history事件顺序正确。返回新revision时钟与DB值相等。原错误验证临时库与所有计时副本分离，失败不会反向污染已保存计时数据。原失败与补充验证必须一起保留。

## 输入、schema、时间戳与参考语义

verify.py独立用Python字典生成完整预期逻辑输入（非只检查节点数）：固定entries、每条created事件及其sequence、dependencies、空document_dependencies、sqlite_sequence；与生产/复现全部fixture input_hash一致。5000节点图由互不相连的至多16节点链构成，目标n00000后代15；wide为512后代，符合冻结exact_calls。实际add/correct使用计划的ID/content/source/reason/deps/evidence；不是省略验证的SQL微基准。

独立重算原始/复现各fixture的21对唯一pair/arm、全部顺序（包括warmup消耗的RNG）、正有限wall_ns、中位数、比值、所有输出/状态hash及42条样本数量。每对两臂稳定完整逻辑状态/输出hash相等；没有丢弃失败样本或选最小值。impact各臂自身DB字节不变是harness断言，复现也实际通过；原raw未保存每样本前后物理hash，这是审计细节限制，不能声称原raw含有它们。

仅新entry revision/new-entry及seeded最大sequence后新事件的created_at被归一化；所有旧行时间戳仍严格等于固定输入值。独立检查每条原始新时钟非空、严格SQLite UTC格式、可解析日期、允许身份、事件sequence唯一且连续、数量符合API事件行为。correct事件包括created、corrected、revision_of和每个stale事件，未忽略其他字段。原快照按完整JSON排序而非事件sequence排序，sequence身份仍保留、history API另按sequence核验。独立负向探针确认旧时钟变化和非法新时钟不会被normalizer掩盖。

实际EQP明确显示baseline anchor `SCAN dependencies`，recursive step使用`AUTOMATIC COVERING INDEX (parent=?)`，automatic_index=1；不能说每一步均为全表扫描。候选anchor和recursive step均使用持久`COVERING INDEX memory_dependencies_parent`。双方完整sqlite_master逻辑schema差异只有该索引，index_info顺序parent,child；page_size4096、journal delete。独立复现保存同样EQP/schema/pragma并验证差异。收益支持避免临时automatic index构建等开销的解释；未拆分各因素独立成本。

另外60组独立随机循环/共享有向图，用纯Python遍历求可达集合并核对两个schema臂的完整impact返回与排序，全部一致；循环可达目标本身时按现有SQL语义纳入，未额外修改算法。这是独立参考边界，非复制递归SQL自身作oracle。

## 门槛与成本

| 场景 | 生产下降 | 独立下降 | 判定 |
| --- | ---: | ---: | --- |
| impact_sparse5000 | 59.72% | 47.95% | 双主之一≥20%，通过 |
| correct_sparse5000 | 47.03% | 36.25% | 双主之一≥20%，通过 |
| impact_tiny16 | -0.24% | -0.71% | 退化≤15%，通过 |
| correct_wide512 | 0.79% | -0.12% | 退化≤15%，通过 |
| add_existing5000 | -5.04% | -9.23% | 退化≤15%，通过 |

未降低20%双主或15%逐控制阈值；控制退化如实保留。绝对时间与增益幅度不同，说明宿主状态/短操作噪声；只支持这些同机配对测量的诊断结论，不是统计显著性或通用加速保证。IQR/中位数在verification.json保留。

5000节点候选索引文件增加106496B，tiny增加4096B，wide增加16384B，均与page_count增长一致。生产DDL中位约1.04–1.23ms（5000节点），独立约1.18–1.24ms；wide约0.34/0.37ms、tiny约0.18/0.20ms。DDL成本被单列，不能把排除DDL后的API收益直接当首次迁移的净收益。新增/重复CLI构造、真实迁移、已有同名索引冲突、锁竞争、磁盘冷启动、长期写放大与跨硬件工作负载未在此诊断被认证。

## 六项标准

| 标准 | 结论 | 实际依据 |
| --- | --- | --- |
| implementation | pass within scope | 实际同一源码、完整API/事务路径，索引为唯一临时schema差异；原oracle问题已定位隔离。 |
| reference_boundary | pass within scope | 60独立Python可达图；完整history/状态/失效传播和前后写回滚验证。 |
| data_integrity | pass within scope | 输入独立再生成、源/协议/hash、全部pair/order/样本/状态hash/时钟身份检查，失败保留。 |
| numerical_sanity | pass | 正有限ns/API、独立中位比值/门槛重算、DDL字节/page_count一致。 |
| measurement_validity | pass within scope | 新副本、对称API范围、单独DDL、warmup/随机顺序、独占任务计时，全部样本保留。 |
| reproducibility | pass within scope | 同冻结21对复测双主及全部控制通过；EQP/语义/回滚和原oracle解释独立复现。 |

证据：原probe.py/probe.log/raw.json/validate.py/validation-v2.json保留；reviewer下probe-independent.py/raw.json/replication.log/verify.py/verification.json及hash清单。审查脚本最初两次断言错误分别漏计correct新entry的created事件、误把按JSON排序的原始事件时钟列表当成sequence排序；已修正审查预期，失败日志verification-attempt1/2.log保留，无计时重跑/数据修改/阈值放宽。

最终人工接受范围：固定源码、五个合成温缓存fixture、一个索引候选、完整公共API诊断。无模型KV、QA、token、TTFT、RSS/GPU或生产收益主张；不能将diagnostic pass作为schema迁移/发布批准。evidence-hashes.json绑定实际代码、输入生成器、配置、原始数据、独立复现与环境；它是内容绑定，不是身份认证。后续源阶段必须绑定新实现并完成自己的schema/CLI/回归及结果验收。
