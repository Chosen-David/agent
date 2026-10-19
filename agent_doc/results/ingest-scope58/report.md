# INGEST-SCOPE-58：导入暂存不复制无关根目录文件

日期：2026-10-19；基线 cacbee7663282bcd17b8e08de6b4a00945a0a9fb。范围仅 Chosen-David/agent。独立结果验收及发布状态见后续记录，不以本报告存在作为已发布证明。

## 问题和修复

`agent_runtime/knowledge_ingest.py:37` 原先复制整个语料根目录，再用 `KnowledgeStore(stage)` 验证。但 `knowledge.py:103–125` 只消费 `entries/` 的条目。根目录中的文档、索引、缓存、附件不会参与该校验，却仍被递归复制；无关的悬空链接或 FIFO 会让合法候选导入失败。

改为复制完整 `store.root/'entries'` 到 `stage/'entries'`。不按扩展名过滤，不省略内部附件/未知文件，不变更元数据、路径、引用、候选状态或 provenance。三个语料验证、提交前 snapshot 比较、目标文件系统临时目录和 rename 均保留；独立插件同步同一改动。已有竞态/多写入者约束没有因此消失，不声称文件系统沙箱或原子快照。

Python 官方 [shutil 文档](https://docs.python.org/3.12/library/shutil.html#shutil.copytree) 于2026-10-19查阅：copytree递归复制目录，默认跟随链接，悬空链接会形成错误。这里的缺陷结论来自实际旧代码复现，不由文档或论文代替测试。

## 冻结对照和结果

[计划](plan_v1.md) → [独立计划审查](plan_review.md) → 实施/测量 → 独立结果检查 → 发布。计划hash见审查；本机 Python3.12.14、Clang22.1.3、Linux x86_64、AMD EPYC9V74，虚拟环境9个可见逻辑CPU；无GPU/LLM调用。

[before.log](before.log)：初始6项针对性测试，1 failure、2 errors，分别证明无关缓存被复制、悬空链接和FIFO导致导入失败。保留原始失败。之后增加 entries 内 FIFO 不得被忽略的拒绝对照；最终 [after.log](after.log) 7项通过，包含非法依赖、重复ID、symlink/orphan Markdown、内部附件保留和暂存期间语料变化拒绝。

[measure.py](measure.py) 从固定 Git SHA 加载旧 ingest，调用当前未变的 KnowledgeStore；不是手写近似旧实现。[measurements.json](measurements.json) 保留完整源/输入hash、逐文件逻辑复制计数、预热和全部7次交错配对样本。每次复制相同模板后才计时；输入hash检查会预热文件，故不作冷缓存主张。计时涵盖完整 ingest 的校验、两次复制、rename和清理，不含fixture构建及后续输出对照。复制计数单独运行，未在计时中打点。三组 old/new 全部记录、snapshot、引用和去时间戳provenance完全一致。

| 输入场景 | 逻辑复制字节：前→后 | 完整 ingest 中位数 ms：前→后 |
| --- | ---: | ---: |
| 当前115条语料，原有根文档 | 902199→707292 | 152.440→181.760 |
| 同语料 + 根部16 MiB合成附件 | 17679415→707292 | 162.132→166.061 |
| 同语料 + 根部真实SQLite索引 | 4453431→707292 | 171.307→157.828 |

**不宣称普遍提速**：前两组变慢，第三组较快，单组7次本机温缓存结果不足以推断生产延迟。保留负结果，不重复选样直到变好。可用收益是恢复无关特殊文件下的导入可用性，并减少被请求复制的逻辑负载。该字节计数不是物理磁盘IO、峰值内存或模型token。SQLite场景仅适用于显式放在语料根下的索引；README示例索引在根外，不把本组收益外推为默认配置收益。

## 文献背景与历史范围

本次沿用已完成的十篇原始正文阅读记录：[研究A](../read-boundary56/research_a.md)、[研究B](../read-boundary56/research_b.md)。AgentChaos 的实际故障触发+正常对照和分层记忆的原始语料/派生缓存区分用于选择验证方式；没有移植论文模型或声称算法创新，也不把这些论文再次计为本轮新读。压缩、训练、自主删除记忆仍暂缓：不解决此复制范围问题，且缺同模型质量验证。

[历史搜索](prior-search.json) 扫描237目录，partial=true，68个缺失record错误；5个候选不适用于本次复制范围，未复用其验收。保留历史原始证据和任务，不宣称历史已全面检索。

监督能力：只有真实本地 flock；tmux/受信任常驻 adapter 不可用，不伪造常驻服务或机器认证 ReviewSession。本机独立上下文审核与托管运行时部署是不同结果。

## 回归和独立验收

全量回归：1297 tests，OK，8 skipped，98.891s；Reader：3 tests，OK，1.580s。分别见 [短日志](full-tests.log)、[Reader日志](reader-tests.log)。完整全量输出保存在私有 Git 检查点，SHA-256 为 `47d21b879692e95c75137c0a882adf61d2fa11210920eb1afb621d878b7e0431`；没有把套件耗时作为性能收益。插件生成检查 exit 0（空输出），canonical/镜像 SHA-256 均为 `9e56a59b94feae3ae95bcfcd04aff9752fbbdb8b219b9bb0ec2344d95c58e7c8`。

收尾追加（不改被审核的数据）：[独立结果审核](result_review.md) 已接受为 usable-with-scope。独立旧新语义/字节差分、内部/外部特殊文件、禁止扫描根目录、隔离插件和7项回归通过；48项计时观测的顺序/hash/中位数全部重算一致。只接受可用性与逻辑复制减少，不接受普遍速度提升。[独立脚本](independent_checks.py) 和 [结果](independent_checks.json) 保留。

main发布和远端回读在形成该提交后另行执行，不以本报告预报成功。
