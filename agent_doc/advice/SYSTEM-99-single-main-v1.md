# SYSTEM-99 单主 Agent / 多 Skill 迁移 v1

Status: aligned
Authorization: 当前用户明确要求一个主 agent、多个 skill、一次一步沿任务链执行，禁止多 agent 并行开发。
Base: 2fd4865210a219527b25bbabd35fad8ae6b8df37

## 已核对的差异与实施顺序

- 16 个专业能力已有 SKILL.md 和 registry，不另建角色库或 TASK。setup.py 当前为每个 Skill 生成 `.claude/agents/agent-*.md`；改为只安装 Skill 和主入口。旧受管入口仅在原指纹未变时清除，编辑冲突在写入前停止，不触碰用户自建 agent。
- 主入口仍要求 planner-main/review-main，且 orchestrator 明示有界并行。建立唯一单主控契约，入口和各 Skill 导航到该契约；专业阶段由同一主 agent 顺序调用。旧双主控资料作为历史协议保留，不能作为自动创建第二 agent 的指令。
- core.Engine.tick 的 SQLite 事务一次领取一个节点，但没有阻止另一 tick 在前一步 doing 时领取另一节点。增加事务内单活动步骤门禁；等待或不明确副作用的步骤不允许后续步骤越过。依赖、授权、证据、更正、取消和原预算保持。
- 角色进程入口不能继续偷偷创建独立模型。为当前主 agent 提供只读 Skill 加载入口；旧执行入口改为明确迁移错误，离线预览保留诊断兼容。不会启动、重试模型或 tmux。

## 验收与诚实边界

先固定修前失败：安装 16 Skill / 0 子 agent；升级删除未修改的受管旧入口、保留编辑冲突；真实 SQLite/并发 tick 同时最多一个 doing，重启继续当前步骤；Skill 加载不执行任何模型。修后实际安装/加载/恢复与相关既有回归，再检查全库和包内引用。旧独立结果合同不改成主 agent 自批：同主 agent 切换复核 Skill 只能称自检，必须独立验证的结论继续 pending，缺后端如实保留。

这次是 SYSTEM-99 的授权架构变更，不是新一轮优化或新的论文计数。旧失败、原始证据和耗尽测试额度不重置。当前迁移验收不证明模型任务质量、token/费用提升、真实宿主部署或所有历史协议已迁移。agent_doc 不迁目录；guide 只读，唯一 TASK/MemoryLedger 和当前未决项延续。
