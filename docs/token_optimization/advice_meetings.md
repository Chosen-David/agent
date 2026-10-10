# advice 会议：先检查变更，再加载必要证据

实现入口为 `scripts/advice_poll.py`。它递归扫描当前 PROJECT_ROOT 的 `agent_doc/advice/`，包括 archive，输出新增、修改、删除和可唯一配对的内容迁移；不输出正文或全量库存，不把归档/文件名/自报通过解释成已结案。缺失基线按首次观察枚举全部文件；基线须绑定项目根与实际 SHA256。不可读目录、链接、跨项目基线、文件/字节/目录数超限或观察到并发变化直接报错，不静默漏项。两次扫描不是原子事务，也不构成实时延迟上限；交接/消费前仍核对实际来源。

```powershell
python scripts/advice_poll.py --root ABSOLUTE_PROJECT_ROOT --snapshot-out .agent-runs/advice-poll/run-001/inventory.json
python scripts/advice_poll.py --root ABSOLUTE_PROJECT_ROOT --baseline .agent-runs/advice-poll/run-001/inventory.json --baseline-sha256 HOST_RECORDED_SHA256 --snapshot-out .agent-runs/advice-poll/run-002/inventory.json
```

每次输出的 `snapshot_ref` 是本次观察，尚不是“所有意见已处理”的确认。宿主核对并处理事件后才显式选择下一次的基线；CLI 不推进确认、不覆盖文件、不写 advice 原文。读取事件对应正文前再次核对它的 path/SHA，随后按任务需要加载完整前提、异议和原证据。上下文重置时从任务详情/当前决策与未决问题恢复；磁盘库存不能证明模型仍记得正文。

`changed=false` 只表示两次有界观察中的 advice 字节与路径一致。它不能跳过到期任务、未决阻断、新用户指令、指南/代码/配置/证据变化或必要复审。独立宿主先检查这些事件，确实没有待办时才可结束 advice 检查，避免让模型每小时重读旧会议。此次没有安装轮询器或改变正在运行的宿主。

`content_relocated` 仅表示一个消失路径和一个新增路径具有相同字节 SHA；不证明是同一作者/运行、Git rename 或已经关闭。重复内容出现多义匹配时保留全部新增/删除事件。库存是导航数据，全局 advice 评估与项目文档验收规则保持原状。

## 会议的最小交接

每个独立议题用稳定 issue ID，并绑定代码/输入版本。作者保留原始报告，主 AI 在当前任务详情维护当前决定、未决反例、影响边界、负责人和下一次检查点。回复给出 `adopt/adapt/reject/defer + 理由 + 与上一版的差异 + 证据引用 + 下一动作`；不再逐段复述对方报告。不同意见和更正不能因摘要被省略。

派发给实现者的是已授权方案和验收契约；审计者读取实际 diff、相关调用链、失败触发条件及验收结果。只有这些依赖变化或存在明确未决检查时才再次审查。多名审计者按不同问题/依赖划分范围，避免独立复审退化成复制同一套检查。全部消费者仍核对当前证据，不能信任作者或多数赞同票。

修复前列出不变量和最小反例矩阵，尤其覆盖生成中断、并发交错、内容不同混代、同字节但不同运行/配置、未知 schema 和测试 oracle 被破坏。它们是从 SGLang 会议发现的检查线索，是否适用于某项目仍须核对；不能把该项目的报告当作新项目实测。

## 本次 SGLang 提交阅读

只读目标 `Chosen-David/sglang` 的 `two-level-indexer`，冻结为 [e771d2d](https://github.com/Chosen-David/sglang/commit/e771d2dd03704bf1cd1e16dd67511757f1a7acab)。查询该路径一页100条，返回77条；详细阅读8个提交的 advice diff、6份当前文件，并追踪下面的连续链。不是所有77份提交的逐项源码/实验复核，没有执行 SGLang 测试、GPU或其报告中的复现。

| 链路 | 源报告 → 主 AI 回应 → 验收补记 | 实际追加量（Git行数） |
| --- | --- | --- |
| 059/060/061 | [48893cd](https://github.com/Chosen-David/sglang/commit/48893cd9dc7836ec450484801569cef790ab1906) → [3088724](https://github.com/Chosen-David/sglang/commit/3088724d10d4f104c41ec3fa3df0ed5b5b469cb3) → [2ec9bb4](https://github.com/Chosen-David/sglang/commit/2ec9bb42cc64234b775292175444ff11e893b576) | 原报告109行；回应18行；补记12行，原报告未删除 |
| 062/063/064/065 | [8984a26](https://github.com/Chosen-David/sglang/commit/8984a263dcc8bf15ca001da69cc9ccaae5279f37) → [309ae53](https://github.com/Chosen-David/sglang/commit/309ae53a822cb0706ccdf274d56bf4e97966e866) → [5b8e0f9](https://github.com/Chosen-David/sglang/commit/5b8e0f9c0fb1ea086d208c744ba6c21bb777b36d) | 原报告133行；回应18行；补记12行，原报告未删除 |
| 066 | [ea872af](https://github.com/Chosen-David/sglang/commit/ea872afbdd82181b23a8365567bdb2f0e6b45813) → e771d2d中的回应 | 新反例：同预测字节、不同运行/配置；不能当作062的重复报告 |

连续复审有实际信息增量：059指出预测/回执缺绑定，062进一步指出 staging 与稍后源目录的交错，066进一步区分内容等价和运行来源。这里只确认报告/回应文本及提交变化，未重新验证这些生产缺陷或主 AI 自报的测试成绩。

S-T009 的 baseline讨论也保留了重要更正：原文把 aavg(0,0) 当无L1单级，随后明确其仍有L1，旧分数不能证明去掉粗筛的效果。压缩时必须保留这项更正，不能只抽取原表和早期主张。

冻结版本有2个直接活跃文件、52个archive文件，分别20,587与636,293字节。agent的 `_inventory` 通过 `os.walk` 递归读取，而 `validate_advice_assessments` 仍要求全局覆盖，因此“移到archive”不会自动免除全局评估。归档提交还新增8个文件、修改1个文件、移动44个文件，不能简单把它视为没有新内容的批量搬家。文件内手写时间与Git时间不完全一致，版本比较使用提交/内容哈希，不靠手写时间认定已处理。

上述字节数、行数和文件数不是模型用量。[本轮结果包](../../agent_doc/results/advice-link-20261010/)已完成不同owner的CPU/来源门禁：15项测试在WSL全部通过，Windows14通过且符号链接1项因权限SKIP，WSL补验该项。没有新增付费模型A/B、token节省百分比或第10次成功计数。后续短对照必须同时检查遗漏异议、陈旧结论、复审质量，以及全部审计/整理/主AI总token。

官方[上下文工程说明](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)支持按需读取原文和保留外部引用；这是设计参考，不能替代本库的质量/总成本验收。
