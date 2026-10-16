# MEM-HISTORY-INDEX-08 实施/集成独立结果审查

**最终实现及集成结果：usable-with-scope。完整回归已读回通过，发布冻结/远端读回仍须完成。** 本报告是另行派发的人工独立代码/数据审查，不是managed receipt、ReviewSession或自动可信认证。仅Agent公开history/CLI audit接口；无内部runtime/model KV性能主张，TwoLevel暂停。未修改生产源、测试、计划、文档或guide。

## 身份与实际源审查

基线c854e274fea7e72a574bf1377d7f38679832812d，诊断源7df8e23ecee946e996b828fb702258e03dabe2306b42c63a3daadf15008d950e。最终source SHA256 `3ab5bf98029e56ed98f1702bc0ee0fba19ef1176284fe440705b04b073d0422c`；新test SHA256 `98872a24b616f16acbb0c72bed82fabc0876ad46501952e412c5d9401bb17be2`。implementation-source.py保留快照；implementation-hashes.json绑定源/测试、workflow/三份generated引用、计划、baseline、integration code/raw/log以及独立探针/结果。

实际对比固定baseline.py：唯一生产源差异是在events建表后加两行`CREATE INDEX IF NOT EXISTS memory_events_entry ON events(entry_id)`。公开查询、ORDER BY sequence、完整_get/历史装配、纠错/事件写入/事务和CLI派发均不变；无缓存、截断、排序改写或新runtime消费者。实际工作流文档与三份同步引用说明完整sequence历史、写入/空间成本以及继承既有升级/失败CLI/same-name边界，没有许诺模型性能或整个迁移原子。

诊断独立接受在前，源码阶段随后才开始，使用计划已有条件式范围；只做这个DDL候选，没有调输入/阈值/第二候选。源阶段从约08:12开始的15分钟预算由父执行者维护，本审查实际语义测试在integration结束通知后执行，结束即通知父启动完整回归；未与任何任务计时并发。

## 实际独立验证

执行reviewer/implementation_verify.py及tests.test_memory_history_index六项unit；4个独立边界组和6项unit全部通过（implementation-verification.json/log、implementation-unit.log）。

- 用固定旧模块的public add/correct和真实snapshot_project_docs创建四份非空document_dependencies。额外插入负sequence、0、间隙90及倒退时钟。普通候选构造/history/list/impact/check不安装索引、物理字节/schema不变。真实create=True升级及重复升级后全部entries/deps/document bindings/events/sqlite_sequence逐字段精确不变，所有旧clock未被规范化，完整旧history packet及[-20,0,1,90]顺序不变。重复初始化物理字节也不变。
- 真实生产索引metadata为非唯一、非partial、entry_id升序BINARY键、隐式rowid辅助项，无表达式。index_xinfo完整等于诊断手工DDL。真实新库的全部schema与诊断candidate schema仅可忽略DDL空白/IF NOT EXISTS存储语法差异，其他表/原reverse index一致。实际history EQP为非covering USING INDEX，且无temp-sort。SELECT *不冒称covering，也没有“消除基线排序”的虚构收益。
- 因API源码完全不变、真实安装schema与诊断相等，允许复用**本轮**已接受诊断的索引已安装后六个完整API计时；不复用为第一次init/CLI净收益，不用旧reverse-index轮数值。
- 普通Python add在旧库不安装本索引。真实production-index图中lineage前置失败及c的stale事件写后异常完整回滚，正常correct保留superseded b、stale c和新revision文档snapshot。实际CLI duplicate-ID add返回2，初始化索引已安装而所有业务行/clock/sequence不变，清楚区分初始化与entry事务。
- 同名错列index、另表同名index均原样保留；同名table碰撞MemoryError且原业务/schema保持。没有自动drop/rebuild，不对自定义schema许诺性能，也不推广为任意DDL/磁盘/权限/并发故障的全迁移原子保证。
- baseline/candidate分别用独立module globals加载，类不同，main.__globals__均绑定其自身类。各实际调用一次main(add)验证稳定完整packet相等、返回new-entry clock等于真实DB值，防止基线误调用候选类。

## 集成raw独立重算

实际integration.py使用measure.seed(...,baseline.MemoryLedger)明确建立未安装新索引的固定50000条目/事件输入。每个样本新副本；steady/repeat候选在计时外真实create=True预装索引，first-upgrade候选起点未装索引；baseline保持其旧部署schema。四场景21对、3warmup、seed81602随机AB/BA，全部main参数固定new-entry/claim/new/synthetic:experiment/verified/无deps。

