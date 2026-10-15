# MEM-STORAGE-REG：让已有记忆实验可被检索，保留验收边界

2026-10-15；本轮基线main `14cee3ac6470a5c1bd327756ed500a2e142d907e`。继续MEM-STORAGE-01已有批次，不把维护登记计为新算法或新一轮推理提速。

## 确认的问题与修正

上一批 `memory-storage-20261015` 的实现、原始样本、独立审查及12篇论文阅读矩阵已发布，但没有 `record.json`。真实 `ResultStore.search` 尝试读取该目录时抛缺文件错误，无法把已完成的实验作为候选返回。主AI未来检索可能遗漏历史、重复实验；此次补齐本任务自身交付遗漏，不推广为全库记录自动修复。

使用现有 `ResultStore.register_history` 原子创建唯一历史索引，固定8个真实文件/hash：原manifest、主测/独立raw、独立review、report、research、measure与第一版负结果。**没有改写这8个文件或旧manifest，没有改runtime、查询排序或实验数字。** 记录来源为historical-external-reference，contract=null、validation=unknown/proof=null；手动独立审查报告可被找到，但登记不等同当前受信任验收。未伪造原生受管ReviewSession、服务部署或模型实验。

## 实际查询对照

查询在登记前固定，真实仓库同一入口，limit5/max-scan200。摘要是实际测量及边界说明，未因宽泛查询未命中继续堆词或修改检索器。输入、前后top5、扫描及错误数见[query_check.json](query_check.json)。

| 查询 | 修前目标排名 | 修后目标排名 |
| --- | --- | --- |
| MemoryLedger SQLite retrieval | 未进前五且记录解析失败 | 1 |
| memory-storage-20261015 | 无候选 | 1 |
| memory scope retrieval | 未进前五 | 仍未进前五，负结果保留 |

三者都只扫描200目录，partial=true。缺目标record错误消失，其他错误仍61项（原62项），没有宣称全库检索完整。两个具体导航查询0/2→2/2首位，仅证明该历史结果可发现；不是问答质量、语义检索召回率、模型memory或KV命中收益。

复验入口（只读）：

```bash
python agent_doc/results/memory-storage-20261015/registration-20261015/check_registration.py
python -m unittest discover -s tests -p test_result_store.py -q
```

新检查核对8个artifact hash、specific查询候选的unknown/unchecked状态、空/已知部分context的6组decide_run结果：未获验证只verify_delta，new_claim/明确复现必rerun，proof为空、automatic_skip_authorized=false。既有ResultStore21项回归通过；不重复全库性能测量来制造新收益。

独立上下文另读实际record、Git基线8文件及前后搜索；重复登记拒绝且字节不变，隔离副本中的raw改动触发rerun/stale，当前未认证结果不可自动reuse。独立证据见[independent.md](independent.md)与[independent.json](independent.json)，不是新的原生验收凭证。

本轮另跑项目文档回归64项通过、canonical文档validate通过，检查脚本普通及-O一致。最初误用 `test_project_docs.py` 模式得到0 tests/exit5，不计通过；更正为 `test_project_docs_*.py` 后才得到64项。两份短回归日志一并保存；此次无runtime改动，未重跑全库或旧性能实验。

环境沿用Python3.12.14、Linux x86_64，本轮没有模型、GPU、远程KV存取或性能基准。12篇原文的方法/实验及适配决策复用上轮冻结research.md，未冒称本次重新精读12篇；KVFlow/LMCache等仍需真实引擎适配和实际TTFT/质量验证。跨任务scope装配优化只是未实施候选，此次没有用登记替代该优化的性能证据。

## 下一步

当前模型KV后端/遥测接口仍需实际接入，不能用Python字典或结果索引替代。宽泛检索未解决；未来若改善检索，应冻结未参与调优的真实需求及排序强基线，保持原始证据、修正依赖和当前独立验收。本次仅允许找到旧证据，不允许自动复用旧结论。
