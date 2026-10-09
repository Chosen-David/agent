# advice 上下文与多 AI 治理：本轮结果

任务：CTX-20261009-01；起始 main：bb5bf5b8edaebd8910f9a7af28830c668113d339。

设计文档：[长上下文、advice 生命周期与多 AI 协作](../../../docs/advice_context_governance_by_gpt.md)。原文保留、项目记忆与通用知识分层、增量处理记录、逻辑归档、多主提交、跨机边界和真实模型实验设计均在其中。自动整理、删除、索引服务及跨机协调尚未部署。SGLang 本地不可读，未改动，也未核实其当前 advice 数量。

## 实际修复

- `task_document_refs` 在深拷贝之前只保留本节点 adopt/adapt 的 advice inventory。全局 inventory/逐项评估、全部人工指南、当前稳定任务依赖与未知扩展字段保留。没有意见摘要或自动知识提升。
- 15份文档副本与1份runtime副本同步；另修复已有 code-reading_execution 生成副本缺少源规范的两行内容。未修改该源规范。
- WRITE-EVIDENCE 缺 Task-ID/Date 且使用非契约标题；MATH-55/56/57 缺身份字段。仅补格式字段，所有其他字节保留；原件在本run。项目快照恢复为194详情、2指南、7 advice。既有冻结计划的稳定hash/节点形状发生变化时仍须显式重规划，不自动改写历史回执。

## 同输入表示体积

标准库、UTF-8、相同最小JSON序列化；原始数据：[raw.json](raw.json)，复现：[measure.py](measure.py)，冻结基线：[baseline_project_docs.py](baseline_project_docs.py)。比较的是全部节点的document_refs列表，以及全局project_documents加节点列表；不含完整DAG、模型提示、工具包壳或调用费。

| 公开输入 | 节点/意见数 | 节点列表：旧→新字符 | 全局＋节点：旧→新字符 |
|---|---:|---:|---:|
| 无 advice | 1/0 | 706→706 | 1232→1232 |
| 合成适用范围 | 4/50 | 22585→4377 | 28979→10771 |
| 合成适用范围 | 40/500 | 1960371→52361 | 2021349→113339 |
| 当前仓库结构、无采纳意见 | 194/7 | 263621→114629 | 291406→142414 |

最后一行是结构诊断，空采纳/空指南评估不是可派发的当前项目计划。各节点除advice字段外与旧实现逐对象相同，原全局快照不被修改。没有 advice 时体积相同；所有意见都适用某节点时该节点也不会减少，不能声称普遍固定比例节省。

实际tokenizer不可用，tokens=null；未把字符折算token。没有真实模型、账单、KV缓存、推理延迟或正确率A/B，不声称效果更好或收费下降。

## 检查、失败与验收边界

公开新增7项程序测试覆盖adopt/adapt、无适用意见、多任务交集、脱离源对象的复制、另一任务来源、遗漏全局处理、陈旧采纳和全部指南集合/内容变化。经task_manifest完整契约和任务消费方核验；既有ManagedEngine等回归继续检查受支持入口。它们不是未见模型题，也不证明模型理解适用范围。

初次40项定向测试通过。随后第一次表示实验被历史MATH身份字段缺失阻断，没有发出raw.json；首次全套859项只有生成引用同步断言失败，8项跳过。错误、原脚本与旧日志在 [failed_attempt1](failed_attempt1/)，没有覆盖为成功。

最终全套859项：851通过、8可选依赖跳过；reader 3/3；生成引用检查和git diff --check通过。原始日志分别为full-tests.log、reader-tests.log、mirror-check.log。四份格式修复逐字节核对，仅允许规定的字段/标题替换；原历史状态不变。检索历史55项、22缺record，partial=true；不据此宣称无相关历史，不复用旧性能数字。

计划采用实际独立本地调用审核；第三次有界补充明确记录因发现同类历史缺口而调整本地自设审核上限，未重置任何已部署runtime账本或用户硬预算。最终计划hash固定于plan_review_by_gpt.md。实际独立结果检查与回执由另一个新上下文完成，见independent_review_by_gpt.md/independent_validation_by_gpt.json；生产者自报和测试退出码不构成独立验收。发布状态以publication.json及远端读回为准。本轮不声称已部署ReviewSession、后台监督、真实模型或多机数据库。

## 尚未解决

全局 advice 仍要求完整评估；多主同时写Progress仍依赖唯一作者约定。下一阶段需实现带来源/范围/前提版本的处理记录、可重建索引和可信revision提交，再以同模型/权限/总预算验证质量与总token收益。不能用自动删除、任意跨频率摘要或多数AI同意替代这些门禁。
