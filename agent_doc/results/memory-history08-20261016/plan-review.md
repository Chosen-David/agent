# MEM-HISTORY-INDEX-08 独立计划审查

**准入结论：ACCEPT，无计时前必需修订。** 只准入计划所定临时schema诊断；条件式生产DDL阶段仍须本轮诊断独立usable-with-scope，两个主场景各达30%改善、每个控制退化不超过15%，且实际代码/数据/语义无阻塞。此为手动独立计划审查，不是managed ReviewSession回执、结果验收或发布批准；任何旧轮数值均不可复用成本轮证据。

## 审查对象与实际工作

读取plan.json全文、AGENTS.md、当前project_memory.py初始化/_connect/history/CLI派发及相关测试入口，并检查本轮prior-search和knowledge-search。沿用本上下文已读的决策、项目文档和独立结果治理。当前HEAD为c854e274fea7e72a574bf1377d7f38679832812d，git status --short为空。plan.json SHA256为d8cea0f4599589084613dc6316c0085af39914dc6b38a282c8a6b426a4f4c23e；源码SHA256为7df8e23ecee946e996b828fb702258e03dabe2306b42c63a3daadf15008d950e。

没有修改生产源码、计划、指南或harness；没有运行测试、EXPLAIN、建索引或计时。只写本指定审查文件。未独立探测主控锁的实际状态，不把主控提供的owned-lock说明改述为本审核已验证。范围仅Chosen-David/agent，TwoLevel不在范围。

## 目标与实现合理性

当前history先完整_get目标entry，再执行`SELECT * FROM events WHERE entry_id=? ORDER BY sequence`，完整装配events并在事务结束后返回。计划使用真实public history完整路径，而不是只测SQL片段，保留路径/连接/事务、entry hydration、JSON和完整历史装配成本，适合回答现有audit接口的实际延迟问题。当前源码搜索只见本接口和CLI history派发；本轮没有已证内部runtime历史消费链，结论仅可称audit历史查询改善，不能外推agent检索质量或模型KV。

单个非唯一events(entry_id)索引与实际筛选条件一致。sequence当前为INTEGER PRIMARY KEY AUTOINCREMENT，计划将其rowid语义作为待核实机制，通过真实index_xinfo/EQP和结果顺序验证；索引只含entry_id时并不覆盖SELECT *，计划明确避免covering或“消除基线排序”的未经验证说法。查询仍显式ORDER BY sequence，生产阶段不改查询或缓存历史。真正收益、额外写入/空间成本和优化器选择只能由本轮数据确认。

## 诊断公平性与门槛

两主场景分别固定50000事件账本的n00000/n49999完整history，其他控制涵盖小账本、单条目长历史和add/correct的额外索引维护。first/last主场景不是两个独立用户群或独立科学证据，应按固定fixture分别报数；仍必须两者各自通过30%，不能平均或只选更好者。history_many512明确为schema-valid重复事件压力fixture，不冒充真实public生成历史，这个边界合理。

相同冻结源码/逻辑fixture的成对临时副本，唯一新增schema为memory_events_entry；21对seed81601随机AB/BA、3对新副本热身、写API每样本新库，排除复制/DDL/预检/快照比较，收益按1−median(candidate)/median(baseline)，保留全部样本和顺序。每个控制单独<=15%退化，任何正确性失败阻断收益结论。一个固定候选、一次诊断和一次独立复现，不调fixture/阈值/索引碰结果。

应按计划保存环境、pragma、索引schema/xinfo、实际EQP、原始样本/随机顺序/逻辑输入哈希/文件状态，DDL完整connect→execute→commit→close单列，物理大小在可比关闭/检查点状态计算，相关side files同样记录。预检两臂都读取数据意味着仅有本地合成温缓存主张；不声称冷盘、跨进程启动、生产负载或一般吞吐。额外EXPLAIN在独立预检副本执行，避免只给一个计时臂预热。

## 正确性与legacy边界

