# 高等代数课程边界与双索引

完成的是有限维高等线性代数标准主线及有界矩阵分析扩展；不是全部抽象代数或整个研究前沿。原有 SVD、Cauchy–Schwarz、top-k margin、谱子空间扰动和求解稳定性保留，不重复建卡。下列各主题均有对象/假设/准确结论、证明思路、正例、边界与误用反例；来源定位在元数据及 sources.json，有限检验在 verify.py。

|主题/学科入口|知识 ID|不提示定理名的问题结构入口|近期筛选簇|
|---|---|---|---|
|多项式、带余除法与互素分解|[math.polynomial-euclidean-calculus](../../../knowledge/entries/math.polynomial-euclidean-calculus.md)|整数系数只能保留整数时，t除以2t能否总有次数更小的余式？|block-polynomials|
|向量空间、商空间与对偶查询的保真条件|[math.rank-nullity-quotient](../../../knowledge/entries/math.rank-nullity-quotient.md)|线性编码把(x,y,z)变成(x+y,z)，收到编码后能恢复x+y吗？能恢复x吗？|rrqr|
|矩阵秩、秩分解与左右等价|[math.matrix-rank-factorization](../../../knowledge/entries/math.matrix-rank-factorization.md)|矩阵的第二行是第一行的两倍，可以如何精确存储并计算它的作用？|rrqr|
|相似、等价、合同与坐标不变量|[math.similarity-invariants](../../../knowledge/entries/math.similarity-invariants.md)|同一个线性状态在新坐标中的矩阵怎么变？这种变化保持欧氏距离吗？|schur-stability|
|行列式、可逆性与体积解释|[math.determinant-invertibility](../../../knowledge/entries/math.determinant-invertibility.md)|二维变换的面积倍率是1，是否足以断定各方向误差不会放大？|sylvester|
|特征多项式、最小多项式与主分解|[math.minimal-polynomial-primary-decomposition](../../../knowledge/entries/math.minimal-polynomial-primary-decomposition.md)|一个更新算子的某个多项式等于零，如何拆成互不干扰的不变子空间？|random-block|
|循环模、伴随矩阵与有理标准形|[math.rational-canonical-cyclic](../../../knowledge/entries/math.rational-canonical-cyclic.md)|实系数状态更新有不可分裂的二次因子，如何在实域给出循环伴随块表示？|block-polynomials|
|广义特征空间、Jordan 链与块恢复|[math.jordan-generalized-eigenspaces](../../../knowledge/entries/math.jordan-generalized-eigenspaces.md)|已知重复根对应各次幂的核维数为2,3,4,4，如何恢复每条状态链长度？|matrix-functions-classic-only|
|起点最小多项式与精确 Krylov 闭包|[math.krylov-minimal-polynomial](../../../knowledge/entries/math.krylov-minimal-polynomial.md)|固定起点反复乘同一矩阵，第三个状态与前两个线性相关，何时能永远用两个坐标？|random-block|
|内积、正交投影、QR 与最小二乘|[math.orthogonal-projection-qr](../../../knowledge/entries/math.orthogonal-projection-qr.md)|用正交列表示观测，如何找距离最近的投影并求最小二乘残差？|rrqr|
|自伴、正规谱定理与酉 Schur 分解|[math.hermitian-spectral-schur](../../../knowledge/entries/math.hermitian-spectral-schur.md)|一个复矩阵有特征向量基，是否就能选互相正交的特征向量？|schur-stability|
|SVD、伪逆与最小范数解|[math.moore-penrose-pseudoinverse](../../../knowledge/entries/math.moore-penrose-pseudoinverse.md)|观测系统秩亏而数据不一致，如何选择残差最小且范数最小的解？|tensor-als|
|双线性型、二次型与实合同惯性|[math.bilinear-quadratic-inertia](../../../knowledge/entries/math.bilinear-quadratic-inertia.md)|实对称能量矩阵经可逆变量替换后，正负能量方向数会变化吗？|kronq|
|广义自伴特征问题与质量度量|[math.generalized-hermitian-eigenproblem](../../../knowledge/entries/math.generalized-hermitian-eigenproblem.md)|振动系统同时含质量矩阵和刚度矩阵，模态在哪个内积下正交？|tl-filter|
|张量积、Kronecker 运算与向量化|[math.tensor-kronecker-calculus](../../../knowledge/entries/math.tensor-kronecker-calculus.md)|把二维未知矩阵按列展开，左右矩阵乘法对应什么大线性算子？复数时用转置还是共轭？|tensor-als|
|矩阵函数、Hermite 插值与缺陷谱|[math.matrix-function-jordan-calculus](../../../knowledge/entries/math.matrix-function-jordan-calculus.md)|更新矩阵只有零特征值，为什么指数作用仍可能产生很大的非零状态？|random-block|
|Sylvester 方程、算子分离度与解矩阵条件|[math.sylvester-equation-separation](../../../knowledge/entries/math.sylvester-equation-separation.md)|左右作用的矩阵方程残差很小，特征值间距能否直接保证解矩阵再求逆可靠？|sylvester|
|Schur 补、块消元与边界等效|[math.schur-complement-block-elimination](../../../knowledge/entries/math.schur-complement-block-elimination.md)|消掉内部网络节点，怎么严格保留边界电压和电流关系？直接删除行列是否等价？|sylvester|

## 验收和停止边界

结构检索与有限算例是本轮可验收项；有权威证明但未完成 Lean 的条目仍为人工核对推导。经典闭包、精确分类和条件等价不因有限算例通过而升级成形式化证明。自然问题与反例已公开，全部是开发/回归材料。没有独立未见测试或同模型A/B，不能报告主AI推理能力普遍提升。

课程外保留：Galois/域扩张、一般环/交换代数、无限维算子、完整高阶张量秩理论、全量GPU复现及形式化证明。各主题近期研究按相关结构簇筛选；没有找到可采用的新结论时保留经典条目，不为多项式/行列式基础捏造最近突破。
