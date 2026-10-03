# 合成只读阅读输出

输入 `evals/fixtures/synthetic_selector.py`，SHA256 `6fc687e85d2c169c5dc88d7dc126b970036f22b822c00c9f8f0d8b628a6e8ea1`。这是本轮作者按skill作的静态阅读示例，非独立模型盲测；未运行目标。该fixture无外部数据或用户论文材料。

- `run` L28–30 先调用 `select` 再传原query/keys和选中positions到 `full_score`，不是低维表示传到最终评分。
- `represent` L6–9 默认只取0、2维；可选basis作为固定输入用于线性变换，没有训练或query条件更新。
- `select` L16–25：near_len默认4决定边界；forced_len默认1单独决定强制尾位置。预算3，far_budget默认1；skip_far只清空far名单，scores仍计算，near仍排序，final full_score仍调用。
- `full_score` L12–13 对选中原始完整向量做zip点积。长度一致是未强制前提（zip截短），不是已验证输入契约。
- 模块“near=forced/window”“skip=no scoring”“query-trained”“final reduced keys”四项叙述均与上述函数体冲突。

数据边：原向量→represent→候选分数→positions；原向量+positions→full_score。控制边：run→select→represent，run→full_score，select按skip_far分支构建far。未给调用参数，实际运行配置未知；小预算、forced_len>near_len等边界需要额外约束/测试，不能泛化为所有参数正确。
