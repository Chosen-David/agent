# MEM-CHECK-SCHEMA-06

Task-ID: MEM-CHECK-SCHEMA-06
Date: 2026-10-16

## Plan

版本v1：仅优化Chosen-David/agent的记忆有效性入口，基线
06ed701b30fc6f83c554f1f240b1f05122d387e3。用户明确纠正项目范围后，
TwoLevel未发布工作已暂停，不属于本次交付。父任务MEM-STORAGE-01保持打开。

真实路径为MemoryLedger.check及handoff_basis的记忆门禁。只在内置公开check
拥有的普通SQLite事务内，复用document_dependencies表是否存在的查询结果；
不复用记忆对象、不跳过祖先/状态/文档校验、不合并handoff多次检查。
_get及直接_check仍不缓存。自定义实例/类入口、连接或factory保留原路径。
先查既有结果与知识；旧check03/04只复用契约，不复用通过标签或性能数据。

冻结协议：21对随机AB/BA，seed61016，各臂warmup3，每样本5次完整check。
512层有文档表和旧库无表两个主场景中位wall均需下降至少10%；单条、64父节点
及128请求根控制分别不得退化超过15%。完整输出、错误及DB字节不变。
主AI独占实现与任务；独立方案与结果审阅者只写各自证据。手动宿主执行，
不宣称受管ReviewSession、DAG服务或tmux监督器已经启动。

原最多两版/30分钟本地CPU上限：v1实例覆盖缺口、v2可变sqlite3.Row判定缺口
均拒绝并保留。版本化repair-plan-v3明确承认原候选数已用尽，只允许一次同目标
正确性修复，仍在原30分钟内，不修改输入/阈值/计时，禁止第四版。
新阻断或任一性能门槛不通过则停止本批，不发布；不是受管预算重置。

## Progress

- 原始协议、候选负结果、实际测量和独立审查统一归档在
  [报告](../../results/memory-schema-20261016/report.md)。v3源码6daa9f90…，
  主测两长链下降15.01%/12.16%，独立复测13.94%/11.22%；单条主测退化8.16%
  仍在原15%控制门槛内，不主张小库加速。
- 独立329差分、原Row反例、实际文档校验/修正/失败重查及52项针对性测试通过。
  全库1214项运行/8跳过，-O memory32项、Reader3项通过；独立六项手动验收
  usable-with-scope，只限合成温缓存SQLite完整check，不代表受管运行时认证。
- v3验证在原30分钟内完成；没有第四版。发布前重新fetch，保存实际远端SHA及
  字节核对检查点；父项真实模型KV、QA与完整请求时间保持未完成。


### 2026-10-23：跨环境测试预期核对

SYSTEM-99续接，基线bb3d5e8188fd2b21f3f34aa5f996c3b86b676e9f。原验收限3.12.14/SQLite3.53.1，不改历史结论。新增3.9.25/SQLite3.50.4运行时，原custom Row回调内DROP TABLE测试报锁；公开check与直接未缓存_check均同MemoryError/cause OperationalError，3.12环境则均成功。不能仅凭两组环境差异归因为Python版本，也不能把原路径的锁错误当缓存回归。

独立计划复核批准只改测试：无DDL自定义Row明确检查水合顺序leaf/a/parent/b和4次schema查询；DDL用相同数据库字节分别执行公开/直接路径，比较完整返回或精确异常type/args及cause，并要求回调触达a一次。没有skip、吞异常或修改生产代码；同连接非Row DDL原回归保留。隔离内存变异将固定Row判定退回动态sqlite3.Row，新测试1!=4稳定失败，保留原故障区分力。原失败日志与私有row-factory-{plan,review,mutation,py39,py312}-2257记录继续保留；较广回归及最终复核下列补记。

- 正确fixture入口（PYTHONPATH=tests，全部test_memory_*.py点号模块加tests.test_project_memory/tests.test_handoff_basis）下，真实3.12/3.9各139项通过（11.366/11.079s）。独立两环境schema各10项普通/-O通过，dynamic Row变异各失败1!=4；额外非锁OperationalError变异明确失败，未把任意共同错误算通过。独审accept/usable-with-scope，最终test SHA256为9a3b2f64…，生产project_memory.py b26ec40a…不变。此为测试可移植性纠正，不是生产锁表修复、性能收益或全库3.9兼容承诺。普通发布/远端回读另核。
