# [INDEX-03] 交付用户指定《子空间设计改进建议_by_gpt.md》，包含数据结构/消费者、区域inclusive预算、增量维护、成本模型、最小实验链与停止规则；不改SGLang或生产行为。

Task-ID: INDEX-03
Date: 2026-10-07

## Plan

交付用户指定《子空间设计改进建议_by_gpt.md》，包含数据结构/消费者、区域inclusive预算、增量维护、成本模型、最小实验链与停止规则；不改SGLang或生产行为。

## Progress

### Preserved implementation and evidence

- [x] [INDEX-03] 交付用户指定《子空间设计改进建议_by_gpt.md》，包含数据结构/消费者、区域inclusive预算、增量维护、成本模型、最小实验链与停止规则；不改SGLang或生产行为。

交付文件v1.0 SHA256：6c5190590c202af78b326cb9bf717d8e8b60a2a0185efa4eb9b2ab2aebd52e20；可复跑脚本包含于文档，SHA256：73d5dd345667baf9757a946fef71b384f9cc0bdf829874353f43ffd4fe1b1a6b。该独立文档已交付，论文材料不镜像进公共知识仓库。

结果边界：三模式toy认证模拟与全量top-k一致，但64键中仍需查询48/63/50个真实分数；脚本预先计算全量truth用于核验，这些不是实际FLOPs/带宽节约。优先低成本结构化表示与残差诊断，复杂投影/严格生产认证待证据。下一owner为主AI，按文档E0实际adapter核对→E1固定trace损失分解→冻结至多两候选→E2/E3模型质量→E4匹配端到端成本接续；上述模型/GPU验收尚未执行，不属于本次设计交付已完成部分。

### Historical context

Original task: [line 375](../legacy/TASK.d9d62758a6294a346955315378ee6849aa5c1e6f072e8b23ff3ef7bebcadd650.md#L375).
Shared methods, results and evidence: [source section, lines 371–379](../legacy/TASK.d9d62758a6294a346955315378ee6849aa5c1e6f072e8b23ff3ef7bebcadd650.md#L371-L379).
Source SHA256: d9d62758a6294a346955315378ee6849aa5c1e6f072e8b23ff3ef7bebcadd650
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
