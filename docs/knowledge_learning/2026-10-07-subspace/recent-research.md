# 近期原文筛选

检索日期2026-10-07。Huan Qing, [A Subsampled Davis-Kahan Bound for Large-Scale Eigenspace Estimation](https://arxiv.org/abs/2609.09211)，v1，2026-09-06；arXiv页仅列预印本，未核实正式接收。固定[HTML原文](https://arxiv.org/html/2609.09211v1)。初始直开失败，搜索结果引用再次打开成功。实际阅读§2、§3.1–3.2、Appendix A.2–A.4；§5仅浏览文字，不声称完整逐页阅读或复现实验。

作者Theorem3.4在rank-d对称信号、对称噪声E、独立Bernoulli列采样下给出子空间误差界。0<alpha<1分支要求alpha≥max(16 mu d log(p)/p,8(||E||op/delta)^2)，mu=(p/d) max行范数平方，delta为非零谱绝对最小值。它不能仅凭“低秩”使用；右端≥1时该分支不可行。证明路线是采样保秩→最小奇异值下界→矩形扰动→旋转对齐。复杂度主张不等于实际GPU加速。

**本项目审查，非作者结论：** A.4末尾写V=VB OB，却将最终O设为O1 OB^T；沿前式右乘应为O1 OB。脚本用90度旋转检查这一代数不一致。它是局部对齐表达问题，不构成存在某个O的主结论反证。alpha=1分支援引降序特征值定理，而目标在不定矩阵中定义为非零谱空间；应用时必须另厘清代数/绝对值排序，不能直接照搬。未完成全证明独立审定，候选不写入经典定理条目。

**迁移与否证路径：** 子空间提取成本可能受益；但用户稀疏注意力分区是任务驱动筛选，未证独立Bernoulli采样或coherence条件。diag(2,0,..,0)的rank-one方向集中于首列，若采不到该列，信号全丢；alpha=0.1时失败概率0.9。这是满足低秩却缺少可行采样条件的反例。保留研究候选，无生产采样改动；后续先测实际矩阵秩/谱尾、coherence、噪声与端到端代价，再考虑实验。

另检索到[Geometric bias in eigenspace perturbation under random heterogeneous noise](https://arxiv.org/abs/2606.11263)，2026-06-09，Liu/Wang/Wang；仅获取摘要，原文访问失败，版本/发表状态未核实，不采纳其定理。本轮没有遍历所有最新论文，也不宣称上述是领域最新一篇。
