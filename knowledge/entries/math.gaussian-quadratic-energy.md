# 高斯二次能量的谱尾界与相关样本二阶矩

稳定ID：math.gaussian-quadratic-energy；v1；核查2026-10-07。核心经典上尾来自Hsu–Kakade–Zhang(2012) Proposition1.1；以下mgf核查、下尾及相关矩阵迁移为本项目推导，不声称新基础定理。

## 对象、结论与证明
x∈R^m联合N(0,C)，C≥0真实确定；A=Aᵀ≥0固定。定义B=C^(1/2)AC^(1/2)，a=trB，f²=tr(B²)，l=||B||op，Q=xᵀAx。平方根/正交谱分解使用前置math.hermitian-spectral-schur。高斯线性变换及正交不变性使Q与Σ_i λ_i Z_i²同分布，λ_i≥0，Z_i独立N(0,1)。允许C/B奇异；不需逆。E Q=a，Var Q=2f²。

对t>0：
\[
P(Q-a>2\sqrt{f^2t}+2lt)\le e^{-t},\qquad
P(a-Q>2\sqrt{f^2t})\le e^{-t}.
\]
B=0时Q=0几乎处处；单边下阈值可为负，不强行改概率。这里是二次型尾界，Q本身通常不是正态。

可复核mgf：一维高斯积分给E exp(sλZ²)=(1−2sλ)^(-1/2)。独立相乘，
log E exp[s(Q−a)]=Σ[-sλ−½log(1−2sλ)]。
对0≤u<1，−log(1−u)−u=Σ_(k≥2)u^k/k≤u²/[2(1−u)]，故0<s<1/(2l)时log mgf≤s²f²/(1−2ls)。Chernoff中取s=√t/(f+2l√t)，其中f=√f²，得到上尾。下尾使用−log(1+u)+u≤u²/2（导数积分即可核对），log E exp[−s(Q−a)]≤s²f²；取s=√t/f。零f单独处理。

## 从标量方向到矩阵：严格的有限模型迁移
设G∈R^(n×d)元素独立标准正态，X=T^(1/2)GΣ^(1/2)，T∈R^(n×n)为真实确定相关矩阵(T≥0,diagT=1)，Σ≥0。行间可以相关；各行边缘协方差为Σ，跨行Cov(X_i,X_j)=T_ijΣ。这是**可分离联合高斯模型**，不是任意相关样本。
S=XᵀX/n，则E S=Σ。对事先固定的单位u，γ=uᵀΣu；uᵀSu与(γ/n)zᵀTz同分布。因此相对方向误差上尾宽度为
\[
2\sqrt{t/n_2}+2t/n_\infty,\quad
n_2=n^2/\mathrm{tr}(T^2),\quad n_\infty=n/\|T\|_{op}.
\]
下尾只有平方根项。γ=0精确处理。两种计数均介于1与n，但含义不同；只知道n₂不能恢复所写上尾线性项。与均值的n²/(1ᵀT1)也不同。

若需全矩阵谱保证，取事先确定的1/4球面网N，体积装球论证给|N|≤9^d：极大1/4分离点的小球半径1/8互不相交，均在半径9/8球内；极大性保证覆盖。对实对称H，取单位最大绝对Rayleigh向量v与距离≤1/4的u，则|vᵀHv−uᵀHu|≤(1/2)||H||，故||H||≤2 max_N|uᵀHu|。确定BΣ≥||Σ||，令t=log(2·9^d/δ)，δ∈(0,1)，逐网方向并合两尾得
\[
P\!\left(\|S-\Sigma\|_{op}>
2B_\Sigma\left[2\sqrt{\mathrm{tr}(T^2)t}/n+2\|T\|_{op}t/n\right]\right)\le\delta.
\]
这是保守维数依赖界，不声称intrinsic-rank最优；若界远超任务容差，就不能认证，不能据此断言算法一定失败。固定某一方向的尾界不允许直接用于同数据挑出的最大特征向量；上面的有限网论证才将它升级为全方向。

## 正例、反例与计算边界
T=I：n₂=n∞=n。T=11ᵀ：两者1，复制n次不增加协方差信息。AR(1) T_ij=φ^|i−j|需合法平稳高斯生成，tr(T²)=n+2Σ(n−h)φ^(2h)，n₂对应平方目标而非均值目标。
三个点的等相关矩阵：offdiag=.5的谱为(2,.5,.5)，offdiag=−.5的谱为(1.5,1.5,0)。trT=3、trT²=4.5相同，n₂都2，最大谱/上尾线性项不同。单个方差等效计数不足以确定这条尾界。

高斯边缘不够：Z∼N(0,1)，独立随机符号ε，x=(Z,εZ)，边缘正态、C=I₂，但Q=||x||²=2Z²，不是χ²₂。其Var Q=8而联合高斯公式给4；t=10也可算出它违反误套的C=I₂上尾。重尾有限方差不提供本mgf；A不定时不能套PSD结论。同数据挑A=xxᵀ/||x||²会使“rank1固定能量”变成||x||²，拒用固定A保证。

未知均值时S是二阶矩；用同批样本均值中心化后目标/随机算子变化，不能继续宣称E S=总体协方差。未知T、Σ用样本谱/ACF代入不自动覆盖；跨行依赖非T_ijΣ时模型映射失败。若T正定，真T的白化T^(-1/2)X可还原独立行；但小特征值放大扰动，||T^(-1/2)E||F≤||E||F/√λ_min(T)。估计白化、秩截断和实际成本另证。

## 任务价值、单位、关系与验证
子空间校准：若真实embedding满足上述模型，才可将本谱误差界传给math.eigenspace-gap-perturbation，继续核对谱隙与同一目标投影。真实模型未建立，因此只给候选分析，不更改indexer或Agent生产行为。
电压测量：Σ及S单位V²，T/n₂/n∞无量纲；标量Q的A若无量纲则Q单位V²，f²单位V⁴。传感器一般不自动联合高斯/可分离；控制合成过程可验证，真实实验未运行。

强前置：math.hermitian-spectral-schur（谱/平方根）；相关：math.dependent-mean-variance（不同目标ESS）、math.centered-covariance-merge（中心化目标）、math.matrix-bernstein-covariance（独立有界的另一组前提）、math.eigenspace-gap-perturbation（谱隙后续，不能自动加载或采用）。
来源为作者托管ECP最终PDF，DOI10.1214/ECP.v17-2079，Proposition1.1 PDF1、AppendixA.2/LemmaA.4 PDF6；低维二次谱尾上界是经典事实，本文矩阵转换须核对所有额外模型条件。原始来源/固定哈希见sources.json。
一般推导人工核查；Fraction有限矩、float64/MGF/边界及固定种子合成验证见verify.py/checks.json。未运行Lean、未见模型应用/拒用测试、模型A/B、GPU或传感器实验。数值覆盖频率不证明一般尾界；近期论文只作为research.md的研究候选。
