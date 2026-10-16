# MEM-REVERSE-INDEX-PROBE-07 独立诊断计划审查

结论：**REVISE：方向可接受，计时前补齐可复现的调用与核对协议。** 这里要求补充诊断计划，不要求另换候选或调整门槛。只允许在临时fixture上诊断；通过诊断不等于允许生产schema迁移或发布。这是手动独立计划审查，不是受管ReviewSession、结果验收、预算扩展或发布授权。

## 阅读与范围

实际阅读本次plan.json、prior-search.json、AGENTS.md、当前project_memory.py相关schema/_get/_descendants/_insert/_revise/impact/add/history，以及当前TASK中的MEM-STORAGE-01与既有优化状态；沿用本上下文已读的决策和项目文档治理。当前HEAD为a73bf13424bdd789284eeac6d5664bea5d104574，与计划基线一致。当前实现SHA256为6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580；被审查原plan.json SHA256为ba5c7e4e03fe6d60502188fb5441ec33e9ce7ab09a33feae75f71670ad6a0ad8。

只写本指定私有审查文件；没有修改源码、fixture、计划或指南，没有执行测试、EXPLAIN、建索引或计时。范围仅Chosen-David/agent，TwoLevel不在本次任务内。

## 判断依据

当前dependencies主键为(child,parent)，_descendants的起点与递归连接均按parent找child。候选(parent,child)覆盖索引针对实际反向查询，假设具有明确入口；但不能仅因缺少永久索引便声称每层全表扫描。计划要求先检查真实EXPLAIN QUERY PLAN和automatic_index设置是正确的。应保存原始计划文本、SQLite/Python版本、pragma及两臂index_list/index_info，而不是只记录“使用索引”。这属于诊断证据，尚无本轮实测结论。

impact会先_get原节点，再对排好序的全部后代逐个_get；correct还要插入新版本、更新旧状态、逐个加载后代并写入失效事件，且整个事务提交后返回。因此完整公共API计时能检验索引对真实入口的净收益，避免仅用递归SQL微基准夸大收益。add控制也能暴露额外索引维护成本。当前计划保留全部装配、校验、事务及返回，没有改变记忆有效性规则。

## 计时前必须明确的项目

1. **冻结完整API调用及预期结果规模。** 原fixtures只有op，impact/correct未写目标ID；correct的新ID/content/source/reason/deps与add的完整参数/evidence也未固定。根节点和叶节点会产生完全不同的后代数，不能由计时runner临时选择。补充exact_calls：例如稀疏链选择n00000时应有15个后代，wide选择根时应有512个后代；明确tiny目标和add是否verified、所需deps与新ID，且在计时外先检查所有fixture的节点/边/状态/内容和预期规模。两臂必须执行同一调用。

2. **固定DDL与API两类计量边界。** 候选临时副本执行唯一CREATE INDEX，基线保持原schema；DDL不进入API计时，但另报完整索引创建成本，至少覆盖执行和提交，明确连接/关闭是否计入。推荐把候选建索引的完整连接→DDL→commit→close单独计时，并在API开始前关闭DDL连接。文件增长在相同关闭/检查点状态下比较；记录journal_mode/page_size/page_count及相关侧文件状态，不能把尚在journal/WAL中的大小当最终空间成本。不要为了让候选表现更好而只对某臂执行VACUUM、ANALYZE或额外热身。

3. **时间戳按新行身份归一化。** 只允许忽略本次API实际新建entry和event的created_at，在规范化的完整返回及完整逻辑DB快照里一致应用；保留原值和被排除的(table,key,field)清单。既有行created_at必须逐字段完全不变。events.sequence、entry_id/action/reason/source/related_id不能忽略，事件顺序和数量必须一致。新时间戳须匹配当前SQLite默认YYYY-MM-DDTHH:MM:SS.sssZ格式并可解析，不能只检查非空字符串。可记录调用前后UTC用于合理性核查；不要求成对API调用生成相同墙钟值。

上述三项是补齐协议，不是变更唯一索引候选、fixture规模或已定性能门槛。补充后固定新计划版本/哈希，交结果核验者；未补齐前不开始正式计时。

## 其余执行与验收约束

- 21对seed71406随机AB/BA、每臂3次独立新副本热身、一份全新DB只执行一次被测写API，是公平基础。每个pair在复制前来自同一冻结原始fixture，两臂逻辑输入哈希相同；复制/检查/GC均在计时外。明确定义收益=1−median(candidate)/median(baseline)，保留所有原始样本和顺序，不改用最佳值或事后删异常值。
- DDL和复制会影响热缓存，因此只主张此协议下本地合成温缓存结果。配对两臂使用同样复制/关闭过程；EXPLAIN和额外预检在独立副本进行，避免只给一臂额外读预热。不要把该API稳态收益说成首次迁移即有净收益；若讨论摊销，只能依据单列DDL成本和对应API节省推导，并标明假设。
- impact应比较完整返回，且各臂API前后自身DB字节不变；两臂之间物理字节不同是索引的预期结果，不能跨臂强求字节相等。correct/add比较归一化完整返回及所有业务表逻辑快照，并核查sqlite_sequence与事件顺序；schema差异仅允许所声明的候选索引。
- correct核验旧根superseded、准确后代stale、其余disjoint链未变、新版本和关联事件正确；已有superseded后代不得被复活。失败回滚至少包含在插入前失败与实际写入后失败的覆盖，按既有独立验证规范检查，而非只看成功退出或JSON pass。原始失败与不一致均保留。
- 两个sparse5000主场景必须各自达到中位耗时下降>=20%，其他每个控制退化<=15%，不能平均抵消。任何正确性不一致阻断性能结论；任一性能门槛失败保留负结果，不调阈值、不换规模、不加第二索引。20分钟/单本地CPU/一个固定schema候选的边界保持不变。
- prior-search确实为scanned200、partial=true且有59条读取错误；命中主要是无关corpus/comm记录，不能解释成完整历史无结果。历史记忆合同可复用方法和语义，不能复用其性能数据当本轮证据；知识卡相关性不证明适用性。

## 七项计划结论

| 项目 | 结论 |
| --- | --- |
| intent | pass：Agent现有反向依赖查询的局部诊断，未偏离项目。 |
| guide | pass：无人类指南写入或冲突。 |
| assumptions | conditional：需保存真实查询计划；不预设自动索引不存在。 |
| prior_results | pass within scope：检索不完整被如实保留，只复用方法。 |
| acceptance | revise：补齐exact_calls、DDL边界及新行时间戳归一化后才冻结计时。 |
| risk | pass within diagnostic scope：只改临时副本索引，生产代码/schema无授权扩张。 |
| resources | pass as prospective bound：单CPU、20分钟、一个候选；实际预算由主控核验。 |

正式数据须经另一次实际源码/runner/输入/原始数据/数值/测量/复现独立审查，验收只可为具体协议下usable-with-scope。诊断通过后仍需单独版本化实现/迁移方案，覆盖既有库升级入口、幂等/失败恢复、写入和空间代价及最终回归；本审查不授权该阶段，更不授权推送索引迁移。无模型KV、QA、token、TTFT或GPU收益主张。
