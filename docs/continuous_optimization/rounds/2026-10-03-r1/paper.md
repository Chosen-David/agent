# R1 论文与机制取舍

2026-10-03 阅读：Shunyu Yao、Noah Shinn、Pedram Razavi、Karthik Narasimhan，
[τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/html/2406.12045v1)，
arXiv:2406.12045v1，2024-06-17。此前仓库来源台账未记录精读；本轮新建去重登记，后续版本不重复计新论文。
主文 §§1–6、附录 A、B.1 的 API 示例及零售规则开头、C.2.3 完整轨迹已读；实际查看 PDF 第 7–8 页图表。
未声称读完其他附录。版本及 PDF 哈希见 `../../papers.json`。

## 论文报告（限定原版本）

- 问题：工具调用正确之外，Agent 能否持续完成多轮用户请求并遵守领域规则？§3 使用模拟用户、确定性数据库 API 和隐藏目标终态；奖励结合终态与必要答复，明确承认无法充分检查过程权限。
- §3 的 pass^k 要求 k 次全部成功，区别于至少一次成功的 pass@k；估计量为任务平均 C(c,k)/C(n,k)，需 n≥k。
- §§4–5：零售 115、航空 50 任务；每次最多 30 个动作，主结果每题至少 3 次，Agent/user 温度 0/1。Table 2 的 GPT-4o FC 为 61.2/35.2%，领域等权均值 48.2%；Fig.4 的零售 pass^8 低于 25%。这是历史配置，不代表当前模型。
- §5.1 的 FC/ReAct/Act 对比与 §5.2 的去策略消融表明该设置下工具格式和领域规则有影响；不证明本仓库需要更长 Prompt。Table 3 的航空基线 33.2 与 Table 2 的 35.2 不同，不擅自混合。
- §5.2、C.2.3 展示复合请求遗漏；§6 承认模拟用户能力、标注歧义、用特定模型调任务的偏差。§5.1 报告每任务 Agent/user 费用 $0.38/$0.23，且输入占 Agent 费用 95.9%；其中总费用口径不够清楚，不用它估算本仓库预算。

## 实际源码与现有 Skill 对照（本轮观察）

读取官方 [Env.calculate_reward](https://github.com/sierra-research/tau-bench/blob/59a200c6d575d595120f1cb70fea53cef0632f6b/tau_bench/envs/base.py)：
先保存实际数据哈希，重置并执行目标动作，再比较目标哈希；另检索答复中的必要输出。
该 commit 的 [README](https://github.com/sierra-research/tau-bench/blob/59a200c6d575d595120f1cb70fea53cef0632f6b/README.md)
已警告旧任务不再更新，故本轮仅学习机制，不安装旧 benchmark 或引用其榜单代表最新水平。
源码 SHA-256：`1ad0402073f0ac9ca6b527efa0706e2aa8836dd2e5c1d453ed414ecb768c6d21`。

复读已锁定的 [Superpowers completion Skill](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/verification-before-completion/SKILL.md)，
检查其命令→退出码→证据的验收步骤；该 Skill 本身没有需要运行的依赖脚本。
本仓库已借鉴过该原则，所以不再添加同义 Prompt。实际读取本地 research-assistant 的 SKILL.md、execution.md、
通用调度、handoff 文档及 CLI 后发现：规范已有证据要求，可执行工具却仍放过未完成任务和非法 task evidence。
这正是本轮小型修复的依据；没有引入外部 runtime。

## 本仓库推断、实验和决定

| 候选 | 映射 | 最小实验与代价 | 决定 |
| --- | --- | --- | --- |
| CO-001：核对交接实际终态 | validate_handoff.py、handoff_validation.md、test_handoff.py | 少量 stdlib 代码；旧新版同一输入检查误放行及有效记录非退化 | 采用，19 例独立保留检查由 6 到 19 符合预期；仅程序完整性 |
| CO-002：消费者持有请求/输入版本 | handoff CLI 与评测准备脚本 | 固定产物后变更输入或遗漏任务；测试是否拒绝陈旧交接，先明确接口 | 待测；现有 task 清单来自提交者，遗漏项无法自行发现 |
| CO-003：重复任务可靠性 | evals 任务与执行记录 | 同模型/工具/预算的新角色任务重复运行；记录所有失败 | 待测；本轮确定性程序对照不能冒充模型 pass^k |

不迁移：用字符串命中判断科研结论、用终态替代授权审查、照搬客服成功率、单轮通过等于可靠。
论文未验证我们的具体修复；本仓库效果仅由本轮代码和测试支持。独立审阅还提示大文件哈希/长 DAG 成本，列为 CO-004 待测。
