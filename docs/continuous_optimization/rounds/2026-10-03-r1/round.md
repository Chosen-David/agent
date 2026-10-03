# R1：让交接完成声明与实际任务一致

日期：2026-10-03。基线：`a5328e407ba1f12a6b887d2206d2eb1258b6cee1`。
决策：EXECUTE，修复既有本地校验契约，不替换架构/领域 schema。
本轮上限三小时、一个独立审阅上下文、无付费模型 API/GPU/第三方 runtime 安装。

## 基线与任务链

读取最新 main、AGENTS.md、决策协议、通用/科研入口、角色与后端注册表、已有评测和来源锁定。
本地初始工作树干净，main 快进补上 Claude marketplace；没有持续优化状态文件或已登记的同候选执行。
沿现有入口追踪：角色产物→主 AI 归一化本地 handoff→显式 CLI/API 校验→主 AI 内容验收。
仓库没有自动调用该校验器的完整运行引擎，不声称端到端所有角色都已接入。

| 任务 | 状态 | 证据 |
| --- | --- | --- |
| R1-READ：核对当前文件与精读论文 | done | paper.md、../../papers.json、environment.json |
| R1-BASE：保留基线并复现缺陷 | done | evidence/reproduction.json、baseline-tests.log、baseline.json |
| R1-FIX：修复并运行验收 | done | scripts/validate_handoff.py、evidence/updated-tests.log、candidate.json |
| R1-AUDIT：独立保留输入及复核 | done | evidence/holdout.py、acceptance.json、review.md |
| R1-PUBLISH：非强制快进发布 | 以 Git 可达性核验 | 引入本文件的提交须在 freshly fetched origin/main；不能只凭本表认定已推送 |

## 预定验收与改动

主要指标：固定无效记录须被拒绝且返回诊断，不得误报完成或崩溃。
非退化：有效交接、可恢复 partial、允许跳过的独立任务、可省略 tasks、既有哈希/路径/依赖检查仍有效；
保持 main 的角色、Claude 接入和领域契约。原测试中的长 DAG 把 completed 与 todo 混在一起，
改为 done+真实 artifact ID，保留长链测试目的；新增 partial 状态检查，而非放宽完成门禁。

修复：completed 中残留 todo/doing/blocked 会失败；task evidence 必须引用登记产物；
blocked/skipped 的理由须是非空文字；坏路径/读取错误返回诊断。文档限定此本地 schema，
并解释旧记录迁移和跳过边界。没有改写所有 skills 或加入重复 Prompt。

## 实际结果与失败保留

- 基线已有 76 项仓库检查通过，但三个最小反例被误放行、符号链接循环抛 RuntimeError。
- 独立审阅者先固定 19 个不同于单元测试的输入；相同 Python、文件、API/CLI 和预算，旧版 6/19，新版 19/19。
  其中旧版 10 例误放行、3 例 API 异常；六个有效控制均不退化。不是开放域成功率。
- 新版仓库 83 项通过；handoff 新测试对旧版运行保留红灯日志。独立上下文读实际 diff 和原始输出，非盲审。
- 阅读器首次三项都因沙箱禁止本机 socket 启动而报错；获准本机测试后 3/3 通过，模型路径为替身。
  保留两份日志，未改测试或把缺测记通过。Git 首次 fetch 也遇到代理连接失败，按获准权限成功重试。
- `evidence_hashes.json` 固定原始证据；`environment.json` 固定实现哈希。没有模型质量、成本/延迟或 GPU 性能提升结论。

## 发布与下一步

发布前 main 新增 `dbfc901ce5de58a09e516ad541406cac52ef0dfa`（只读 Code Reading 角色），
已合入并保留全部 30 个相关文件；当前 13 个角色不等于本轮已实跑 13 个模型任务。
合并后仓库 **93 项**、阅读器 **3 项**通过，原始日志为 merged-tests.log / merged-reader-tests.log。
交接实现哈希未变化，独立 19 例对照仍适用于该实现。CLI push 因无 GitHub 凭据失败，
改用已连接 GitHub API 上传等值 tree；不是绕过权限拒绝，也未新建分支/PR。

发布前刷新 main；若前进，保留并发提交并重验受影响范围。发布后读取远端 SHA 与树确认内容一致。
提交号通过 `git log --diff-filter=A --format=%H -- docs/continuous_optimization/rounds/2026-10-03-r1/round.md` 解析。
回滚只撤销本轮实现/测试/契约变更，保留审计和已有并发改动；不 force/reset 远端。

主要剩余缺口：提交者省略任务、任意填写 input_version 仍无法被本地校验器发现；
跳过理由和证据语义仍须主 AI 核查。下轮优先 CO-002 与一个跨角色输入变更/恢复任务，
轮换覆盖科研调度/写作或旅行修订；CO-003 需要受控模型评测条件。
本轮有经验证的小型改进，无改进计数归零；完整角色覆盖周期未完成，继续任务，不宣称收敛。
