# 有限softmax的KL、中心化误差与Fisher曲率

ID `math.softmax-kl-fisher`，版本1。触发：概率预测器的分数误差应使用哪个度量？低秩重建好是否代表概率质量好？本卡补齐KL几何，已有TV/输出界复用 `math.softmax-barycenter-error`，不重复称为新发现。

## 对象与准确结论

共同非空有限支持集J，n=|J|，s,t∈Rⁿ均有限，p=softmax(s)，q=softmax(t)，e=t−s，R=max e−min e。自然对数，KL单位nat；温度τ>0已计入s,t。定义d=e−(1ᵀe/n)1，A(x)=logΣexp x_i，p_u=softmax(s+ue)。本卡自足有限推导（非形式化），经典LSE微分与正半定Hessian见来源1：

\[
D_{KL}(p\Vert q)=A(s+e)-A(s)-p^Te
=\int_0^1(1-u)e^TF(p_u)e\,du,
\quad F(p)=\operatorname{diag}p-pp^T.
\]

方向重要：p||q的梯度在s；q||p交换端点而不是复用同一线性项。F为categorical Fisher，F1=0，eᵀFe=Var_p(e)。n≥2时零空间恰为span{1}；n=1矩阵0。

全局上界及条件下界：
\[
0\le KL(p\Vert q)\le R^2/8\le\|d\|_2^2/4.
\]
若**整个路径**每个p_{u,i}≥m>0，
\[
KL(p\Vert q)\ge(m/2)\|d\|_2^2.
\]
可保守选L=max{osc(s),osc(t)}、m=e^{−L}/n；有限路径的振幅不大于L。这个m依赖数据，不能当统一全局常数。另一个不用独立m的有条件精度包络为
\[
\tfrac12e^{-R}\operatorname{Var}_{p}(e)
\le KL(p\Vert q)\le
\tfrac12e^{R}\operatorname{Var}_{p}(e).
\]
因此½Var_p(e)是小R的局部代理，R大时包络宽，不应报成精确KL；同样不能由单点Fisher的零/很小值保证任意大扰动无害。

## 可复核推导

1. log(p_i/q_i)=−e_i+A(s+e)−A(s)，按p平均得KL恒等式。LSE梯度为softmax，微分再得F；对f(u)=A(s+ue)用二阶积分余项得到加权路径积分。
2. 对任何分布r，Var_r(e)=min_cΣr_i(e_i−c)²。不等式Var≤R²/4：取区间中点c使每项≤R²/4；积分权重总和½。R²≤2||d||²由最大、最小坐标差的柯西不等式。这个上界也证明Hessian的二范数≤½，不需假装引用未读定理。
3. 若r_i≥m，则Var_r(e)≥m min_cΣ(e_i−c)²=m||d||²；沿全路径积分即下界。对路径每对坐标差是端点差的凸组合，最大振幅≤L；分母≤n exp(maxx)，分子≥exp(minx)得m。
4. p_{u,i}/p_i=exp(ue_i)/E_p exp(ue)，夹在e^{−R}与e^R之间。对每个c比较加权平方，再分别最小化，得e^{−R}Var_p(e)≤Var_{p_u}(e)≤e^RVar_p(e)；积分得包络。

这都是实数数学，不保证浮点实现误差。计算用max-shift、log概率和适当精度；小KL时A(t)−A(s)−p·e可能抵消。概率下溢后不要把log0的Inf当理论结果；需要更高精度或误差区间。本轮有限float64/高精度参考检查不是全输入浮点认证。

## 正例、边界和拒用