完整CLI timer包含main的argparse、init/DDL/commit、entry写事务、JSON格式化及对称StringIO print；不含Python进程启动或真实外部stdout写成本。constructor timer含完整create=True。input/snapshot/copy/equality在timer外。integration raw自带source/script hash，均与实际冻结字节匹配；baseline源亦与固定Git/诊断源相符。

integration_verify.py独立核验168个样本，所有pair/arm唯一且顺序符合包括warmup在内的RNG，全输入hash等于诊断add50000，正有限ns、精确中位数/比值、每pair完整output/state hash相等。CLI仅new-entry/event sequence50001 clock允许规范化，原始clock非空合法SQLite UTC；constructor没有新clock且state hash精确等于原input hash。各场景索引预装/未装起始物理大小、关闭后页倍数、升级/重复init大小符合记录，未要求跨schema物理字节相同。全部原始样本和控制负值保留。

| 含完整初始化的场景 | baseline中位ms | candidate中位ms | reduction |
| --- | ---: | ---: | ---: |
| steady_cli_add | 2.378972 | 2.526353 | -6.195% |
| first_upgrade_cli_add | 2.437768 | 10.249791 | -320.458% |
| constructor_upgrade | 0.862812 | 9.440863 | -994.197% |
| constructor_repeat | 0.818416 | 0.836602 | -2.222% |

唯一新增稳态CLI控制退化≤15%门槛通过。首次CLI额外7.812023ms、constructor首次额外8.578051ms，是升级成本，未设速度保证/事后换门槛；必须单列，不能称第一次请求已净获益。重复init约+0.018186ms。此前独立诊断六门槛已全部通过，首/尾分别72.81%/69.38%，其余控制逐一不超过15%退化。

未另行独立21对CLI性能重测（父明确不要求）；本次独立复现专注最终schema/API/CLI语义，CLI性能做全部raw独立重算。此前诊断已完整21对独立复测，本次实际证明其schema/API等价性，足以支持所列限定复用。绝对时间差和IQR在integration-verification.json保留；不作统计显著性、跨硬件或普遍吞吐保证。

compression.json两项compressed/uncompressed SHA复核通过，gzip解压逐字节等于私有原raw及独立raw，未丢样本/clock/EQP。implementation-compression-check.json保存观察。最终report.md已实际读取，API/集成表、首次升级成本、文件增长、非covering/无baseline-sort机制、真实audit消费者和旧库/CLI边界均与实测一致。报告已澄清raw仅留完整对象hash、完整对象在运行时逐字段比较；baseline checkout复现口径正确。最终manifest/实际staged tree仍需冻结后另核验。

## 六项标准

| 标准 | 判定 | 实际依据 |
| --- | --- | --- |
| implementation | pass within scope | 精确2行DDL、独立globals、实际index完整属性/全schema、legacy/非空docs升级和CLI副作用。 |
| reference_boundary | pass within scope | 固定旧模块+诊断DDL对照、负sequence/间隙/逆clock全packet、同名对象、真实纠错/history/rollback。 |
| data_integrity | pass within scope | source/script/baseline/plan hash、168pair样本/clock/状态/输入/物理状态与无损压缩核验。 |
| numerical_sanity | pass | 正有限ns、独立中位比值/15%控制重算，首次升级成本及720896B诊断文件增长分开。 |
| measurement_validity | pass within scope | 完整真实main/init、fresh副本、baseline显式seed、对称stdout、steady/first分离，父串行测量。 |
| reproducibility | pass within scope | 独立实际4组最终源边界+6unit；诊断独立21对复测经真实schema等价验证后限定复用；未重测CLI21对。 |

最终源码/集成数据无阻断。已实际读回父full-tests.log：1224项、63.681s、OK(skipped=8)；reader-tests.log：3项、1.558s、OK；optimized-memory.json：42项、errors0/failures0、successful=true。源hash仍3ab5bf98，报告追加的最终数字与日志一致。全库/Reader/-O为父执行日志的独立读取核对，不冒充本审查者再次全量执行；本审查者另执行6unit和4组真实边界。verification.json保留独立人工语义及生产回归的不同来源，不创建managed proof。

另执行normalizer_verify.py三个非法输入探针，旧clock变化、非法新clock、未授权new-entry身份均按断言拒绝；原harness normalized代码在唯一两行DDL变化前后未变。normalizer-verification.json/log保留结果，支持报告“clock负向检查”的具体范围，不泛称任意clock都被history审计接口校验。

允许固定实现/结果在已述范围内使用。发布还须冻结最终源/证据、manifest/实际staged tree检查、fresh fetch/reconcile和远端SHA/tree/字节读回。人工usable-with-scope不等于managed信任或发布已完成。MEM-STORAGE-01保持打开，无KV、QA、token、TTFT、RSS/GPU或模型服务收益声明。
