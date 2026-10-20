# SYSTEM-99 独立链路审查

结论：优先收敛“安装入口的项目归属”“实际维护结果进入共享检索”“portable core 的终态证据新鲜度”三个交接边界，再评估局部性能。确认项不包含已知 TASK 格式/详情问题、RESULT-TIME-97，也没有将缺模型后端归为实现缺陷。

## 范围与证据等级

- 基线：`dcc10b10537a3b410a25f6ef3f2c842a3c1777b4`。审查期间主控有并发变更，本审查不修改或回退它们。
- 读取 AGENTS、决策协议、项目文档/结果复用/监督/记忆/通信契约及实际入口、核心、包装器、验收和相关测试。当前人类 GUIDE.md 为零字节；未写 guide。
- 实际执行仅本地只读检索、固定 CPU 测试和一次性测试 fixture；fixture 仅写自有临时项目并清理。没有启动真实后台监督、外部模型、GPU、未知任务或外部写入。唯一持久新增为本文。
- “复现”指本机代码/固定合成输入，不是生产实例实测。代码定位说明机制；没有把静态推断写成现场事故。

## 已确认缺口

| ID / 严重度 | 真实交接边界 | 确认证据与影响 | 最小验收 |
| --- | --- | --- | --- |
| CHAIN-ENTRY / P1 | README 完整 Claude 安装 → 项目 CLAUDE 入口 → 项目文档 | `setup.py:56–57` 仍生成“Project A 的指南、任务、建议和结果全部属于 Project A/doc”，同块随后又要求 `agent_doc/*`。安装器实际只初始化 `agent_doc/`。全新临时项目实际 install 与 check 都返回 configured，同时上述矛盾仍在；这是检查与入口共同认可错误说明，不是推测模型必然写错目录。 | 从全新临时项目运行实际安装/检查，断言生成主入口对 guide/task/advice/results 只有统一 canonical 归属，普通 `doc/` 保留；再用真实宿主新会话检查其解析，后者未在本机执行。不能仅测试模板等于自身。 |
| CHAIN-RESULT-CATALOG / P1（运行流程交接，不是搜索器实现错误） | 本库已完成维护任务 → 原始结果/独立报告 → ResultStore 检索 | `result-fd95`、`validation-fd87`、`check-helper85`、`context-schema83`、`artifact-fd77`、`artifact-read76`、`prompt-scan69`、`prompt-read67` 实有正式报告/测试证据，但无 `record.json`。实际全目录有界检索 `RESULT-FD-95` 扫描 251、partial=false、81 个读取错误、无候选、status=incomplete；其中明确含上述缺 record 错误。`result_store.py:350–394` 只从成功 show 的登记记录产生候选，因此这些目录不能通过统一接口成为可复用候选。不能把“有 Markdown、旧通过标签、已完成 TASK”当已接通历史结果复用。 | 先为一个有代表性的已完成批次建立只引用旧字节/实际哈希的登记并独立核对，验证正式查询可返回其候选；仍须当前独立验收才能 reuse。随后量化应登记的批次覆盖率、豁免理由和缺件，而不是把 81 个错误一律当损坏或自动给旧数据授信。 |
| CHAIN-TERMINAL / P2 | portable `Engine.tick` / CLI tick → 终态读取 → 完成声明 | `core.py:403–404` 在 done/cancelled 快返，跳过下方 `_check_done`。用现有 RuntimeContracts/SyntheticHandler 固定 fixture：首 tick done；将同一 handler 的当前 verify 改为 false；下一不同事件 tick 仍 done，节点仍 done，run 次数 1。即已完成 portable 链的后续可信 tick 不重验其证据，不能被解释为“当前仍验收通过”。 | 单节点与多节点完全完成后使已绑定证据/记忆失效，验证后续公开 tick/状态明确区分历史完成与当前有效，且不盲重放副作用、不解除取消。当前测试只覆盖还有未完成后继时的证据失效，需补完全终态用例。 |

CHAIN-TERMINAL 的重要边界：`task_supervisor.worker` 在完成前/重启后的 done 分支另行调用 `engine._check_done`，`ReportingHandler.verify` 和 `review` 也会复核声明的记忆/结果。故本项**不能外推为受管 worker 一定写出错误 final-report**，也不能把原始 Store 状态当作它宣称的独立报告。缺口在公开 portable 执行语义与“每次 tick 核对完成证据”契约之间；若终态有意冻结，至少需要明确且可执行的当前有效性查询边界。

### 实际探针输出

