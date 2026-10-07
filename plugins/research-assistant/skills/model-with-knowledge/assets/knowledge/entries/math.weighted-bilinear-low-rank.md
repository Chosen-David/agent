# 二阶矩加权的双线性低秩分数近似

稳定ID：math.weighted-bilinear-low-rank；版本1；核查2026-10-07。

## 问题触发与范围
压缩key能量最大的方向，是否也能压缩query/key点积分数？相同索引维数下比较K-PCA与双侧任务度量。经典截断SVD见强依赖math.low-rank-svd；以下概率目标的化归是本条目自行推导，不宣称新的原创定理。

## 对象、假设与准确结论
q∈R^m,k∈R^n独立，Sq=E[qqᵀ]、Sk=E[kkᵀ]为有限正定非中心二阶矩。H∈R^(m×n)固定，目标分数qᵀHk，以qᵀMk近似，rank(M)≤r，r∈{0,…,min(m,n)}。中心化协方差不能直接替代Sq/Sk；无需零均值或高斯。

设E=H−M，则
L(M)=E[(qᵀEk)²]=tr(E Sk Eᵀ Sq)=||Sq^(1/2)(H−M)Sk^(1/2)||F²。
取C=Sq^(1/2)HSk^(1/2)，对C截断SVD得Cr。最小值为Σ_(j>r)σj(C)²，最优解之一为
M*=Sq^(−1/2)Cr Sk^(−1/2)。
若Cr=Ur Dr Vrᵀ，设A=Dr^(1/2)UrᵀSq^(−1/2)，B=Dr^(1/2)VrᵀSk^(−1/2)，则M*=AᵀB，qᵀM*k=(Aq)ᵀ(Bk)。r=0时使用空特征/零矩阵；全秩预算时L=0。重复奇异值允许多个最优子空间，不宣称唯一。秩不足输入的伪逆/支持空间推广不包含在本条目的SPD接口中。

## 可复核证明
1. 对k取条件期望：E_k[(qᵀEk)²|q]=qᵀE Sk Eᵀq，独立性允许用固定Sk。
2. 对q取期望，用E[qᵀFq]=tr(F Sq)得迹式；展开Frobenius平方即双侧权重表达。
3. 两侧平方根可逆，B0=Sq^(1/2)M Sk^(1/2)保持秩，且与所有rank≤r矩阵双射。因此问题严格等价于min_rank(B0)≤r ||C−B0||F²。
4. 用已有Eckart–Young–Mirsky结论，Cr达到尾部奇异值平方和。逆映射和因式分解直接验证。

## 正例、边界和误用反例
H=I2,Sq=diag(.01,100),Sk=diag(100,1)，r=1。K-PCA选第一坐标，分数误差为100；本目标选第二坐标，误差为1。key的高能量不等于query可见的高能量。

非零均值：q≡2,k≡3,H=1,M=0，误差36；用中心化协方差会错误给0，非中心二阶矩4×9正确。

相关性反例：q=k∈{−√2,0,√2}，概率{1/4,1/2,1/4}。两者二阶矩均1，但H=1,M=0时E(qk)²=2而非1。这里必须拒用独立因子化，不用样本数增加弥补缺前提。

Sq/Sk奇异或含负特征值时，本算法拒绝或转另一个经过核验的支持空间模型；正则化Sq+λI定义的是另一个目标，不能声称精确优化原风险。实际计算优先Cholesky/线性solve，不显式形成逆；记录最小特征值、条件数、dtype和重建残差。PSD数值噪声与真正非正定须区别处理。

## 可解决结构与不适用条件
适用于已指定独立乘积分布下、有限维双线性分数的均方低秩近似，包括独立载荷/应变传感器的响应压缩。q为载荷系数，k为传感器模态，H为固定耦合；若单位不一致，先按物理量纲定义权重，不用无量纲误差冒充物理指标。

真实attention同文档的q,k通常相关，因果位置采样也不是无条件独立。可用校准q×校准k全部笛卡尔积定义一个**经验乘积分布代理**，该有限目标严格成立；它不等于真实paired风险。需在独立文档留出集检查成对分数、排序、实际V/W输出及e2e。

post-RoPE实际q/k也可定义此代理，但固定矩与独立性仍须核对；模型的不同位置/长度可能改变目标。一般A,B不相同、M不对称，不是UUᵀ。压缩维没有自动继承某个原始FC频率；不保证ARp=RbarpA。不能跨频率融合后声称单频RoPE无损。pre-RoPE低秩也不保证post-RoPE低秩。

分数MSE不保证top-k保持，缺少逐点误差和排序margin时拒绝用math.topk-margin；也不保证softmax或value输出最优，后者按math.attention-output-geometry单独检验。缓存z_k是额外索引存储，最终保留全KV时不自动减总缓存。校准/投影计算成本需测量。

## 前置与相关关系
强依赖math.low-rank-svd@1；math.generalized-hermitian-eigenproblem提供度量变换导航（不是此证明的强依赖）；math.attention-output-geometry区分分数与输出目标；math.topk-margin需补充分数逐点条件。

## 验证状态
显示证明经独立数学审阅，CPU有限产品分布与随机SPD输入检查见doc/results/math-weighted-bilinear-20261007/。公开开发问题含未点名定理的压缩问题、传感器跨域与相关性/奇异性拒用；拒用为人工前提核对，不是模型测评。数值样例不替代一般证明。无Lean、真实模型A/B、GPU时延或未见模型验收；待执行留出协议不记为已完成。

## 来源
David Bindel, Cornell CS6210, Matrix nearness problems, 2025-10-15, §Low rank and Eckart–Young–Mirsky，https://www.cs.cornell.edu/courses/cs6210/2025fa/lec/2025-10-15.html ，访问2026-10-07。只用作者讲义核对SVD最优性；概率迹式和双侧化归是上述推导。
