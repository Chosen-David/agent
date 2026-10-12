# OPT-INPLACE

Task-ID: OPT-INPLACE
Date: 2026-10-12
Owner: root; independent reviewer: accounting_review

## Plan

用户明确要求优化确认有效后原地修改，不常驻冗余旧源码。本轮只修改 Agent 行为规范，不清理用户研究实现。权威源为 workflows/implementation_optimization_workflow.md；优化角色 execution.md 只引用同一规则，使用现有 sync_plugin_references.py 生成主控与独立 skill 镜像。

允许隔离验证；正确性、实测性能与独立验收通过后整合正式入口并更新引用、测试、文档。仅删除本批确认无消费者且有 Git 回滚点的冗余替代源码；必要 reference/基线/fallback 记录用途、入口、测试、理由；保留未验候选、活跃路径、用户修改与原始/失败证据。最终整合需复验和独审。无 GPU、模型或后台服务；不改研究库、SGLang、two-level-attention 或 TOK-FIFTY 状态。

验收：受影响文档/打包契约、全 tests、paper-reader tests、镜像 --check 与独立审查。发布前重新 fetch，整合并发改动后重验，白名单提交及非 force 推 main，读回 SHA/内容/必需 CI。

## Progress

- 基线 bd65a23；既有结果按“原地整合/冗余实现/in.place”检索无匹配复用证据，沿用现有 §4.5 完成门禁和 §5 产物契约。TOK-FIFTY 另有 owner，新 token 机制不重复。c535330 保持未验收。
- 最小规则补充和执行入口引用已实现；验证及独审 pending。这是规范修改，不是用户项目性能实测或模型遵循证明。

- 独立 reviewer accounting_review 验收通过：§4.6/完整 Prompt/实际 skill 入口一致、清理边界与保留例外齐全；23 项受影响测试通过。全仓 1150 项中 1149 通过、1 项既有 opt-in tmux 跳过；reader 3 项通过，镜像 --check 通过。原始日志和源码哈希见 [validation](../../results/opt-inplace-20261012/validation.json)。两份既有知识镜像经生成器同步，canonical 未改。
- 发布前重新 fetch main 仍为 bd65a2348e32d8a70af9e003cbc309064363dd9e，无并发整合；实现和本地验收完成，普通推送/远端 SHA、内容与 CI 读回由主控本轮交接记录。
