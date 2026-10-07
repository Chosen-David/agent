# Schur 补、块消元与边界等效

稳定 ID：math.schur-complement-block-elimination；语义版本1；核查日期2026-10-07。

## 对象、符号与前提
M=[[A,B],[C,D]]，A 方阵可逆，S=D−CA⁻¹B；Hermitian正定判据另要求C=B*。

## 经典结论
M=[[I,0],[CA⁻¹,I]] diag(A,S) [[I,A⁻¹B],[0,I]]；detM=detA detS。Mx=(f,g) 化为 Sx₂=g−CA⁻¹f，x₁=A⁻¹(f−Bx₂)。Hermitian情况下 inertia(M)=inertia(A)+inertia(S)；M>0 iff A>0且S>0。

## 证明思路与可复核推导
逐块相乘验证因子化。Hermitian情况下因子为 L diag(A,S)L*，可逆合同保持惯性；SPD若成立其A主块SPD，逆向两块正给整体正。消元需同时变换rhs，不只替换D。

## 正例与边界
[[2,−1],[−1,2]] 消去首变量得到S=3/2。对接地电阻网络消内部节点，边界电压与电流响应完全保持，此为线性方程严格迁移。

## 误用反例与拒用条件
[[0,1],[1,0]] 整体可逆但A=0不可逆，需换枢轴。简单删除内部节点用D代替S改变响应；奇异未接地拉普拉斯不能直接求A逆（可能内部块可逆，但必须检查）。

## 问题结构与迁移
保持边界消费者观测的精确消元；实际实现用solve A而非显式逆，误差与 fill-in 成本单独评估。

## 前置关系与来源版本
基础前置：有限维空间、基、矩阵乘法和域算术；涉及内积的条目另需共轭转置/正定范数。本条在正文重述使用的基础结论，导航关联不要求一次加载整条课程。准确出处：[2023-06-01 block factorization、positive-definite property；边界映射为本项目推导](https://nhigham.com/2023/06/01/what-is-the-schur-complement-of-a-matrix/)。Axler 使用第四版、作者2026-08-16 PDF修订；Saad 使用第二版2003；Conrad未标日期的讲义以本轮PDF哈希固定；网页按标题日期与检索日期固定。PDF哈希/近期论文筛选见本轮 sources.json/research.md。

## 验证状态与限制
已核对所列来源的相关段落，并人工检查上面的证明思路/自推公式。verify.py 对该主题给公开正例、边界或反例；Fraction精确运算与float64数值检查分别标注。数学证明核查不是 Lean 形式化证明；计算实例不证明一般结论。未做同模型Agent A/B或真实GPU系统测试；没有性能收益声明。
