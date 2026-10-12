# ART-EQUAL-01 独立代码与数据复核

审查者：`/root/artifact_equal_review`，由宿主创建，与实现/测量生产者分离；审查和复跑实际执行，不以生产者的 pass 为结论。状态：**usable-with-scope**。

## 固定范围与方案

基线 `bd65a2348e32d8a70af9e003cbc309064363dd9e`。候选 `agent_runtime/artifact_context.py` SHA-256：`e533244e68e698cb95f298bd04ce5e63727dd2cf485e4f731805883191b3e30f`。审核先于候选测量给出 approve：同接口、同权限范围内，仅在两个文件已读取并 SHA 校验后，跳过相等字符串的 `_edits`。性能验收预设为 2048 重复行完整公开入口 7 对 CPU 测量中位数减少至少 50%。

源码核查：基线 `_edits` 在相等输入时只产生 equal opcode，被过滤为 `[]`，最后返回 `None`；超字符/行边界也返回 `None`。候选增加 `before != after` 不删除任何输出候选。相等判断发生在两个 `_bound` 之后，因此并不通过“引用 hash 相等”跳过当前磁盘读取。`full`、`reuse_identical`、预算、token_counter 和恢复路径保持原流程。对不同文本仍调用 `_edits`，没有把一般 diff 禁用。

## 独立执行

独立脚本 `independent_check.py` 从固定 git 基线加载旧模块，并与当前模块执行同一个真实 `compare_artifacts` 入口；临时文件由两者共用。

- 30 对输入 × 8 个布尔 flag 组合 × 有/无计数器，共 480 组：完整 payload 完全相等、计数器收到的 wire 序列完全相等、恢复结果逐字符相等。
- 覆盖空输入、Unicode/emoji、CRLF、增删、重复行、不同文本，以及 2049 行、65536/65537 字符边界；生产者另有 2048/2049 行覆盖。
- patch 观察确认相等输入跳过 `_edits`，不同输入仍调用一次。
- 相等预期 hash 下修改实际 after 文件，两版都拒绝 stale，并在拒绝前未调用计数器。
- 实际运行 `python -m unittest discover -s tests -p 'test_artifact*.py' -v`：36 项全部通过，含新回归。

独立复测使用不同重复行文本，`reuse_identical=False`，输出为原有 splice/full 选择结果；性能仍计入 SHA 读取、解码、单 splice、候选序列化与最终预算判断。7 对交替顺序，单位 ns 保存在 `independent_raw.json`。基线中位数 **458.304713 ms**，候选 **1.078548 ms**，减少 **99.7647%**，满足预设验收。生产者的 7 对数据在 `reuse_identical=True` 下为 **473.834342 ms → 1.400838 ms**，汇总与原始样本一致。

## 代码、结果与度量边界

生产者 `measure.py` 确实计时完整 compare 入口，固定 baseline 字节、输入 hash 和当前源码 hash；warmup 不计入 7 对样本，交替先后顺序，未截除失败样本或按快慢选择结果。生产者 72 组等价检查有效，但来自 9 对输入/flag 组合，不能称为 72 个独立任务。

全部时长有限且为正，两个中位数由完整样本复算；独立不同文本复测支持相同范围内收益。由于合成重复行是 SequenceMatcher 极端重复输入，这一结果只支持**相等且启用 multi_edit 的指定 CPU artifact 入口**，不支持所有文档分布的平均收益，不支持模型质量、token/账单降低、端到端 Agent 加速或 GPU 收益。不同输入额外字符串比较的潜在成本未做代表分布统计，仅验证语义保持。有限测试不是普遍无 bug 认证。

## 证据

执行：`python agent_doc/results/artifact-equality-20261012/independent_check.py`，以及上述 artifact 测试命令。原始样本/环境：`independent_raw.json`；终端输出：`independent_run.log`；测试输出：`independent_tests.log`。代码或数据字节若后续改变，应重新核对受影响证据，不能沿用本通过结论。
