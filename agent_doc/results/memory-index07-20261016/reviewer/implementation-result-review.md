# MEM-REVERSE-INDEX-07 实施及集成结果独立核验

**最终实施及集成结果结论：usable-with-scope。最终回归已核对通过；发布仍须归档冻结及远端读回门禁。** 人工另行派发的独立审查，无managed receipt、受管ReviewSession或自动信任认证。仅Agent；未改生产源码、测试、文档或guide。TwoLevel暂停。实际独立测试已结束并通知父执行者，未与父最终回归/计时并发。

## 固定身份及范围

基线a73bf13424bdd789284eeac6d5664bea5d104574；原诊断源码`6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580`。最终源码SHA256为`7df8e23ecee946e996b828fb702258e03dabe2306b42c63a3daadf15008d950e`，快照implementation-source.py。实际代码/测试/工作流与生成引用、计划、baseline、集成脚本及原始数据、独立探针hash见implementation-hashes.json；诊断固定源码快照和此前独立接受仍保留。

读取implementation-plan-v2及独立计划审查、实际源/四项新测试/工作流diff、完整integration.py/json/log、原测试修前失败/修后通过、诊断独立结果和原始数据。实际源相对基线仅在create=True的既有executescript内增加两行`CREATE INDEX IF NOT EXISTS memory_dependencies_parent ON dependencies(parent, child)`。公开impact/correct/add/check及helper函数未变，未增加缓存、失效捷径或读时自动迁移。CLI main仍按add使用create=True，其他命令不变。三份generated workflow引用属于必要文档同步，不改变运行语义。

独立implementation_verify.py从固定baseline.py加载另一个agent_runtime包内模块；确认baseline/candidate MemoryLedger不同、main.__globals__各自为自身模块字典，基线main绑定基线类。原integration.py同样使用独立globals，不会因候选类名称覆盖而把基线误测成候选。baseline.py与固定Git源/此前诊断源身份相符。

## 实际独立执行

