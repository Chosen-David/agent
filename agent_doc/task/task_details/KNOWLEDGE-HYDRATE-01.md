# KNOWLEDGE-HYDRATE-01

Task-ID: KNOWLEDGE-HYDRATE-01
Date: 2026-10-24

## Plan

同未完成的 SYSTEM-99。基线 `3c8cf7f1`：`basis_context` 校验交接后，另取 `KnowledgeStore` 加载正文；两步间更新已引用知识正文，会把旧 `knowledge_refs.sha256` 与新正文/哈希混入同一载荷。不是普通的读取后变旧，也不是知识内容的科学有效性判断。

仅在实际加载正文的同一内存快照上复用 `check_refs`，非空引用才调用；保留原校验、格式、选集、预算及已知引用门禁。没有新缓存、监听器、存储层或模型输入回执。允许一致的旧快照；不承诺原子文件系统快照、返回时最新或跨库事务。

验收：真实临时项目 `Mailbox.publish → prepare_context`，校验后、取正文快照前更新被引用条目或前置条目；JSON/claims-table/basis-table/auto、全量/定向共16交错场景拒绝哈希不匹配。无更新、无关条目更新、取快照后更新保留一致旧正文；空选集兼容有效 known refs，并保持旧引用拒绝。先存修前失败，独立方案审核后改动；Python3.9/3.12 相关回归及独立结果复核后普通发布 main、回读。仅正确性验收，不宣称性能、实际宿主或整批完成。

## Progress

- 先查结果：`handoff knowledge concurrent snapshot`，max-scan200、partial=true且有缺 record 错误；前三候选为语料采用/批量发布/ACK，未据此认定历史穷尽。已有顺序更正探针不覆盖此次调用内更新。原始查询保留在私有检查点。
- 修前两解释器探针均返回旧 pin `8ec1…5792` 和新正文 hash `67a0…0326`；只改 Markdown，版本标签未变。独立修前复现及方案审核接受。最终新增测试修前4方法/16子场景失败均为未抛异常；首次 auto 夹具漏传计数器的日志保留，补 `len` 仅供格式分支，不作为 tokenizer 或性能证据。
- 修后复用探针拒绝 `stale knowledge ref: math.topk-margin`。Python3.9/3.12 各77项相关回归通过；候选生产/测试哈希和完整日志保留于 `.agent-runs/doctor-restart-2302/knowledge-hydration-*0559*`。独立结果复核与发布回读待核。
- 本批已读 Concord `2610.05281v2` 与 PFM `2610.10265v1` 支持区分源有效性、载荷曝光和模型应用；这里只修已有引用/正文身份边界，不移植其存储或 prompt 改写架构，不挪用作者结果为本库收益。

- 独立复核建议补强 known refs 隔离：采用交接 record 之外的 `physics.dimensionless`，更正后无 hint 的真实 wrapper 仍通过，旧 hint 精确拒绝。整库 project_docs 校验另遇基线已有 MEM-SNAPSHOT-01 身份/日期缺失；恢复 HEAD 索引并排除本次详情的临时副本同错，保留为 SYSTEM-99 未决，不借局部回归宣称全库通过。

- 独立结果接受 usable-with-scope：两解释器专项普通/-O各4通过，补强后 known-only 各1再验通过；隔离去掉 guard 的负控两版本均16失败/0错误。生产哈希 `20b4…f50a`、最新测试哈希 `2638…014f` 绑定私有复核报告；主控补强后专项两版本各4通过。仅接受此身份一致性修复，发布回读另核。
