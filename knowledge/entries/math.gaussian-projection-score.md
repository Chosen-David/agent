# math.gaussian-projection-score@1 — 有限高斯打分降维

## 问题触发与准确结论

对象：Q个查询q_a∈R^d、N个键k_i∈R^d；实欧氏内积；A∈R^{m×d}条目独立N(0,1/m)。集合固定或独立于A，epsilon,delta∈(0,1)。概率关于投影抽样，不是关于任意事后选择输入。

**本项目推导的经典集中论证之内积推论**：令c(epsilon)=epsilon²/4−epsilon³/6>0。若

m ≥ ceil(log(4QN/delta)/c(epsilon))，

则以至少1−delta的概率，同时有

|〈Aq_a,Ak_i〉−〈q_a,k_i〉| ≤ epsilon||q_a||||k_i||，所有a,i。

这是充分维度，不是最小维度，也不保证m<d。固定某次抽样，结论是高概率而非该抽样的确定证书；可另外逐项核验指定有限事件。任意固定/训练投影、PCA、列稀疏符号矩阵不自动共享此高斯常数。

## 可复核证明（非形式化）

1. 对任意固定非零x，每行Ax为方差||x||²/m的独立正态，Z=m||Ax||²/||x||²为chi-square_m。由高斯积分，E exp(tZ)=(1−2t)^{-m/2},t<1/2。
2. Markov/Chernoff优化：上尾取t=epsilon/[2(1+epsilon)]，得到Pr[Z≥m(1+epsilon)]≤exp(−m(epsilon−log(1+epsilon))/2)。下尾用E exp(−tZ)，t=epsilon/[2(1−epsilon)]，得到Pr[Z≤m(1−epsilon)]≤exp(−m(−epsilon−log(1−epsilon))/2)。
3. 对0<e<1，e−log(1+e)≥e²/2−e³/3：左右差在0为0，导数e³/(1+e)≥0。−e−log(1−e)≥e²/2：左右差导数e²/(1−e)≥0。因此两尾之和≤2exp(−mc)。零x恒为0不需概率。
4. 对非零q,k归一化u=q/||q||、v=k/||k||。所有u+v和u−v共至多2QN个固定向量，union bound（不需事件相互独立）失败≤4QN exp(−mc)≤delta。
5. 在这些向量的相对平方范数误差均≤epsilon的事件上，极化恒等式给出

|〈Au,Av〉−〈u,v〉| ≤ epsilon(||u+v||²+||u−v||²)/4 = epsilon。

最后乘回两向量范数；零query/key分数精确为0。这一步是条件事件蕴含，不依赖A的分布；概率认证依赖第1–4步。

**排名衔接**：对固定query，E_i=epsilon||q||||k_i||。若完整分数s_i中每个入选i与未入选j均满足s_i−s_j>E_i+E_j，则代理保留Top-k；统一E则gap>2E，见强依赖math.topk-margin@1。等号只保证非反转，可出现tie，不能保证集合不变。注意力logit为s/√d时E也除√d。没有margin证书不能从平均小误差推断保排名。

## 正例、边界与误用

公开精确事件例：A=diag(1,4/5)，u=(1,0),v=(0,1),epsilon=2/5。u±v平方范数2变41/25，相对误差9/50<2/5，点积保持0。这只是一个确定事件样例，不是高斯覆盖实验。

严格排名例：s=(1,0),hat_s=(9/10,1/10),E=1/10，gap1>1/5，集合保持。gap=2E的s=(1/5,0),hat_s=(1/10,1/10)产生tie；gap<E的s=(1/20,0),hat_s=(−1/20,1/10)翻转。u=−v时u+v=0，不能除以零；零向量直接处理。

量词反例：m<d时rank-nullity给非零x∈ker(A)。观察A后取单位x，||Ax||²=0而||x||²=1。不存在该维度下对全部R^d的近等距保证。此x依赖A，未违反固定有限集概率命题。真实模型query若受该sketch影响而生成，不自动满足独立条件；需新的自适应分析或冻结独立轨迹。

求逆反例（本项目精确推导）：g=g'=e1，F=diag(1,99)，P=[1,1]。有限集合{g}的范数/自内积由P精确保持，但g^T F^{-1}g=1，而(Pg)^T(PFP^T)^{-1}(Pg)=1/100。不能把有限向量的几何误差直接当作影响函数误差。P不是高斯样本，此例反驳逻辑蕴含，不反驳高斯定理。F全秩，P不在range(F)上单射。

维度诊断：Q=1,N=1024,epsilon=1/5,delta=1/20时上述充分m约1306，已超过常见d=128。它不能凭该常数为压缩提供可用认证；不意味着所有较低m都失败。

## 迁移与不适用条件

原问题→理论：冻结完整query/key轨迹→有限向量；压缩索引→共用A；完整内积分数→s；代理误差→E；排序→strict gap。NoPE直接适用此数学对象。RoPE只能对**先完成各位置旋转后的固定向量**使用A；先投影再按代表频率旋转须另证AR_m=barR_m A，见rotation-intertwiner。NoPE+RoPE应记录实际拼接/scale；不从名字推断维度/误差。此映射保留线性内积与有限集合，未保留推理反馈、value加权输出或e2e精度。

跨领域传感器匹配也可映射为固定测量向量与模板打分。可证伪预测：逐项核验u±v事件及strict gap成立后，精确算术下排名必须保持；不满足条件的实验只报告经验误差/召回。索引缓存、投影成本、GPU访存/浮点/量化误差均未被该定理消除。

建议最小研究：固定同一轨迹/候选/预算，比较选坐标与高斯草图，报告逐项分数误差分布、分界gap、候选召回、attention-output误差、e2e和总延迟/新增缓存；Gaussian仅基线候选，无生产采用/收益结论。不能拿重合度单一指标代替输出或任务质量。

## 来源及研究筛选

经典：Dasgupta & Gupta，Random Structures & Algorithms22(1):60–65 (2003)，DOI10.1002/rsa.10073；作者PDF Section2 Theorem2.1/Lemma2.2及证明，Section3比较独立高斯映射。其Section2随机正交子空间算法与本文iid高斯映射不同；本文自行推导标准归一化和上述有限内积推论。

近期：Hu et al., A Unified Theory of Random Projection for Influence Functions，arXiv2602.10449 **v2 2026-02-13**（v1 2026-02-11），2026-10-09检索，预印本；仅读摘要、Section1及Section2.1 Theorem1陈述。作者报告未正则化影响在range(F)上对所有g,g'精确保留当且仅当P在该空间单射；本文不采纳未读附录/regularized常数，只用自行可复算反例标记任务对象差异。未复现论文实验；正式发表状态未独立核验。

实际状态：公开精确检查与独立非形式化推导审核，双后端结构检索；不是Lean证明、概率覆盖Monte Carlo、LLM拒用测验或GPU/e2e/token提升。未使用的模型holdouts未读取；公开案例之后只能算开发/回归用例。