命令：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-index-probe-20261016-1406/reviewer/implementation_verify.py`，以及独立运行tests.test_memory_reverse_index四项unit。父回归停止后执行，输出implementation-verification.json/log与implementation-unit.log；四个边界组和四项unit均通过。

1. **真实非空文档绑定升级。** 用旧模块public add与真实snapshot_project_docs建立a/b/c，再document-bound correct(b→b2)，四行非空document_dependencies。候选普通构造/check/impact/history/list不装索引，DB物理字节/schema不变。显式create=True后entries/dependencies/document_dependencies/events/sqlite_sequence逐字段精确等于升级前，包括所有created_at和原序号；重复init同样精确且DB字节稳定。
2. **实际索引等价。** 初始化生成的索引非唯一、非partial、列序parent/child、升序、BINARY collation，无表达式，保留原child/parent主键；index_xinfo包含预期rowid辅助项。与旧源+诊断DDL的完整schema仅有可忽略空白/IF NOT EXISTS语法差异，索引metadata完全相同。实际生产SQL EQP在anchor和递归都使用该永久覆盖索引。旧API诊断候选schema与真正init-generated schema一致，因此其固定API计时可复用到**索引已安装后的同一API路径**，不能复用为首次init/CLI成本。
3. **业务/API及失败边界。** 普通Python add在旧库不安装本索引；真实生产索引下document-bound correct的lineage前置拒绝及c的stale事件写后异常均完整回滚，正常修订保留superseded历史和文档snapshot。CLI duplicate-ID add返回2，stdout空、stderr有immutable错误；初始化已安装索引但所有业务表保持原值。这是两个阶段的既有入口行为，不是对整个CLI操作原子性的保证。
4. **未知同名schema。** 同名错误列索引、另表上的同名索引均被IF NOT EXISTS原样保留；不能宣称此类库获得索引收益。同名table碰撞按MemoryError失败，已有业务数据及schema不变。未加入自动drop/rebuild。独立各运行一次真实baseline/candidate main(add)，稳定完整输出相等，返回新entry时钟等于实际DB行。未知损坏schema、磁盘满/权限/并发DDL/写锁及全程executescript原子迁移不在此认证范围。

## 集成原始计量与重算

实际integration.py冻结seed71407，四场景各21对/3warmup，独立新副本，无累计entry污染。候选稳态场景在API计时外真实create=True预装索引，首升级场景开始时无索引；基线均保持其原部署schema。CLI timer覆盖main中的argparse、初始化、add事务及JSON字符串格式化/print到对称StringIO，不包含Python进程启动或真实终端/磁盘stdout成本。constructor timer含完整create=True调用。copy/输入/快照/equality在计时外。

implementation-data-check.py独立重算168个raw样本：每pair恰好双臂、warmup消耗后的随机顺序、正有限ns、全部中位数和reduction、输入hash与已接受诊断一致、每对完整稳定返回/业务state_hash相等、实际物理文件大小/4KiB页倍数。constructor零新增clock，CLI只允许new-entry及event sequence5001的合法SQLite UTC时钟；事件/entry其他字段不归一化。构造器升级的全部旧值未被时间归一化忽略。原raw没有自身源码hash字段，实际integration.py/baseline.py/冻结最终source由外部artifact hash和本次代码审查绑定；不把文件名或Git字符串单独当执行证明。

| 场景 | baseline中位ms | candidate中位ms | reduction |
| --- | ---: | ---: | ---: |
| steady_cli_add | 2.341841 | 2.348000 | -0.263% |
| first_upgrade_cli_add | 2.183406 | 3.378342 | -54.728% |
| constructor_upgrade | 0.697417 | 1.629011 | -133.578% |
| constructor_repeat | 0.689905 | 0.669855 | 2.906% |

唯一新增稳态CLI控制退化≤15%门槛通过。首次CLI约+1.195ms、构造器首次约+0.932ms，是实测升级成本，未套用或放宽速度门槛。诊断双主≥20%/每控制≤15%已独立复测通过，仍按原范围接受。未独立重做完整CLI 21对计时；本次独立复现聚焦真实最终源schema/API/CLI语义，集成raw做完整重算。此前诊断已经独立21对重测，且本次证明其已装索引API路径的等价边界。

reviewer/implementation-compression-check.json确认公共raw.json.gz及reviewer/raw.json.gz解压后逐字节等于各自私有原始数据，compressed/uncompressed SHA256均符合compression.json。压缩未删除样本、clock、EQP或失败记录。报告草稿的API表/集成表、索引文件增长106496B、旧库/CLI失败边界、非原子初始化与同名索引限制均与实际数据/代码一致；报告没有把首次升级称为净加速。后续最终报告若变更应另核对。

## 六项检查与剩余门禁

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| implementation | pass within scope | 最小2行DDL、隔离module globals、真实生产schema和非空文档升级、业务错误/回滚验证。 |
| reference_boundary | pass within scope | 与旧模块/诊断手工DDL比较完整schema和index_xinfo；原诊断60组独立图oracle；实际CLI/旧库/同名对象边界。 |
| data_integrity | pass within scope | 固定source/依赖/计划/集成脚本与原始数据hash，168样本/完整pair/order/clock/状态hash检查，无损压缩复核。 |
| numerical_sanity | pass | 有限正ns、精确中位比值/控制门槛重算，升级开销与物理页增长单列。 |
| measurement_validity | pass within scope | 完整真实main/init路径、独立fresh副本、对称stdout、升级/稳态分开；不包含进程启动。 |
| reproducibility | pass within scope | 实际最终源四组边界和四项unit通过；诊断独立重测可复用的等价性已证；未另作CLI性能独立重复。 |

已实际读取最终full-tests.log：1218项、63.067s、OK(skipped=8)；reader-tests.log：3项、1.565s、OK；optimized-memory-result.json：36项、errors0/failures0、successful=true。原首轮full仅generated plugin reference同步失败，保留为full-tests-before-sync.log；随后同步三份生成引用后完整重跑成功，源码仍7df8e23e、四项测试未变。父原-O exit0但summary被捕获，最终TestResult JSON明确计数，未把空summary当通过证明。这些全库/Reader/-O是父产出日志的独立读取核对，非本审查者重跑全部套件；本审查者另独立执行了四项unit及四组真实边界。

最终报告追加的1218/8skip/63.067s、Reader3、-O36以及先失败后同步重跑叙述与实际日志一致，API/集成/升级成本数字及限制前文已逐项核验。批准本固定实现和结果在声明范围内使用，不是未执行的远端发布声明。父仍须最终源/证据冻结、fresh fetch/reconcile和实际远端tree/SHA读回；不引入managed信任主张。

原诊断oracle失败、原四项测试修前3fail、首次CLI成本与控制退化均保留。整个MEM-STORAGE-01继续开放；无模型KV、QA、token、TTFT、RSS/GPU或真实服务吞吐主张。
