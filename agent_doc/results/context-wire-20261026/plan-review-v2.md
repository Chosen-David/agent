# CONTEXT-WIRE-01 v2 独立方案复核

Verdict: **approve**，限当前 v2 方案与冻结 fixture；无剩余方案阻塞项。这是执行前方案结论，不是修复正确性、回归通过或发布验收。

根 `/workspace/scratch/6416f20dc59b/agent-run-1303`；基线 `80c4a368dc3453304f9c5398cafec2cfc9a3b5ed`。已读取 v2 方案、完整新 fixture、Version36 阶段V及相关继承范围，核对 v1 方案/审核原件未变，proposed-fixture-v1.py 与上次 fixture 哈希相同，runner 不变。未运行测试或论文示例，未派发任务；本次唯一写入本文件。继续使用前次审核中绑定的 AGENTS/工作流/生产源码边界；生产改动尚未验收。

## 返修核对

- token_counter：新增受控工厂 direct-main 回归，令 full 紧凑 JSON 恰占 cap、终止换行后不适配，而 splice 可适配；核对实际输出总字符与可恢复两版原文。cap=1 同时固定所有候选不适配的 exit2/stderr/空stdout。该测试与子进程真实 wire 精确边界测试互补，未引入真实 tokenizer/模型成本。
- 内容与只读：source 原文/行位/ref、artifact 双版本恢复、advice leading_text/选段/heading位置、grid 全坐标/metadata恢复、dispatch 完整父 params/config/reasoning/approval/sandbox/thread IDs、input documents/dependencies 均有明确 oracle。精确边界及旧数据拒绝路径新增字节快照；Unicode 成功路径保留快照。没有用同一个内部长度公式取代真实子进程 stdout oracle。
- helper：新增默认1M拒绝、显式16MiB上限允许及非法 ceiling（bool、空值、负值、超硬上限）拒绝；大 artifact 子进程成功样例仍保留。应复用 render_cli_context，不复制 serializer；默认1M及其他消费者边界不放宽。
- artifact API 两处 comparison-budget 异常改为 ContextBudgetError（ValueError 子类）已明确列入 v2 生产范围。允许有类型的精确 CLI 错误分类；既有 API ValueError 捕获兼容、原预算/codec/counter选择语义及错误文字仍须保留，由最终 diff 和原相关回归复核。
- dispatch direct-main Popen fail-if-called 与输入字节快照有可观察负控边界；v2 明确有限 mock 不证明未知宿主全部 API 零调用。最终生产脚本/API 无 RPC/backend 调用路径仍须静态复查。

## 七域结论

| 域 | 结论 | 理由 |
| --- | --- | --- |
| intent | pass | 仅五 CLI 的完整 UTF8 实际 wire 边界，保留完整原文/父设置/拒绝协议；不外推收益。 |
| guide | pass | 继承原审核所读空 GUIDE 与人类目录只读约束；SYSTEM-99 Version36 保持同批及未决事项。 |
| assumptions | pass | CLI 与 API 预算分层及 artifact token候选预留原生终止换行明确；API 选择语义保留。 |
| prior_results | pass | v1 发现全部保留并逐项补强；旧结果、失败、PID/ALIAS/role/Codex 受阻预算及原有门禁不替换、不重置。 |
| acceptance | pass | 新 fixture 与现有15模块固定 suite 足以对当前局部假设作有限回归，精确 stdout cap/cap-1、cp936、完整JSON及原文恢复具有可审核判据。 |
| risk | pass | 共享 helper 可选 ceiling 有16MiB硬界，原生错误协议与新预算协议分离；无生产 backend 授权扩大；最终实现仍待审。 |
| resources | pass | 当前执行额度仍0；主控最多3次 targeted（每次120s）、独审后续一次同冻结suite（120s），外层subprocess.run(timeout=120)，超时保留且不自动重试。无 fullsuite/Windows/模型实验。 |

下一步仅按已批准 v2 作固定原源码基线，再在范围内修复并冻结源码/fixture/runner、实际命令/环境和原始失败/成功日志。后续独立结果验收仍待主控明确请求；批准不取消任何既有用户合同或发布门禁，不把本地回归转换成经验收益证据。

## 本次绑定 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `agent_doc/results/context-wire-20261026/plan-v2.md` | `40a58ac6bbc56e64d2b342e6aecb71cd962f4c02816917972fc3fec5fcf3e670` |
| `tests/test_context_cli_wire.py` | `423baacb7177c642bf0a69af3adb0452f77c00578abfe870b291ab7266b1ea0c` |
| `agent_doc/results/context-wire-20261026/run_checks.py` | `80565f43d01e48cd6304ec5eb11323243fe06dc9dd421aaca5f0ba57f80d9c53` |
| `agent_doc/results/context-wire-20261026/plan.md` | `048a6b1794e0dd0f07cc0359bc232bb2eafe72be19d03336c1161f04d50db3fe` |
| `agent_doc/results/context-wire-20261026/plan-review.md` | `495bd1cfe8c9a21340d9250d0c9137c4b6172b5fb81b3a7a59522bda0f8c489c` |
| `agent_doc/results/context-wire-20261026/proposed-fixture-v1.py` | `6ff0cb65b98a081cdc8b3c820e5651d2d78829fa7f919f3f99608daa1b77205b` |
| `agent_doc/task/task_details/SYSTEM-99.md` | `e0743a1364162eeb8118ea96520890d7b3e21e25ee61c3c5c01be2776b7754ca` |
