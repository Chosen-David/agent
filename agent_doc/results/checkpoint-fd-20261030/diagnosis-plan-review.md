# CHECKPOINT-FD-DIAG-01 独立静态方案审核

Decision: **approve**，仅批准下述冻结输入的一次限域诊断。无阻断问题，无需修改 runner。此审核未执行 runner、测试、模型、tmux 或旧门禁；不是受信 ReviewSession、运行时派发回执或部署证明。

时间：2026-10-29 18:04 UTC。项目根：`/workspace/scratch/95d615402a52/agent-run-1202`。HEAD 实读为 `d243266e9b9707ea6aac666e21a3ba8edb8e3a34`。

冻结并核实：

| 输入 | SHA256 |
| --- | --- |
| `.agent-runs/checkpoint-fd-diag-0200/plan.json` | `ae0e44cf6813231bb4517c4bdfc1938614d92b5d5fc1afbe460e0ad1c40bf71e` |
| `.agent-runs/checkpoint-fd-diag-0200/diagnosis.py` | `027fb51e791230eb9379211f44bb3623e9594192b073649c22bd77062b038092` |
| `agent_runtime/task_manifest.py` | `69c4fe53bf09b101bdffda7e5a3d9a8b3a71ba40ddc25174402c2b7260979425` |

plan 中 AGENTS、TASK 索引、GUIDE、guide README、目标源码、两个历史报告及 knowledge-search 的全部 source_refs 均与实际 sha256sum 一致。方案和 runner 仅冻结为本报告的内容哈希，没有改写其文件或权限。

## intent

符合当前 SYSTEM-99 Version56 之未完成系统批次及当前交接：仅确认 generic `task_manifest.atomic_json` 在已获 mkstemp 原始 FD、但 fdopen 尚未成功构造时的所有权行为。源码43–57行当前为默认 closefd=True 的 `with os.fdopen(...)`，构造调用早于进入 with，finally 仅 unlink 临时名。这为诊断提供明确可检验问题，不预先把源码推断当测量结论。本阶段不实施修复，不扩展原生续接方案或旧耗尽额度。

## guide

已读 AGENTS、project_document_workflow、当前唯一 TASK 索引、SYSTEM-99 目标/Version56/近期 Progress 与 guide 两文件。GUIDE 是空字节文件，不能虚构其内容或人类授权；README 解释人类专用边界，且注明其自身为一次性授权 AI 创建，不升级为人类目标。审核只写本角色 `.agent-runs/checkpoint-fd-diag-review-0200/`，不写 TASK、guide、生产源码、producer 文件。SYSTEM-99 的真实宿主、完整输入、最终质量、总费用与并发恢复等未决保持 open；42 篇正文为方案现有计数，本审核不增计。

## assumptions

本地单进程、无并发 FD 关闭/复用干扰。故障注入在 fdopen 调用入口抛同一 OSError，因此并未模拟成功构造后 close 的路径，也不说明真实 OS/Python 在哪些条件、以多高发生率产生同类异常。只结论化为“此注入构造失败路径在当前源码/环境下的原始 FD 状态”。默认 closefd=True 在成功构造后的所有权语义不能反推构造前已交接成功。

runner 使用真实 mkstemp，patch 只记录实际 fd/临时名；`closed` 直接用 os.fstat 并只将 EBADF 认作关闭，其余错误传播，不依赖目标函数自报或 finally 曾执行的计数。构造异常身份用 assertIs 保证未被无关错误替代。无真实用户路径输入，均为 TemporaryDirectory 内合成检查点。

## prior_results

已核读 result-fd95 与 validation-record-fix 报告并核其哈希。前者涉及 ResultStore 的 `_read/_check_ref/_save`，仅借鉴原始 FD 所有权/清理前观察方法，不复用其9/103方法或任何旧数据为本函数验收；后者原问题是 validation_context 最终空记录与恢复阻断，其暂存发布修复不验证当前 generic atomic_json。本调用不重跑任一历史 runner。方案 prior search 标注340扫描、25 errors，不能解释成无遗漏的全历史覆盖；本审核仅接受已明示候选的适用性排除，未授信旧结果。knowledge-search 为空且 applicability unchecked，不证明不存在适用知识，不影响当前源码直接诊断。

## acceptance

静态核验 runner 为3个 test 方法：Unicode 正常写入；构造失败方法含 existing=False/True 两个子场景；已有文件 NaN 序列化失败控制。不存在文件保留不存在、既有文件原字节保持；正常控制核完整 UTF-8/换行字节与 JSON 内容；NaN 控制核 ValueError、原字节、FD 和临时清理，适当地覆盖“流已构造后序列化失败”这一不同阶段。

关键原始观察在 invoke 中 `is_closed = closed(fd)`，在本方 except/finally 关闭之前，且在 retry 之前。返回布尔之后，失败断言不能被测试自身 cleanup 冒充关闭成功。构造子场景用嵌套 subTest 记录 FD 断言失败后继续撤销故障的 retry，并核最终字节与唯一目标目录成员，因此预期泄漏失败不会自动吞掉恢复观察。两个 existing 子场景均有独立 TemporaryDirectory 和原始 acquired 列表。目标 unlink 与 FD 关闭分开测量，不把临时名消失当 FD 关闭。

批准后的 producer 和独立执行各一次，必须保留完整 stdout/stderr、exit、真实 argv/环境/起止、输入/源码哈希及失败信息。失败是有效诊断数据，不是修复验收通过；故障方法的两个失败子场景不能称两个根因。独立阶段仍须检查真实执行代码、原始数据和上下文，不能只认 runner 总结或 producer 自报。后续同角色复核另行进行，本调用未执行。

## risk

标准执行/断言失败路径：invoke 内异常由 except 清理所有已获取的 FD；返回后的各测试以 finally 清理；TemporaryDirectory 回收其内部名字。原始观察因此不会靠遗留 FD 跨子场景累积。不注入 close/unlink 清理失败；OS 强制终止、敌意替换、并发 FD 复用及所有清理故障不保证。patch target.os.fdopen 影响共享 os 模块，但作用域受限、同步且在调用后恢复；本脚本不启线程/外部作业。

不主张原生 Windows/macOS、性能、真实发生率、完整 E2E、全事务或系统级无缺陷。无新增依赖/付费资源、模型或用户文件写入。无阻断问题。解释性非阻断要求：保留“注入路径”的限定；结果目录记录不能把25检索错误说成完整覆盖；失败仍公开原始失败，不据清理后状态改判。

## resources

本方案 planreview1 已占用1；producer1 与 independent_execution1 尚未使用。每命令30秒，共同截止 `2026-10-29T18:18:36.910942Z`；无重试/重置。此次仅只读静态核查及本报告写入，命令均快速结束，未消耗执行额度。原耗尽/暂停门禁、MemDerive 缺口、原生CI续接额度不变。全角色 tokens/费用 unknown。本手工独立 AI 意见只承担本方案静态审核，不产生可信 runtime 审核认证。