```json
{"probe":"fresh-install-entry","status":"configured","check_status":"configured","legacy_doc_instruction":true,"canonical_index_exists":true,"legacy_doc_created":false}
{"probe":"terminal-engine-evidence","first":"done","independent_verify_now":false,"next_tick":"done","node":"done","handler_runs":1}
```

探针复用 `tests/test_setup.py` 的 `SetupTests.setUp`/`setup.install`，以及 `tests/test_task_runtime.py` 的 `RuntimeContracts.setUp`、`plan`、`SyntheticHandler` 与 `engine`；每个 fixture 均调用 `doCleanups()`。没有改实现、测试文件或现有项目数据。

检索先于上述测试：第一次查询 `supervisor communication memory recovery installation`，limit=6/max_scan=200，实际 scanned=199、partial=true，返回的是词法候选，不支持当前链路复用。后续为定位实际登记覆盖查询 `RESULT-FD-95`，limit=20/max_scan=5000，得到上表的完整有界扫描；这里的零候选并不证明所有相关自然语言记录都不存在，缺 record 则由逐目录事实确认。没有授信或重新登记旧结果。

## 待验证假设：不要先改门禁

### H1 / P1 候选：同一个已审核多生产者 DAG 可能因自身新增结果反复要求重规划

`task_manifest.prepare` 固定每个节点当时的 `prior_result_search`，`ReportingHandler.run:277–284` 对受保护数据生产者比较**整个搜索响应**。其中含 scanned、errors、候选等字段；生产者 A 正常注册新结果后，尚未派发的生产者 B 即使目标、输入、权限和已有审核依据不变，其查询响应也可能只因 scanned 或无关缺件目录变化而不等。此处会 blocked，而不是错授信；不能把这种保守拦截描述为安全绕过。

最小判别：一个固定 CPU fixture、两个事先审核且依赖关系明确的数据生产者与各自独立 gate；A 完成并登记，B 再真实派发。分别测试新增相关候选、无关候选和仅扫描计数变化，保留审核/搜索/状态日志。确认哪些变化必须重新审核，哪些属于计划已声明的因果产物；不能以直接关闭 prior-result 检查或 legacy 降级作为修复。现有独立审核测试覆盖搜索变为 unavailable 的拒绝，但本审查未跑通这个完整双生产者情境，因此只列假设。

### H2 / P1 验收缺口：通信 ACK/impact 与已完成任务的恢复闭环尚无本轮真实宿主证据

实际实现清楚区分边界：`Mailbox.consume_handoff` 验范围/依据并持久化绑定；ACK 不代表任务 done；`impact` 只返回受影响消费者；更正事件与重新编排由主 AI/宿主执行。`check_task_memory` 只保证显式 memory_refs，未声明依赖不会被自动发现。这些是公开设计边界，不是“缺一个自动调用所以有 bug”。

最小判别：固定一个生产者、消费者、独立验收者和无关支线，真实宿主先完成交接，再更正原意图；验证 impact 精确列出已消费 claim/recipient，旧报告不可再用于最终交付、无关原始测量不受损，恢复创建新身份/产物/事件并由原消费者复验；重启与取消分别验证。不仅检查 Mailbox 与 MemoryLedger 各自单测。本文未取得这种实际宿主链路的新回执。

## 本轮检查与资源缺口

实际复跑：`test_setup.py` 10 项通过，`test_project_memory.py` 15 项通过，`test_task_runtime.py` 30 项通过；合计 55 项，无本轮跳过。这里的通过未覆盖上表终态新情境或语义矛盾，恰好说明单模块绿灯不能替代真实交接验收。本轮没有重跑全库，也没有将历史 1300+ 项统计写成本轮结果。

本机 `shutil.which('tmux'/'claude'/'codex')` 均为 null；零模型调用。这不足以证明用户实际服务器也缺资源，但意味着本环境不能验证 Claude 新会话加载、真正独立模型身份/授权、tmux/SSH 生存性、模型异步 submit/poll 和外部作业停止。未安装工具、未探测凭据、未创建服务；这些属于资源/部署待验项，不是已确认代码缺陷。

建议下一系统批次以一个可审计的固定小链收敛：同一安装入口和项目根，实际计划审核，两个已知 CPU 生产者各自独立结果 gate，一次按消费者 scope 的通信，一次意图更正，以及取消/恢复负控。先修统一项目归属和结果登记交接，再用这条链决定需要哪些核心变更；没有真实宿主时先跑明确标注的 CPU adapter 集成契约，不声称多模型生产验收。
