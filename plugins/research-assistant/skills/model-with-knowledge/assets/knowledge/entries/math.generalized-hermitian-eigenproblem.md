# 广义自伴特征问题与质量度量

稳定 ID：math.generalized-hermitian-eigenproblem；语义版本1；核查日期2026-10-07。

## 对象、符号与前提
A=A*，B=B*>0，Az=λBz；B 的正定性必须成立，不能仅可逆。

## 经典结论
B=LL* 后 C=L⁻¹AL⁻* 为 Hermitian；Cu=λu 对应 z=L⁻*u。λ 实，模态 z_i*Bz_j=δ_ij。Rayleigh 商为 z*Az/(z*Bz)。

## 证明思路与可复核推导
将 z=L⁻*u 代入广义方程并左乘 L⁻¹，直接得到 C；C*相等，使用自伴谱分解得到正交 u。回代度量 z_i*Bz_j=u_i*u_j，保留质量内积而非默认 Euclidean。

## 正例与边界
K=[[2,−1],[−1,2]] N/m，M=diag(2,1) kg，λ=(3±√3)/2 s⁻²，角频率ω=√λ s⁻¹。

## 误用反例与拒用条件
B=diag(1,−1)，A=[[0,1],[1,0]] 给特征值±i；B可逆不足。B奇异是矩阵铅笔问题，不能用本条Cholesky。数值近似B若失去SPD需要拒用/修复证据。

## 问题结构与迁移
有限元与带权子空间先白化或保 B 内积；B-正交不必欧氏正交。迁移保存方程与能量单位，不借物理比喻说明 Agent 效果。

## 前置关系与来源版本
基础前置：有限维空间、基、矩阵乘法和域算术；涉及内积的条目另需共轭转置/正定范数。本条在正文重述使用的基础结论，导航关联不要求一次加载整条课程。准确出处：[LAPACK Users Guide Generalized Symmetric Definite Eigenproblems，type1 化归和回代；在线版检索2026-10-07](https://www.netlib.org/lapack/lug/node54.html)。Axler 使用第四版、作者2026-08-16 PDF修订；Saad 使用第二版2003；Conrad未标日期的讲义以本轮PDF哈希固定；网页按标题日期与检索日期固定。PDF哈希/近期论文筛选见本轮 sources.json/research.md。

## 验证状态与限制
已核对所列来源的相关段落，并人工检查上面的证明思路/自推公式。verify.py 对该主题给公开正例、边界或反例；Fraction精确运算与float64数值检查分别标注。数学证明核查不是 Lean 形式化证明；计算实例不证明一般结论。未做同模型Agent A/B或真实GPU系统测试；没有性能收益声明。
