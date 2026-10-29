# VALIDATION-RECORD-FIX-01 v1 / SYSTEM99 proposed Version55

承接已公开d023cfef的构造失败空记录恢复缺口，旧diagnosis plan/producer/verify各1已耗尽，不运行其脚本或重置任何旧门禁。正式检索336目录partial=true/25errors，命中该诊断record70086e18…1745c与两个不适用corpus结果；原始prior-search.json保留。诊断只有构造异常，不能替代新写入/flush/fsync/发布/竞争验证。40篇同批正文继续有效，不冒充新一轮完成。

主控唯一生产writer：只改agent_runtime/validation_context.py本函数，导入tempfile并按proposed-block.txt原地替换旧try-open块。完整serialization、hash、schema、mode600、预算、errors/proof与live验证分离保持。先按当前_path/guard验证；已存在目标仍严格_bytes相等检查，不为幂等重写/再fsync。无目标时同目录mkstemp写入/flush/fsync，关闭FD后再guard并os.link(follow_symlinks=False)不覆盖发布；FileExists只校验当前目标原字节，其余失败直接错误闭合，无replace fallback。finally只清理本方temporary，不删除/覆盖任何既有目标。复用本库ResultStore._save已用标准库发布模式，不调用其不同schema/错误接口、不抽大范围helper，不留旧实现副本。

不保证父目录/暂存inode被敌意替换时的清理、跨文件事务/断电目录durability；没有新增目录fsync，写入内容已fsync而非断电安全声明。link后清理失败可报错但保留已完整发布记录，下次按严格幂等检查；这不是全异常无目标承诺。暂存写失败不可留下最终哈希路径；unsupported link须报原OSError且无覆盖fallback。guide只读、唯一TASK，批准后仅Version54→55并追加阶段AK稳定方案/Progress，不改旧结果/历史。

冻结4新方法new-tests.txt（加入现有ValidationContextTests），生产修复前加入测试：
A 构造/部分write/flush/fsync失败，核FD关闭、最终路径未提前可见、本方临时/最终无残留、撤销后同请求完整恢复；
B EIO/ENOTSUP发布失败无最终/本方暂存且可恢复；
C 精确发布点同字节/异字节竞争目标的原字节/inode保持，仅同字节接受，temp mode及清理；
D 已有完整记录幂等不依赖新fsync/link。
B/C是新增发布机制专项注入，只在fixed/independent执行，不以旧实现从不调用os.link的“未触发”当修前缺陷。baseline仅A及既有9方法；D在fixed执行。固定baseline命令用unittest TestLoader加载现有类，按明确名字排除B/C/D，执行其它全部；fixed/independent运行完整tests.test_validation_context、tests.test_result_validation、tests.test_local_path_guards三个模块。A唯一用于共享修前/修后恢复对照；不能拿两套总方法数作统计提升指标。测试代码/原始oracle修复前冻结，失败和无法继续的subcase如实保留。

先独立方案审核最多2次（revise则保留v1/新v2，新hash批准前不执行）；一次baseline、一次fixed、一次独立verification，单命令120秒、各分支300秒、共享1200秒（含审核）；无重试/扩展旧fullsuite/PID/alias/role/model额度。producer→独立verify→publication，每个分支计数先落检查点。独立须实际读生产差异/固定测试/完整原始日志和hash，按同3模块一次复跑。无性能/模型测量，runtime历史登记unknown，不伪造可信回执。任何失败/超时保留并停止依赖发布，不放宽断言。普通源码/结果发布前fetch/普通main push和13?不预定数量的实际owned-files回读；无外部代码复制、全新依赖或agent_doc迁移。

现有portable-install.yml第52行在四个Ubuntu/Windows×Py3.10/3.12 job运行test_validation_context.py，新增4方法自动进入这4matrix；macOS job只测ingest，不能据其success宣称本修复macOS原生覆盖。检查实际新CI四job/新方法结果，不重跑已耗尽旧CI。用户真实宿主/完整输入/质量/全费用及系统级未决继续open。本方案只本地回归正确性，不称整批完成或性能提升。
