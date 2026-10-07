# 谱隙、子空间扰动与投影打分证书

稳定ID `math.eigenspace-gap-perturbation`，v1。来源固定arXiv1405.0680v1；近期采样论文只在本轮研究记录中作为候选。这里的结论限实对称有限维矩阵。

## 对象、触发与准确结论

问题往往是“矩阵变化很小，方向为什么变很多？”或“重复特征值的基转了，是否需要重建投影？”先确定对象、排序、范数及目标簇。

设A、Ahat=A+E对称，特征值降序，U、Uhat分别由r..s列正交特征向量组成。d=s-r+1，外侧谱隙g>0按元数据定义；P=UU^T、Phat=Uhat Uhat^T。全空间d=n时投影恒I，单独处理。

**已有定理：** Yu–Wang–Samworth Theorem2给出

\[
\|\sin\Theta\|_F\le {2\min(\sqrt d\|E\|_{op},\|E\|_F)\over g},\qquad
\min_{O^TO=I}\|\widehat UO-U\|_F\le {2^{3/2}\min(\sqrt d\|E\|_{op},\|E\|_F)\over g}.
\]

此式不要求E小，但大右端可能没有信息；簇内重根允许，簇外边界不能为零。Frobenius界不能直接改称无维数因子的算子界。不要将“不满足充分条件”解释为“必然不稳定”。

## 可复核的自推rank-one界

以下是本项目独立写出的推导，不是新研究贡献。目标为最大特征值，单位向量u、uhat，g=lambda1-lambda2>0；已知||E||op≤epsilon<g。Rayleigh商给出lambdahat1≥lambda1-epsilon。分解uhat=a u+w，w垂直u，投影特征方程得

\[
(\widehat\lambda_1 I-A_{u^\perp})w=(I-uu^T)E\widehat u.
\]

左侧算子的特征值均≥g-epsilon>0，因此

\[
\sin\theta=\|w\|\le {\epsilon\over g-\epsilon},\quad
\|\widehat P-P\|_{op}=\sin\theta.
\]

最后的等式可在span(u,uhat)中写2×2矩阵核对；符号改变不影响投影。若epsilon<g/2，用Rayleigh极值/Weyl界，lambdahat1-lambdahat2≥g-2epsilon>0，主方向唯一至符号。没有认证epsilon时不能把经验RMSE或平均元素误差代入。

一般簇可保守用||Phat-P||op=||sinTheta||op≤min(1,||sinTheta||F)；投影Frobenius范数为sqrt(2)||sinTheta||F。存在簇内任意正交旋转时逐列向量比较失效。

## 正例、边界和误用反例

A=diag(2,1)，E的两非对角元为0.1；epsilon=0.1、g=1。theta=atan(0.2)/2，实际sin(theta)≈0.09854，小于证书1/9。验证脚本检查闭式特征方程、投影幂等性、范数和误差界。

A=diag(1+delta,1)，E=diag(-delta,delta)，delta>0可任意小；主方向翻转90度，特征值变化≤delta。epsilon/g=1，故不能宣称“绝对矩阵误差小就稳定”。A=I、任意小diag(t,-t)与diag(-t,t)选择相反主方向，未扰动单方向不存在唯一目标。

A=diag(3,3,1)的前两列可旋转90度，基差Frobenius范数2，但P完全相同；第一单向量的簇外边界为零，而完整二维簇的边界为2。这不是理论冲突。非对称矩阵不得沿用以上公式；应另核验奇异子空间、Hermitian变换或非正规条件数。

## 任务映射与成立边界

**自推打分传播：** 若beta≥||Phat-P||op，且||q||≤Q、||k_i||≤K，则|q^T(Phat-P)k_i|≤QK beta。原投影分数第k名与第k+1名差gamma>2QK beta时，候选集合稳定。这只使用内积定义、算子范数与差分代数，独立于关联条目；相关score/topk知识供导航复查。

对于“先子空间→near/far→两端L1/L2”的算法，只在**确实使用这个投影分数**且其余量固定的消费点成立。near/far分区变化、完整点积分数、量化、截断补空间和近似细筛需另外控制；低秩近似误差与换基误差不同。q或k范数未受控时不能推广统一排名保证。未修改任何实际稀疏注意力行为。

物理迁移：固定正定质量M和对称刚度K的无阻尼方程M x''+Kx=0，先在质量坐标y=M^(1/2)x构造A=M^(-1/2) K M^(-1/2)。模态特征值为频率平方，g、epsilon均为s^(-2)，角度界无量纲；A、Ahat须使用同一M和坐标。直接给一般非对称M^(-1)K套对称定理错误；M也变化须先计入坐标和矩阵误差。这里只是精确方程映射及合成数值验证，无真实物理实验。

## 前置、来源与验证状态

前置概念：实对称谱分解、Rayleigh极值、欧氏算子范数、主角度与正交投影；本文rank-one和打分推导写全，requires为空。导航关联低秩SVD、score-difference、topk-margin及线性系统稳定性；这些关系不自动批准应用。

经典来源见元数据：原文Theorem2及Corollary3；证明思路为残差控制→外簇坐标逐项谱分离→主角度→正交对齐，附录eqs(5)-(9)。本项目核对了该路径与rank-one推导，没有重写全部一般簇证明。

实际验证：标准库闭式2×2浮点检查、有限有理矩阵身份与物理量纲/反例；不是Lean形式化证明，不以有限样例替代一般推导。检索案例已公开用于开发/验收，不再属于未见模型测试。没有同模型A/B，无法报告Agent能力或性能实测提升。
