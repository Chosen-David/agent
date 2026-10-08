# [MATH-16] 更新学科/问题结构检索与插件快照，记录推导、公开验收及真实成本边界，执行回归；重新同步main后直接发布并独立读回。

Task-ID: MATH-16
Date: 2026-10-07

## Plan

更新学科/问题结构检索与插件快照，记录推导、公开验收及真实成本边界，执行回归；重新同步main后直接发布并独立读回。

## Progress

### Preserved implementation and evidence

- [x] [MATH-16] 更新学科/问题结构检索与插件快照，记录推导、公开验收及真实成本边界，执行回归；重新同步main后直接发布并独立读回。

主AI单一写入者；证据 `docs/knowledge_learning/2026-10-07-algebra/`，接续 `.agent-runs/math-krylov/`。本轮转向用户明确指定线性代数/高等代数，既有矩阵集中下一主题保留；不修改SGLang，不把精确代数维数当作浮点近似秩或Agent性能保证。当前宿主无tmux/真实模型适配器，不声称后台部署。

### Historical context

Original task: [line 353](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L353).
Shared methods, results and evidence: [source section, lines 350–356](../legacy/TASK.b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384.md#L350-L356).
Source SHA256: b537d62002c8478825021eef769c6482faa0d2926d604df95467c45595e80384
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
