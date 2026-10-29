结论：**revise（两处局部精确性修订，无需重做阅读）**。

1. `reading.md:13`：“attachment因原执行未注入”过于绝对。附录A.1是“matched memory need not have been supplied”，不保证一定未注入。建议改为：“attachment不能保证已有真实pre-action context，因此按论文使用任务描述＋新提案构造context。”

2. `reading.md:11`：候选排序漏了同类型候选间的“trigger gain”。附录A.2顺序为：改善类型优先 → 触发任务增益 → 历史最差margin → 较小编辑。建议补全，避免把历史margin写成类型之后的首要排序项。

其余重点核对通过：

- `reading.md:20`准确区分ConMem外部基线与本实现零注入，数字一致，并明确零注入仍建设/评估记忆；未把主表差值解释为纯策略因果收益。
- 单次运行、孤立注入而非多记忆边际贡献、累加avoid不可撤销、Scope误归因、不可逆任务重放及成本缺口均有明确限制。
- `correct()`创建`user_confirmed`修订及后代stale的说明与代码一致；真实用户来源仍由host核验。未把模型修复提案升级为用户更正。
- 未发现本库性能提升、复现实验或全轮完成主张；SYSTEM-99仍明确open。
- `inputs.json`全部cache_refs及source_refs均与当前文件SHA256匹配。哈希匹配不证明历史实际阅读或科学有效性。

实际阅读：AGENTS.md；reading.md、inputs.json全文；paper.txt字符`[0,41182)`（补齐Limitations/Ethical Considerations）及`[52336,87341)`；指定project_memory.py、handoff_basis.py范围；project_memory_workflow.md全文，另读project_document_workflow.md。

限制：本次仅一次独立静态AI审核。未读参考书目正文、PDF像素、作者代码或原始实验轨迹；未执行论文prompts、仓库代码、后端或测试；未写任何文件，未重开旧门禁。本反馈不是受信ReviewSession回执，也不构成实验复现或系统验收。
