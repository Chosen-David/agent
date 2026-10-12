# 唯一单行变化：跳过不可能胜出的 multi-edit 匹配

基线 `71496c7b1f42b94616343683c7671b6a0e6e8a3b`，2026-10-12。实际入口为 `scripts/artifact_context.py` → `compare_artifacts`。

失败先行：第一版尝试裁掉共同首尾后再运行 matcher，生产测量看似无退化，但独立 6,032 次检查找到 16 次 wire 增大。该结果完整保留在 `artifact-localized-20261012/`，没有提交或用其宣称完成。

修复方案不再改变 `SequenceMatcher` 的输入或对齐。普通字节选择下，若线性 splice 恰好只插入/删除各至多一行，且变化行在另一全文完全不存在，则 matcher 无法把它复用成 equal；单 edit 含相同插入内容和坐标，却比现有 splice 多一层 schema 开销，因此不可能胜出，可以跳过。只要变化可能复用、超过一行、使用 token counter，或其他任一条件不满足，就保留原 matcher 与候选集合。双方文件读取、SHA、预算、完整 base、恢复和 stale 拒绝不变。

生产重测固定 seed `190823`：16 组边界案例与 3,000 组随机案例，在普通字节选择和 packet 字节 counter 两种模式共 6,032 次完整入口对照，候选 packet 与冻结基线逐字节一致，恢复全部通过。2,048 行重复文本中间唯一单行变化的 7 对交替计时中位数 `612.883613 ms → 1.603235 ms`，降低 `99.7384%`。计时包含读取、SHA、候选选择和序列化；输入、源码哈希、环境和全部样本见 `measurement.json`。

独立验收结论为 **usable-with-scope**：另行从冻结基线重跑 3,016 个案例、普通/计数两模式共 6,032 次完整入口检查，最终 packet 逐字节一致且独立 applicator 全部恢复目标 SHA；旧失败版反例、门禁真/假分支和全部引用哈希均复核通过。独立 7 对计时中位数 `632.832658 ms → 1.809249 ms`，降低 `99.7141%`。23 项 artifact 定向回归通过。全库 1,174 项中 1,164 通过、8 跳过、2 失败；两项是冻结基线已有的 knowledge/plugin 生成副本不同步，相关路径未被本任务改动，因此不归因本候选，也不宣称全库绿。独立记录见 `independent-review.json` 与 `independent_review.md`。

收益范围仅为已测合成唯一单行变化的 CPU 字节选择入口；token counter 明确保留原 matcher，本轮不声称 token、模型质量、账单、GPU、网络或整个 Agent 请求加速。
