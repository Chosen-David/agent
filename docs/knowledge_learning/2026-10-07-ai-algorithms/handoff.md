说明：这是初版研究交接的发布整理副本，历史建议不覆盖最终集成状态；原始文件字节保存在历史归档 `research/handoff.md`。

# AI 算法知识研究交接：2026-10-07

## 采用建议

本轮推荐采用两条有限前提的理论/算法知识，沿用真实 schema v1；无需移植未发布 v2、增加 runtime 类型或修改生产推理栈。

1. `ai.speculative-sampling-residual-exactness`：证明接受/拒绝质量如何补成目标分布，列出支撑、过滤后概率、前缀、零残差、greedy、tree、MTP 和目标改变的适用边界。
2. `ai.speculative-decoding-cost-bound`：由条件接受前缀尾和连接产出与成本；把几何近似、理想阈值和真实成本测量分开。强依赖第一条 version 1。

条目中的有限概率例子和推导为本轮原创整理，不宣称发明这些算法或新定理。EAGLE-3 的作者实验只作为近期适用性边界材料，未建成独立经验规律条目；没有本地模型/性能收益声明。

## 文件与初版锁定

- `entries/`：两对 schema-v1 candidate JSON/Markdown。
- `candidate-freeze-1.json`：初版四文件 SHA256 与知识 snapshot；供独立题验收使用，冻结后未因测试题修改。
- `source-lock.json`：真实来源、日期、版本、阅读范围、许可实情、官方代码 commit/blob 及独立来源审查者提供的 PDF 字节锁。
- `verify.py` / `checks.json`：原创有限有理数自检及实际输出。
- `schema-validation.json`：实际 v1 CLI 结构验证结果。

初始研究产物现保存在 `historical-evidence.tar.gz` 的 `research/`；下面 `entries/` 等名称均相对该归档内目录。当前可检索条目在仓库 `knowledge/entries/ai-algorithms/`，状态以 [report.md](report.md) 与 `final-candidate-freeze.json` 为准。
本研究员仅写该根；主仓库只读，未 commit/push，未读取独立冻结题或其答案。

## 已完成检查与修订

2026-10-07 实际执行：13 个命名检查组通过，包含三元概率单纯形分母 6 的 28 个分布、784 对分布的精确质量与 TV 恒等式检查；另含零支撑、p=q、错误 fallback、确定性候选消元、相关事件、验证成本逆转、长草稿负收益及轮均比率错误。

这些是确定性的有限数学例证；784 对不能声称穷尽所有分布，13 组不能声称 13 次真实模型实验。

实际 v1 CLI 接受 2 条候选及强依赖，snapshot 见 freeze。结构通过不等于科学证明。候选 proof 暂为 `not-checked`，由独立数学/来源审查结论支持后再升级为 `derivation-reviewed`；不得用 `formal`。

初审指出的成本算例小数和 Chen 小标题 locator 已在初版冻结前改正：v=4 的速度比准确为 0.764；Chen 采用 Algorithm 2、Modified Rejection Sampling、Theorem 1 定位。曾经的错误与修订在此保留，不把修改前文本称通过。

## 采用、延后与拒绝

- 采用：上面两条定义明确、可复算、无需 GPU 的知识。
- 延后：具体 EAGLE/MTP runtime 的端到端无损认证、目标硬件上的速度测量、动态 horizon 优化。若将来要做，先固定目标模型/精度/采样设置和预算，分别验条件分布与 ΣL/ΣC，出现非零偏差先停性能结论。
- 拒绝：由 greedy 一致推随机无损；由树节点数推产出 token 数；把任意 proposal 置信度代入单链接受公式；由作者固定配置实验推任意部署加速；把 p→p̃ 的近似目标校正当成原 dense 目标无损。

## 集成提醒

首版已发给独立来源/测试 owner，先保留其冻结证据。主维护者可以在独立验收后把候选移入 `knowledge/entries/`，将 checks 路径改为实际提交的 `docs/knowledge_learning/2026-10-07-ai-algorithms/` 证据路径，再改变发布状态并记录发布转换后的哈希。内容或假设若因审查改变，应保留首版和说明，不覆盖首轮验收事实。

只提交原创条目、精简来源锁、原创检查及审查记录；无需提交第三方 PDF/源代码或大段原文。论文与代码许可分别记录，Apache-2.0 不外推到论文、权重或数据集。main 的同步、全部回归、快照同步和远端读回由主维护者负责。

## 研究范围的终止条件

本轮来源闭环已覆盖原始严格采样算法、独立同期论文、近期正式 EAGLE-3 论文与官方实现的相关分支。再做广泛论文扫描不会解决当前两条候选的主要不确定性，因此停在独立验收与小规模集成，未发起新的 runtime 或训练项目。
