# 2026-10-06：防止漏任务仍宣告完成

本轮是用户“继续升级”触发的有界工程跟进，基线 `e0796943453e690623f1657730537ba49731a38e`，对应 TASK T12–T14。开始前已 pull；宿主无其他活跃 Agent，state.active_run 为空。改动验收完成，发布状态以根 TASK T14 的远端读回及 Git 可达性为准。

## 真实缺陷与决定

上一轮队列 CO-002 尚有未完成部分：校验器已经验证独立输入版本，却只检查生产者列出的任务。消费者要求 A+B 时，生产者只报 A，文件存在、哈希正确、input_version 相同，就能通过 require-complete。把 B 声称为 skipped 也只需一个理由。

这是完成验收边界遗漏。选择 EXECUTE：保持同一工具/目标，补齐可信接收方契约；不引入新的 Agent 框架、云服务或模型。复用已读研究中的任务完成与交接证据原则；本轮没有新增论文，不把这次跟进包装成又一轮10篇论文调研。

## 已实现

`scripts/validate_handoff.py` 新增消费者 `consumer_request` / CLI `--request`，包含版本和明确任务清单。完成验收必须提供；只传旧版 expected_input_version 不再够用。消费者决定哪些任务可以跳过，生产者不能用自己的字段、理由或内嵌 request 授权。

- 必做任务遗漏、整个列表省略、范围外任务、未授权跳过被拒绝。
- 可跳过任务也必须列出真实理由；skipped 不满足后续 done 的依赖。
- 正常完成、消费者明确允许的跳过、显式零任务的简单回答和诚实 partial 都有正例。
- 部分交接仍列完整派发范围，用 blocked/todo 等标未完成；scope verified 不等于 completion verified。
- 消费者 ID 唯一、布尔权限、精确版本/ID 比较；CLI 拒绝重复 JSON 键和畸形请求。
- 请求模板与迁移说明在 [交接文档](../../../handoff_validation.md)；旧的无完成声明完整性检查保持可用。

重要兼容变化：已有 `--require-complete --expected-input-version X` 调用会返回未验证。接收方须先从可信 TASK/派发记录建立 request，再调用 `--require-complete --request PATH`。不得直接把生产者 tasks 复制成 request 来凑通过。

## 验证与数据意义

[summary.json](evidence/summary.json) 汇总实际结果。全仓352项测试：344通过、8跳过；reader3/3；新增12项 scope 测试，含真实CLI、负例和正常控制。同步检查及 diff 检查通过。跳过项为7项历史绘图依赖/字体组合、1项真实tmux socket集成，未算成功。

[baseline.json](evidence/baseline.json) 与 [candidate.json](evidence/candidate.json) 使用完全相同的16个合成案例、同一文件字节和预期判断；旧版8/16，新版16/16。旧API没有 request 参数，比较脚本向两者传入相同可信版本，仅新版接收新契约。新实现拒绝旧实现的8个误放行情境，正常控制保持可用，原始文件未改动。

这是结构验收的确定性比较，案例在开发过程中构造，**不是盲式保留集，也不是模型准确率/科研成功率实验**。没有重新执行14角色模型任务，上一轮真实角色证据原样保留，不能移作本轮实测。

```bash
# 在临时目录导出基线，避免覆盖历史证据；输出路径自行选新的位置。
git show e079694:scripts/validate_handoff.py > /tmp/handoff-before.py
python docs/continuous_optimization/rounds/2026-10-06-handoff-scope/evidence/compare.py --validator /tmp/handoff-before.py --out /tmp/handoff-before-results.json
python docs/continuous_optimization/rounds/2026-10-06-handoff-scope/evidence/compare.py --validator scripts/validate_handoff.py --out /tmp/handoff-after-results.json
```

## 边界与下一步

工具不能证明消费者文件的来源、任务语义、数据真实性或视觉质量；宿主必须保管可信 request 并独立读产物。它只绑定版本、任务成员与跳过权限，不绑定消费者预定的所有依赖边或语义验收条件。仍是显式CLI/API，没有声称已自动挂入所有模型宿主。

本轮未配置新计时器、部署目标服务器或启动未经验证的tmux监督会话；沿用现有持续任务。下一步继续队列中的纠错记忆保留测试、同预算图表配对盲评和文件回滚可靠性测试。未测效果不记为改进，不增加“连续无改进”计数，也不宣称收敛。