history完整packet和顺序精确相等，各臂自身API前后DB字节不变；跨臂物理字节因索引不同不能相等。add/correct仅按新entry ID和seeded max之后新event身份规范化created_at，保存原值并验证SQLite UTC格式；旧时间戳、sequence、相关ID、source/action/reason和全部逻辑行精确保持。correct预期n00001..n00015失效、根superseded、新版本active、其他孤立节点不变，独立验证还要检查public生成图上的superseded保护、前置失败和实际写后回滚。

计划包含乱序插入sequence、负值、间隙和倒退时间戳的回归，能区分真正sequence顺序与偶然插入/时间顺序。实际核验应确认完整entry hydration的未知ID、异常及document绑定等既有语义仍在；DDL-only不意味着可以跳过最终相关回归。

条件式实现仅在events建表后加两行IF NOT EXISTS索引DDL。普通Python构造/读/history不安装索引；Python create=True显式升级，现有CLI add先create=True，即使随后add失败也可能已安装索引。没有不存在的CLI init承诺，未改变旧CLI接口。同名错误索引留存且不保证性能，同名table冲突按真实错误语义核验，不擅自drop/rebuild。现有executescript部分schema/失败边界保留，不宣称全升级原子。含非空document bindings/events/sqlite_sequence的真实旧库升级和重复初始化必须保持全部业务数据，升级自身不应归一化任何时间戳。

## 生产阶段证据与资源

生产源码修改在诊断独立接受前仍阻断。接受后仅按已定DDL实施，并由独立结果核验者验证真实create=True生成schema与诊断候选等价、API源码路径未变，才允许复用本轮诊断稳态API测量。最终源码单独冻结；旧reverse-index轮的测量一律不作证据。

seed81602的21对完整main(add)控制包括parser/init/commit/JSON及对称StringIO，候选预装索引而基线未装新索引，重复初始化控制仍须<=15%退化；首次CLI升级和构造器upgrade/repeat成本单列，不把已装索引查询收益当首次升级净收益。baseline必须独立module globals，防止基线执行候选MemoryLedger。没有process-start收益主张。

25分钟诊断+独立验证预算从本准入后计，只有诊断接受后才启用额外15分钟实施/全检查预算；主控记录实际起止和剩余，超限保留pending/失败而非加轮。只运行一个CPU测量进程，生产者/核验者时段串行，不终止未知作业。最终全库/Reader/-O记忆检查必须实际完成，预算不允许时如实阻断，不以计划勾选代替结果。文档或生成插件副本仅在真实关联内容需要同步时更改，不扩散无关workflow变更。

## 七项审查与最终限制

| 项目 | 结论 |
| --- | --- |
| intent | pass：现有audit history接口的有界索引优化。 |
| guide | pass：无人类guide改动或目标冲突；父任务保持开放。 |
| assumptions | pass as testable hypothesis：实际EQP/xinfo/packet验证，不冒称covering或基线排序。 |
| prior_results | pass within scope：实际搜索scanned200/partialtrue/errors59，命中仍unchecked；不当全库无结果或新收益。 |
| acceptance | pass as prospective protocol：双主30%、每控制15%、精确语义及独立门槛固定。 |
| risk | pass within stated boundaries：临时诊断后条件式DDL，legacy/CLI/同名/顺序边界明确。 |
| resources | pass as bounded plan：25分钟诊断+验证，接受后15分钟实施检查，无模型/付费/GPU；实际消耗待核验。 |

knowledge实际命中Freedman/FAISS/HNSW均为前提不匹配，拒绝迁移正确；论文阅读记录只作路线/历史动机，本审查未独立核验论文原文，不据此认证新论文阅读量或科学机制。无模型KV、QA、token、TTFT、RSS、GPU或内部runtimeconsumer收益结论。

本计划准入不替代后续独立源码/harness/输入/数据/数值/测量/复现审查，不构成发布允许。独立结果接受、最终回归、fresh fetch/reconcile、限定owned文件、正常main提交和SHA/tree/字节/manifest读回仍须按既有授权与治理逐项完成；manual证据不得标成受管可信回执。任一门槛失败保留负结果并停止依赖生产/发布分支。
