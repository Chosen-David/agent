# [ART-LOCAL-01] 局部文本差分只匹配真实变化区

Task-ID: ART-LOCAL-01
Date: 2026-10-12 Asia/Shanghai

## Plan

授权：持续优化 Agent，验收后普通推送 main。范围仅为现有 `scripts/artifact_context.py` → `compare_artifacts` → `_edits` CPU 路径，不启动模型、GPU、受管服务器或付费任务，不新增平行生产实现。

基线：`71496c7b1f42b94616343683c7671b6a0e6e8a3b`。先查结果 registry；既有 `ART-EQUAL-01` 只优化完整相同文本，本任务处理“首尾大段相同、局部发生变化”的不同输入，不复用其收益数字。机制依据为 `SequenceMatcher(autojunk=False)` 的潜在二次工作量；最终方案仅在普通字节选择中跳过无法胜过已有单 splice 的唯一单行变化，token counter 模式仍保留完整 codec 集合。

固定验收：至少 1,000 组随机/构造输入完整恢复正确；候选最终 JSON 不得比基线更大；现有 artifact 回归通过；2,048 行重复文本中间单行变化的完整入口，7 对交替计时中位耗时至少降低 50%。计时覆盖文件读取、SHA 校验、候选选择和序列化；记录 Python/OS、输入哈希、全部样本。CPU 预算 90 秒，模型调用 0。

DAG：prior-search → patch/tests → paired CPU producer → independent code/result verifier → report/publication。测量只支持该合成局部编辑入口的 CPU 收益；不外推模型质量、token、账单、整体 Agent 请求或其他工作负载。失败首版目录为 `agent_doc/results/artifact-localized-20261012`，修复重测目录为 `agent_doc/results/artifact-unique-splice-20261012`。

## Progress

- 第一版“裁掉共同首尾再匹配”在生产 4,016 次检查中未见退化，但独立 6,032 次检查发现 16 次 wire 增大；重复行的非唯一对齐会产生另一份更长 patch。该版本验收失败，证据保留且没有提交或消费性能结论。
- 第二版撤回 matcher 语义改写，仅对可证明单 splice 已支配单 edit、且没有 token counter 的唯一变化行跳过 matcher。生产 6,032 次完整入口对照与独立 6,032 次对照均为 packet 逐字节一致、精确恢复；23 项 artifact 定向回归通过。
- 独立验收为 `usable-with-scope`：独立 7 对完整入口计时 `632.832658 ms → 1.809249 ms`（降低 99.7141%），生产冻结样本 `612.883613 ms → 1.603235 ms`（降低 99.7384%）。仅支持指定 CPU byte-selection 合成输入，不支持 token counter、模型、费用、GPU 或端到端收益。
- 全库 1,174 项中 2 项失败、8 项跳过；失败是基线已有 knowledge/plugin 生成引用不同步，相关路径未由本任务修改，不归因候选，且不声称全库绿。