- s=(0,0)，e=(a,−a)：KL(p||q)=log cosh a，R=2|a|，上界a²/2，局部a→0相切。a=1时KL≈.43378≤.5。
- e=c1任意大：q=p，KL=0，d=R=0；原始||e||²可任意大。应在商空间Rⁿ/span{1}分析，不为共同shift分配低秩预算。
- **无全局下界**：s=(M,0)，t=(M+1,0)，||d||²=½不变，而M→∞两分布趋于同一顶点，KL→0。任何不依赖概率下限的正二次下界都失败。这解释分数低秩不等于概率有效秩，不证明具体indexer收益。
- 硬mask变化：p=(½,½)，q=(1,0)，KL(p||q)=∞；没有有限e不能套上述界。相同mask可限制到共同非空可见支持集后使用。
- 温度τ：若原始扰动e_raw，R=osc(e_raw)/τ；忘记温度会使预算不可靠。τ=0/greedy不在softmax前提内；共同shift不影响argmax，但小概率KL也不保证greedy不翻转。
- n=1、常数扰动均为0；空支持集未定义。自然对数的nat界换log2须除ln2。
- 同样的KL/TV可对应不同value或任务损失。不能以本卡替代attention输出几何、端到端评测或未见测试。

## 可迁移问题结构与最小验证

**Indexer校准（待实测候选）**：代理与完整attention在同一query、历史、支持集的有效分数对应s,t；R/中心化误差/Fisher方向是可计算局部指标。NoPE、RoPE、混合都要求先完成实际位置变换与统一缩放；本卡不允许跨频率无损融合。如果代理仅选集合，最终使用原分数，此KL衡量的是选择代理，不能重复记作最终输出KL。

冻结真实Q/K/V、层、method及投影维度预算；开发集同时保存中心化MSE、½Var_p(e)、精确KL、R、质量、output误差；检查局部代理随R增大何时失效，以及饱和层的排名是否不同。冻结方法后用新校准集及未见文档测质量/成本，再自由生成端到端。在输出词表上测KL须获取**完整执行器的生成概率**，不能把attention token轴的KL直接当输出词表轴KL。接 `math.sequence-tv-coupling` 时用已有TV条目从**输出logits**给单步δ上界，逐前缀满足才能传播；attention局部KL尚无自动跨层/自回归保证。没有真实trace，本轮不部署。

**跨领域Boltzmann权重**：有限能级E_i、固定β>0，s_i=−βE_i；能量误差δE对应e_i=−βδE_i。能量共同基准平移不影响分布，R无量纲，KL用nat，KL≤β²osc(δE)²/8。保留的是归一化指数族的严格数学关系；真实平衡/温度和有限能级建模未检验。不能拿非平衡开放系统直接套平衡概率核。

## 前置关系、来源与实际状态

自足推导，无强依赖；关系导航：TV/输出界 `math.softmax-barycenter-error`，value Gram几何 `math.attention-output-geometry`，双线性MSE最优 `math.weighted-bilinear-low-rank`（目标不同），序列传播 `math.sequence-tv-coupling`。仅在组合使用时加载必要前提。

1. Blanchard, D. J. Higham, N. J. Higham, *Accurately Computing the Log-Sum-Exp and Softmax Functions*, IMA Journal of Numerical Analysis 41(4),2311–2330, DOI10.1093/imanum/draa038；作者认可稿May15,2020，https://www.pure.ed.ac.uk/ws/portalfiles/portal/150063512/paper.pdf 。核查§1式(1.1)–(1.4)、§2 Hessian/Jacobian及§4 shifted算法；本卡KL与上下界是自足有限推导，不归因于该文。
2. Gerard Conangla Planes, *How Much Rank Does LoRA Need? Rank-Error Bounds for Transformer Attention*, arXiv:2608.26052；近期筛选与版本/阅读范围见本轮research.json。作者研究query LoRA概率KL与分数谱误差，不能直接当选择FC/KV或kernel速度定理。无本地复现。
3. Boursier/Boyer, *Softmax as Linear Attention in the Large-Prompt Regime*, ICML2026 PMLR306:9392–9429，正式出版页 https://proceedings.mlr.press/v306/boursier26a.html 。有条件的大prompt/Gaussian/sub-Gaussian理论不是任意模型长文本“自动线性”的保证。

检索日期2026-10-08。公开CPU开发验证及独立验收 `doc/results/math-softmax-kl-20261008/`；无Lean、模型同预算A/B、GPU/真实物理实验。公开题用于修订后不称未见；后续留出协议单独记录。
