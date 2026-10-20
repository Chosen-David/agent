# ARTIFACT-FD-77：读取拒绝路径描述符释放

Task-ID: ARTIFACT-FD-77
Date: 2026-10-20

## Plan

EXECUTE：用户授权 Agent 仓库可靠性修复与直接发布 main。基线 91114412e26d85ae06be5421e42e11bf84fee9c6。GUIDE.md 为空且只读。只修改结果读取资源所有权、相关测试和本任务证据。

历史 artifact-read76/independent.md 已定位目录 fd 泄漏；保留历史原始数据。结果 CLI 查询 directory descriptor leak 存在缺失 record.json，不能证明完整检索；直接核查该独立记录。知识查询 file descriptor ownership closefd 仅供定位，资源契约以 Python 官方 open/closefd 文档和实际测试为准。已有十篇阅读见 read-boundary56/research_a.md、research_b.md，不声称本轮新读十篇。

方法：原始 fd 由 _bytes 独占；fdopen(closefd=False) 仅借用，外层 finally 关闭，保留读取算法、上限、路径及摘要规则。避免依赖失败构造器是否接管 fd。生产者 → 独立六项验收 → 报告/发布；独立 reviewer fd77_review。无已安装监督服务或 ManagedEngine 回执，仅宿主独立工具审查。

验收：真实目录重复拒绝每次零 fd 泄漏；构造/读取失败和成功路径均释放；修前失败记录必须保留。原有分配、增长、摘要、派发测试通过；全库与 Reader 回归。独立检查 implementation/reference_boundary/data_integrity/numerical_sanity/measurement_validity/reproducibility；指标为泄漏 fd 个数，非速度主张。发布前 fetch、仅明确文件、非强制 main 更新和远端树核验。

## Progress

- 已确认干净独立检出和独占 /tmp/agent-audit.lock；待复现、实施及独立验收。
- 计划经独立fd77_review批准：显式closefd=False借用、精确fd验证、单次关闭及异常语义核对。新增4项回归修前2失败；修后45项专项通过；全库1318项、8跳过，Reader3项通过。独立22组对照旧版泄漏13个fd、候选0，21次成功open各关闭一次。详见agent_doc/results/artifact-fd77/；最终独立报告和发布回读为消费门禁。
