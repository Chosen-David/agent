# 本轮增量代码与产物地图

现有入口：`setup.py` 安装主 AI/Skills；`config/role_registry.json` 注册角色；`prompts/orchestrator.md` 路由；`agent_runtime/` 执行与验收；`scripts/sync_plugin_references.py` 生成独立插件资源。本文件是知识库升级的增量地图，不宣称已盘点全部历史产物。

| TASK | 实际锚点 | 生产者 → 消费者 | 用途 |
|---|---|---|---|
| T19 | `knowledge/entries/`, `knowledge/FORMAT.md` | 知识维护者 → 建模 Skill | 一般知识、来源、前提、版本与关系 |
| T19 | `agent_runtime/knowledge.py` | 主 AI 实现 → CLI/ReportingHandler | 校验、检索、引用身份与依赖闭包 |
| T19 | `agent_runtime/knowledge_index.py` | 主 AI 实现 → CLI/建模 Skill | SQLite FTS5 增量索引、排名融合、章节导航 |
| T19 | `agent_runtime/knowledge_ingest.py` | 主 AI 实现 → 学习流程 | 候选原子导入、来源哈希凭据 |
| T20 | `plugins/research-assistant/skills/model-with-knowledge/` | sync 脚本/主 AI → 独立 Skill 宿主 | 流程、脚本和字节一致的语料快照 |
| T20 | `agent_runtime/task_manifest.py` | 任务执行者 → 独立验收/主 AI | 已声明知识在执行前后与验收时复查 |
| T21 | `prompts/math_knowledge_continuous_learning.md` | 主 AI → 用户选择的调度器 | 有界学习、证据验收、更新发布 Prompt |
| T21 | `evals/knowledge/queries.json`, `scripts/eval_knowledge.py` | 主 AI/维护者 → 验证流程 | 可重复文件/索引检索比较 |
| T21 | `docs/knowledge_validation/`, `tests/test_knowledge*.py` | 主 AI/独立测试 Agent → 用户/维护者 | 程序、检索与真实使用证据；不混为部署证明 |
| T22 | `TASK.md` | 主 AI → 用户/后续维护者 | 本轮授权、验收与 main 发布读回 |
| COMM-02 | `agent_runtime/communication.py` | 可信 host adapter → 按任务订阅的消费者 | 事务投递、幂等事件、版本隔离、回执与现有 handoff 消费 |
| COMM-01/03 | `workflows/agent_communication_workflow.md`, `docs/communication_research.md` | 主 AI → 科研角色/持续优化任务 | 有证据的通信设计、定向反馈、研究候选与验收边界 |

`.knowledge-cache/` 是可重建索引；`.agent-runs/knowledge-v1/` 是当前运行临时状态，均不提交。未移动历史目录或活跃作业路径。

T23 增量：`knowledge/entries/math.linear-system-stability.*` 等5条、`agent_runtime/knowledge.py` 的context/双向related、`knowledge_index.py` 的Porter/engine_version/事务重建、`evals/knowledge/*queries.json` 与 `docs/knowledge_learning/2026-10-06-round2/`。生产者主AI与独立使用D/E/F；消费者为建模Skill、维护者与最终验收。

本轮知识学习增量：

| TASK | 实际锚点 | 生产者 → 消费者 | 用途 |
|---|---|---|---|
| MATH-11 | `knowledge/entries/math.eigenspace-gap-perturbation.*`, `docs/knowledge_learning/2026-10-07-subspace/verify.py` | 主 AI/知识维护者 → 建模 Skill/科学验收 | 谱隙、投影打分、物理模态、采样边界及近期原文审查；有限验证非模型收益 |
| MATH-12 | `docs/knowledge_learning/2026-10-07-subspace/report.md`, `tests.json`, `retrieval.json`, `publication.json` | 主 AI/现有eval与sync脚本 → 用户/下轮维护者/独立插件消费者 | 程序与结构检索验收、版本固定及main发布读回 |
