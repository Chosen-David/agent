# 反向索引实施计划v2独立审查

**结论：ACCEPT，条件式实施计划准入。** 原implementation-plan-review.md的入口事实阻塞项已修正；不新增必需算法或源码扩展。诊断仍未完成独立语义验收，因此当前仍不得编辑生产源码。必须同时具备诊断独立usable-with-scope和本实施计划准入，才进入源码阶段。数值门槛通过不等于诊断已验收。

实际读取implementation-plan-v2.json全文，SHA256为5581cf8a5a576821353258906ad5282bad8564c10475b86cfaab3788297f1961。沿用同轮已读AGENTS、初始化/CLI/修正/插入实现及原审查约束。只写本指定审查输出，没有修改源码、计划或指南，没有运行测试/计时；诊断reviewer的独占测量不受干扰。这是手动计划审查，不是受管ReviewSession、预算扩展、结果验收或发布批准。

## v2修订为何足够

v2撤回不存在的CLI init，保持唯一索引DDL的最小实现。Python显式create=True重初始化是升级路径；现有CLI add本来就先create=True，因而会尝试安装索引，且即使后续记忆插入校验失败，初始化副作用仍可能保留。计划已明确该边界和一次性建索引/锁/空间/失败成本，不把初始化与后续entry事务混为一谈。普通读取不自动升级，也不引入新CLI接口。

新验证范围包含真实CLI add在旧库安装索引且保留旧行/事件、重复add初始化，以及Python新库/旧库/reinit幂等和完整逻辑数据保持，覆盖了此前漏掉的真实生产入口。

性能证据分层合理：已装索引后的公共API诊断仅在输入、schema、最终源码差异和协议一致且独立审查允许时复用；真实构造器升级/重复初始化完整成本单列。新增21对seed71407随机AB/BA的完整CLI main(add)控制包含parse/init/create/entry commit/json格式化，stdout对称重定向，预装索引的重复初始化控制中位退化不得超过15%；旧库首次升级单列成本、不伪造速度门槛。该控制不会更改原诊断两主场景各>=20%和各控制<=15%的门槛，任一依赖门槛失败即停止源码/发布分支，保留负结果。

## 执行与结果核验的必要解释

- “普通构造/read/correct/add schema-read-only”只能解释为不安装本次索引、普通read不迁移；不能说add/correct完全不写schema或业务数据。当前_insert对于document_refs仍有既有CREATE TABLE IF NOT EXISTS document_dependencies。文档和最终报告应使用“不会安装本索引”，避免扩大兼容承诺。
- CLI基线从固定git源码加载时，须与候选拥有独立module globals/MemoryLedger绑定；同属agent_runtime包以支持相对导入是可以的，不能共享会让基线调用候选类的可变全局命名空间。独立结果核验应检查实际已执行的source身份及module隔离，不能只看git字符串。
- 每个CLI样本从新的同逻辑fixture开始，固定同一完整参数/输入，记录初始化前后schema/数据/文件状态。重复初始化场景的候选预装索引，基线维持其部署schema；首次升级场景候选必须初始无该索引。不要在测量过程中重复累积新entry，或只给某臂额外预热。
- 真实init生成索引的比较须覆盖表、非唯一性、列顺序parent/child、排序/partial/expression属性；保留(child,parent)原主键。不能只看同名。针对同名错误索引至少记录/测试现有IF NOT EXISTS边界，不声称它能验证并修复任意旧schema；本轮不新增自动drop/rebuild。
- 升级没有业务行/事件产生，全部created_at与sqlite_sequence均应精确保持，不套用诊断correct/add的新时间戳忽略规则。业务写入的预期新行/事件另按既有合同核验。
- 既有executescript初始化语义保持，不承诺新增全程原子迁移；验证失败/锁/路径守卫时不丢业务行、不自动重建库。索引安装可能在后续CLI add失败前已完成，测试与报告必须与该事实一致。
- EXPLAIN绑定实际SQL和SQLite版本，检查已安装永久索引对seed/递归查询的作用，不硬编码跨版本完整文本。失效传播、superseded保护、事件顺序、前置和写后失败回滚仍须实际核验。

## 七项结论与边界

| 项目 | 结论 |
| --- | --- |
| intent | pass：同一Agent反向依赖索引实现，最小范围。 |
| guide | pass：无人类guide写入或冲突。 |
| assumptions | pass within scope：实际CLI初始化行为已纠正，未知旧schema不冒称自动修复。 |
| prior_results | conditional pass：诊断数据只有独立验收及等价性检查通过后才可复用。 |
| acceptance | pass as plan：双门槛、旧库/CLI回归与独立结果核验明确。 |
| risk | pass within scope：单索引初始化，旧读路径无自动迁移，无算法/失效语义变化。 |
| resources | conditional：串行CPU、一个修订、无新增付费/模型工作；主控须绑定本实施/核验阶段的实际剩余时间。 |

主控称诊断独立计时五组通过；本审查未读取/核验其原始数据，不据此签发结果接受。最终源码、构造器/CLI计量、所有数据与回归仍需独立实际核验，且保留诊断与实施结果边界。发布前fresh fetch/reconcile、正常main CAS和远端读回仍是单独门槛，本审查不授予发布权限。整个MEM-STORAGE-01继续开放，模型KV/QA/token/TTFT等尚未由此验证，TwoLevel不在范围。
