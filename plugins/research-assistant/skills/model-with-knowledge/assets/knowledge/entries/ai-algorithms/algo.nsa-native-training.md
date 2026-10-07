# NSA：原生稀疏训练不等于无损替换

## 问题触发

native sparse attention；块稀疏训练；NSA GQA MoE；long context selection

## 精确结论与证据身份

ACL 2025 的 NSA 在共同训练设置下保持多数任务质量，并有明确退化项；它是训练架构变化，不能直接套到未训练的密集模型。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- model: 27B total / 3B active MoE with GQA
- training: 270B tokens at 8k then 32k continuation
- method: compression selection sliding-window branches

## Observation / 实验 / 源码定位

- §3.1 指定压缩块 32、步长 16、选择块 64、16 块、窗口 512。
- Table 1：MBPP 从 full 0.482 到 NSA 0.466，MMLU 0.567 到 0.565；平均收益不掩盖退化。

## 可算例子与任务映射

16×64=1024 个选择 token，另有压缩和 512 窗口路径，不能只按 1024/长度宣称总计算削减比例。

## 失败情形与不可推广范围

- 稀疏 FLOPs 减少不必然转为硬件速度；必须计入选择和布局开销。
- 原生训练结果不证明替换任意 checkpoint 无损，64k kernel 图不是全模型吞吐。

## 最小迁移验证

- 核对训练架构授权和质量约束；若仅要求等价 kernel 则不采用。
- 只做目标块布局/选择开销的最小 profile，再决定研究规模。

## 来源定位与尚未验证项

- [§3.1 Tables 1–2; §4 efficiency; Appendix C–D](https://aclanthology.org/2025.acl-long.1126.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
