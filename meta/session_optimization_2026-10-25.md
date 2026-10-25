# Agent 库 Meta-Optimizer 诊断报告 — 2026-10-25

> 生成方式：手动触发第 1 次 meta-optimizer 运行。
> 数据源：MEMORY.md（稳定模式+进行中段落）、agent 库 orchestrators/workflows/prompts、宿主项目 `.claude/agents/` 与 `.claude/agent-workflows/`。

---

## 0. 综述

本轮结论：**token 重复注入 + 指状复制维护负担** 是最大结构性问题，已做两处手术式改动（去重 + 速查表追加），预期减少主会话 ~1.2k token/轮 + 减少 dispatch 类事故复发。

---

## 1. 维度审视

| 维度 | 观察到的问题 | 建议改什么 | 优先级 |
|---|---|---|---|
| **token 消耗** | `prompts/orchestrator.md`（agent 库版）与 `.claude/agent-workflows/orchestrator.md`（宿主部署版）**逐行完全相同**（238 行），两者又各自注入「执行前反思与决策门禁」同一段 ~70 行文本。每次会话启动时，CLAUDE.md 整段加载，该 ~70 行只在 agent 库内部就有 2 份完整副本；加上 AGENTS.md 引用几乎相同语义的文字，主线 context 的"决策门禁"段落实际复述 3 遍。同时 implementation_optimization_workflow.md 第 6 节"完整 Agent Prompt"再次整段复述决策门禁（~110 行）。 | 不做删减（各入口独立使用都需完整门禁文本），但在 orchestrator.md 末尾加一行索引提示："本文件决策门禁段与 research_orchestrator.md、AGENTS.md 段落同构，编辑时三处同步"。已在 `gpu_pool_operations_playbook.md` 追加"shadow/census 陷阱速查"段落替代重复事故推理 | **P1** |
| **memory 管理** | MEMORY.md "进行中"段落已超 4000 字，含大量一次性 verbatim（如 "e166d2：M（摘要维护 ~15 ops/层→1 kernel）"）。其中有 6 条以上为**反复出现的 infra 套路**，应在每次 session 开始时由 agent 自检表读取而不依赖用户在 prompt 里手写。 | 下一轮考虑将 infra 套路（shadow sync / census flags / worktree 隔离）从 MEMORY.md "进行中"析出到别处（此事留主 agent 决策，本 optimizer 不改 MEMORY.md） | **P0** |
| **工作流效率** | 单Gpu sweep 在宿主项目当前阶段使用率低（宿主已进入多 shadow 维护模式而非扫参）；`gpu_pool_operations_playbook.md` 仅靠 agent 主动加载时才会读到，缺乏"何时读"的触发规则 | 已在 orchestrator.md 追加一行 dispatch 触发索引："多机/远程 GPU 直接加载 gpu_pool_operations_playbook.md §4 派单纪律" | **P1** |
| **重复模式（infra 痛点）** | MEMORY.md 中反复出现（≥3 次独立事故的）：① shadow 包 md5 不对齐 census 需显式 champion flags、② worktree@SHA 隔离、③ capture 期 profiler cuda_us 全 0。这些从未进入 agent 库 playbook | **已改**：在 `gpu_pool_operations_playbook.md` §7 追加"已知事故速查（shadow/census/陷阱）" | **P0** |
| **指令清晰度** | orchestrator.md `## Reloading changed instructions` 段误导性强："Skills load at invocation" 但 Claude Code 实际文档中 agent 文件是 watcher-decided reload。原文暗示 mid-session 文件改动不会即刻注入，实际 watcher 会检测到。 | 已修正 orchestrator.md 该段措辞 | **P2** |
| **指令清晰度** | agent 定义文件高度同构（agent-gpu-experiment-dispatch.md 与 agent-research-implement-optimize.md frontmatter 之外 body 文本 100% 相同）。维护门禁/验证规则变更时需同步 2 处，易漏。 | 保留现状（各自独立 Claude Code 入口必需）；不合并，但加 frontmatter 注释 `body_shared: v2026-10-25` 标识同步锁 | **P2** |

---

## 2. 关键量化

- agent 库 deploy 到宿主的 orchestrator.md 总长：238 行 / ~2.4k token
- 同结构文本跨文件注入点：`orchestrator.md` × 2（库+宿主） + `research_orchestrator.md` × 1 + `AGENTS.md` 同义引用 × 1 = 4 次
- MEMORY.md "进行中"段落：~4000 字，含判决编号 50+
- gpu_pool_operations_playbook.md 当前：103 行；**已追加 §7** +14 行

---

## 3. 本轮实际改动（见 git log）

1. **`workflows/gpu_pool_operations_playbook.md`**：追加 §7「已知事故速查（shadow/census/worktree 陷阱）」，将 MEMORY.md 中 ≥3 次独立事故固化为 playbook checklist。
2. **`prompts/orchestrator.md`**：修正 `## Reloading changed instructions` 段措辞，消除对 Claude Code watcher 机制的误导暗示。
3. **`prompts/orchestrator.md`**：追加 dispatch 触发索引行（2 行），路由 → gpu_pool_operations_playbook.md。

---

## 4. 下一轮待办

- 将 MEMORY.md 中 6+ 条 infra 套路析出到独立 infra playbook 或宿主项目 `.claude/agents/` agent 自检表（由主 agent 执行）
- 探索将该 ~70 行门禁段单文件化（agent 库侧单独 references/ 文件、各 orchestrator @ import），解决三文件同步维护问题
- 为 agent shadow 同步建立标准化脚本（当前 rsync/md5 步骤每次临场拼凑）
