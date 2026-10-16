# 反向索引实施计划独立审查

**结论：REVISE。** 初始化脚本增加一个非唯一覆盖索引是与诊断同目标的有界实现，但计划对现有CLI入口和旧库升级时机的描述不符合当前源码，必须先纠正。只审计划，不修改源码、不执行测试/计时；诊断reviewer独占计时不受本审查干扰。此为手动审查，不是受管ReviewSession或发布批准。

审查对象implementation-plan.json SHA256为3bc9acac4d40834e2f8250aa19790789306bd1bb58b280ec20189079ace20c8b；当前基线a73bf13424bdd789284eeac6d5664bea5d104574，project_memory.py SHA256为6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580。实际读取初始化、_connect和完整main CLI派发，以及有关记忆测试入口。沿用本次已读取的AGENTS和项目治理约束。唯一写入为本指定审查文件。

## 阻塞项：真实初始化入口

当前main()只注册add/correct/accept/list/check/history/impact，没有init子命令；计划称“CLI init”已存在及拟写其现有指导，是事实错误。main()还固定调用`MemoryLedger(args.root, create=args.command == 'add')`。因此仅在create=True脚本加DDL，就会让旧库在CLI add时建索引；这不是“旧库仍可无索引写，只有显式reinit升级”的完整行为。

建议保持最小单行实现并修订计划：明确Python普通构造、读/check/impact以及已有对象add/correct不建索引；Python create=True重初始化和现有CLI add初始化路径都会幂等尝试安装索引。文档提供实际存在的Python重初始化方式，并说明CLI add的升级副作用，不发明CLI init。如果希望新增CLI init或改变add派发，需另版明确接口、兼容和测试范围，本审查不把这些扩展当已批准实现。

修订版应冻结CLI add实际升级回归：从无索引旧库执行CLI add后，索引正确，原有行/事件不变，仅预期新记忆及事件增加；普通CLI list/check/impact不得更改schema。此差异直接来自实际调用链，不能只靠Python API测试覆盖。

## 双门槛与证据复用

诊断尚未独立验收，现阶段不得开始生产源码修改。实施阶段同时依赖：诊断plan-v2及真实runner/raw/validation取得独立usable-with-scope且两主场景各>=20%、每控制退化<=15%；修订实施计划获得独立准入。两者缺一不派发，数值通过不能覆盖正确性失败，计划准入也不能替代数据验收。

诊断数据仅可复用于同一索引定义、同一API/图输入/参数/计时协议及适用环境；用真实create=True生成的索引对照诊断候选的唯一性、表、列顺序、排序/partial/expression属性和schema差异。SQL文本可单列记录，不能仅凭索引同名判定等价。冻结最终源码差异仅为初始化DDL后，由独立核验者决定是否可复用既有稳态API数据，无须为已有同条件结论盲目重跑，但必须验证生产路径真实生成等价schema。

诊断API计时排除了初始化DDL，不能证明create=True升级、重复init或CLI add完整入口的延迟。计划单列真实构造器首次升级与重复初始化的完整连接/DDL/提交/关闭耗时及空间代价是必要补充；新旧两臂均用同一既有库输入。报告只能把诊断称为已装索引后的本地合成温缓存完整API收益，并明确单列一次性/重复初始化成本；不能扩写成CLI端到端收益或首次迁移净收益。

## legacy与迁移核验

- 新库验证索引确实非唯一，列顺序为parent,child，旧(child,parent)主键和全部表schema保持原义。
- 无索引旧库普通构造及读操作保持schema/业务数据不变；create=True重初始化只新增指定索引，不改entry/dependency/document/event/sqlite_sequence，重复执行幂等。按修订后的真实CLI路径增加集成核验。
- 测试用真实public add/correct产生绑定数据/事件，再做升级，避免只有空表bulk fixture。比较精确逻辑快照与旧时间戳；升级没有新业务行，故这里不应忽略任何created_at。
- `IF NOT EXISTS`不验证同名旧对象的结构。至少补充同名错误索引的边界测试/文档：不得因此宣称安装成功或永久覆盖索引已启用；不在本轮悄悄drop/rebuild未知索引。若需要强校验/修复，应版本化扩展方案。
- 保留现有executescript/_connect错误与事务行为，不借单行DDL宣称升级全程原子。锁争用、只读/磁盘错误或不完整旧schema可能导致初始化失败，不能自动删库/重建。核查失败不修改业务行，并诚实限定schema部分成功的已有边界。
- 永久索引的EXPLAIN检查绑定实际执行的递归SQL及SQLite版本；不对所有SQLite版本硬编码相同完整计划文本。索引应不改变后代排序、失效范围、superseded保护、历史事件或前置/写入后错误的回滚行为。

## 其余审查项

目标、指南、历史复用方向和风险范围可接受；单独生产实施方案较诊断范围明确，不把诊断当迁移授权。测试范围总体合理，需补齐上述真实CLI/同名对象边界。资源只允许串行本地核验，不抢占诊断计时，不增加模型/付费/GPU工作；实施与独立核验的实际剩余时间由主控绑定，不能默认沿用已耗尽预算。单一TASK作者和人类guide只读边界不变。MEM-STORAGE-01保持未完成，其他仓库不在范围。

在入口事实修订并经审核前，本实施计划未准入；在诊断独立usable-with-scope前，即使完成该修订也只能推进独立只读准备。最终完整回归、独立实际代码/数据核验、fresh fetch/reconcile和正常main发布/远端读回是后续门槛，本文件不授予推送权限，也不声称模型KV/QA/TTFT收益。
