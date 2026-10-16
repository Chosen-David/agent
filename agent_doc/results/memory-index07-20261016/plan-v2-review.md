# MEM-REVERSE-INDEX-PROBE-07 v2 独立计划最终审查

**准入结论：ACCEPT，仅限已冻结的临时fixture诊断。无新增必改项。** 此结论是手动独立计划审查，不是受管ReviewSession、实验结果验收、生产schema迁移或发布批准。原plan.json及其REVISE反馈保留在同目录，不被本结论改写。

实际读取plan-v2.json全文；SHA256为58d9ed6af2406063fd8c8960be0739ddf378ed943e40eea99cec251f9cf430a1。基线仍为a73bf13424bdd789284eeac6d5664bea5d104574，源码仍绑定先前审查的当前project_memory.py。未修改源码、指南或harness，也未执行建索引、EXPLAIN、测试或计时。本次唯一写入为指定审查文件。

v2已解决原审查三个计时前阻塞项：

1. exact_calls固定impact/correct目标为n00000，correct的新ID/content/source/reason，以及add的新ID/kind/content/source/deps和verified证据级别。稀疏链和tiny预期15个后代，wide预期512个；这与所描述图结构及当前_descendants/公共API对应。
2. DDL明确按connect→CREATE INDEX→commit→close完整单列计时，并记录前后文件大小；API计时不包含DDL。两臂唯一schema差异为dependencies(parent,child)候选索引，源码不变。
3. timestamp_rule只规范化revision/new-entry的created_at及seeded事件最大序号之后新事件的created_at，保存原值并验证SQLite UTC格式；匹配返回的新entry使用同一规则，所有旧行时间戳逐字节不变。事件身份、sequence、顺序和其他字段不被忽略。

此前plan-review.md中的其余执行约束继续适用，主控已明确runner将保存pragma、索引metadata、完整逻辑表/schema/sqlite_sequence、raw时间戳、独立副本预检和全部21对样本。EXPLAIN及额外检查在独立副本完成，避免只对一个计时臂额外预热；DDL连接在API开始前关闭，文件大小在同等关闭/检查点状态比较。impact检查各臂自身API前后字节不变，不能要求索引不同的两臂物理字节相等。

正式测量沿用同一源码、同一冻结原始fixture的全新成对副本、21对seed71406随机AB/BA、每臂3次新副本热身、每样本一次完整公共API。copy/setup/DDL/equality/GC在API计时外，全部样本保留；收益固定为1−median(candidate)/median(baseline)。两个sparse5000主场景各自下降至少20%，每个其他控制退化最多15%，不平均抵消。任何正确性失败阻断性能结论；门槛失败保留负结果，不换fixture、阈值或第二索引候选。

资源边界按主控澄清：20分钟从本次诊断准入后的实验开始计，不追溯计入此前静态审查；一个本地CPU、一个固定索引候选，无GPU/API/模型/付费资源。主控记录实际起止、剩余预算与独占测量状态；这不构成任何受管预算/lineage重置。范围始终仅Chosen-David/agent，TwoLevel暂停。

| 检查项 | 结论 |
| --- | --- |
| intent | pass：针对Agent实际反向依赖入口诊断。 |
| guide | pass：无指南改动或冲突。 |
| assumptions | pass as hypothesis：先保存真实EXPLAIN/automatic_index，不预设全表扫描。 |
| prior_results | pass within scope：扫描不完整/读取错误与知识条目不匹配均保留，不冒用旧收益。 |
| acceptance | pass：精确调用、规范化、完整API及门槛已固定。 |
| risk | pass within diagnostic scope：只在临时副本增加索引。 |
| resources | pass as bounded plan：20分钟、一个CPU、一个候选；实际使用待核验。 |

诊断产出的数据继续为pending，必须另经实际源码/harness/输入/原始数据/数值/测量/复现的独立结果核验，且确认失效传播、事件历史和失败回滚。通过后只支持所测本地合成温缓存完整API结论；不代表生产迁移、首次建立索引后的净收益或通用吞吐改善。后续实现/迁移和发布需独立版本化方案与验收，本准入不授权。无模型KV、QA、token、TTFT、RSS或GPU收益主张。
