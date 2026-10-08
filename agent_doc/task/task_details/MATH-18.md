# [MATH-18] 同步按学科/问题结构索引、插件快照与成本证据，执行检索及统一回归；发布前同步main并保留并发改动，直接推送及独立远端核对后收尾。

Task-ID: MATH-18
Date: 2026-10-07

## Plan

同步按学科/问题结构索引、插件快照与成本证据，执行检索及统一回归；发布前同步main并保留并发改动，直接推送及独立远端核对后收尾。

## Progress

### Preserved implementation and evidence

- [x] [MATH-18] 同步按学科/问题结构索引、插件快照与成本证据，执行检索及统一回归；发布前同步main并保留并发改动，直接推送及独立远端核对后收尾。

证据：docs/knowledge_learning/2026-10-07-matrix-concentration/report.md。33有限开发检查与4道无定理名结构题完成；真实embedding独立性、未见模型A/B、GPU/物理实验均未执行，暂不改变生产行为。next owner主AI；下一数学主题为依赖/重尾校准与固定抽样协议，保留RL/神经科学优先游标。

MATH-18发布闭环：实现提交 e10795ea51870d2cef4b2763c9dfd13ad57fa02c、tree 7147baccdb9d5a7973b73b105a1128e864e1252e 已以899f6a1为新鲜lease非强制发布；API、独立ls-remote及Git完整tree读回一致。合并保留AIK并发成果与上游测试夹具；80总条目=78 published+2 candidate。33有限检查，4新/21旧题双后端无新增退化，548项540通过/8跳过、Reader3/3；单条包最终3,484 tokens，仅为序列化计数，无模型效果/费用结论。回执见本轮publication.json；本次收尾仅状态/文档，后续数学与既有优先游标可续接。

### Historical context

Original task: [line 439](../legacy/TASK.efc0ca3024bd28a2d50a420270c94cf6938d2dccd1a561cff51baa748ea8c613.md#L439).
Shared methods, results and evidence: [source section, lines 436–443](../legacy/TASK.efc0ca3024bd28a2d50a420270c94cf6938d2dccd1a561cff51baa748ea8c613.md#L436-L443).
Source SHA256: efc0ca3024bd28a2d50a420270c94cf6938d2dccd1a561cff51baa748ea8c613
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
