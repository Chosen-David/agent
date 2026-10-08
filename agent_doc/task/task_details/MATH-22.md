# [MATH-22] 同步索引、按需引用与成本证据，完成检索及程序回归；刷新main直接提交并独立读回后更新续接状态。

Task-ID: MATH-22
Date: 2026-10-07

## Plan

同步索引、按需引用与成本证据，完成检索及程序回归；刷新main直接提交并独立读回后更新续接状态。

## Progress

### Preserved implementation and evidence

- [x] [MATH-22] 同步索引、按需引用与成本证据，完成检索及程序回归；刷新main直接提交并独立读回后更新续接状态。

证据：docs/knowledge_learning/2026-10-07-dependence/report.md。39项公开有限开发检查通过；一般推导为人工核查，非Lean或未见模型验收。均值ESS不得移用于外积/子空间；最新空间依赖论文条件仅作候选，不改生产或SGLang。现有优先游标保留。

MATH-22发布闭环：实现commit ce000b6f13aec7c6d36bc58fbccc9f059fadd53e、tree 91e39460d9f326087bff1bd865cdb8e5d7b71633 与本地验收树一致，expected_sha/force=false直接发布main；API、独立ls-remote及Git完整tree读回通过。82条=80published+2candidate；39有限检查、4新/21旧题双后端无新增退化、548程序540通过/8跳过及Reader3/3。单条3521 tokens是编码计数，不是模型质量或账单收益；研究候选不接入生产。回执见本轮publication.json；下一步为未知ACF、外积依赖与固定块留出，保留既有优先游标。

### Historical context

Original task: [line 458](../legacy/TASK.e079e84feba90847fb80edd8a3c4064319c4dcefa26ba97250b14c49ab5fd55a.md#L458).
Shared methods, results and evidence: [source section, lines 445–462](../legacy/TASK.e079e84feba90847fb80edd8a3c4064319c4dcefa26ba97250b14c49ab5fd55a.md#L445-L462).
Source SHA256: e079e84feba90847fb80edd8a3c4064319c4dcefa26ba97250b14c49ab5fd55a
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
