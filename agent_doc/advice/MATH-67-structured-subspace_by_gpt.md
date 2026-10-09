# 共享子空间何时可以复用：结构扰动与谱穿越

候选ID：candidate.structured-subspace-reuse@1；文档候选，不进入canonical卡或生产行为。学科索引：矩阵分析、线性代数；结构索引：不变子空间、块扰动、谱排序、投影复用。检索日期2026-10-10 Asia/Shanghai（UTC2026-10-09）。本文不是新定理贡献或共享子空间的精度实测。

## 来源、已有知识与本轮增量

实际按结构检索并阅读 math.eigenspace-gap-perturbation@1；其条目正文SHA256为4e42b09256c16f4bdf3a7d2ecce11c4fb5c9e856655a5358fb4f0c7d8b8aa372，元数据SHA256为72342d6181acb1ea52118c3f09560b95b288a20f26e53a206d90dbbab3ae85d2。原卡已覆盖普通扰动、换基歧义和投影打分，本轮不重复新增卡。math.sylvester-equation-separation@1的正规/非正规区别仅作导航。

经典依据：[Zhaojun Bai作者讲义](https://www.cs.ucdavis.edu/~bai/Winter09/eig_theory.pdf)，*Basic Theory of Algebraic Eigenvalue Problems: a quick review*，Winter09路径版本，§4、Theorems4.2–4.3（PDF第10–11页），支持实对称Rayleigh/minmax与Weyl；当前修订日期未建立。[Yu–Wang–Samworth作者正式版](https://personal.lse.ac.uk/wangt60/publication/DKvariant.pdf)，*A useful variant of the Davis–Kahan theorem for statisticians*，Biometrika102(2),315–323,2015，Theorem2，印刷页317。本轮直接arXiv v1访问失败、Cambridge作者副本502，成功读到另一作者LSE正式版，不伪称重新读取v1。以下块分解和复用判据为本项目自推，不归为讲义原句。

## 精确块判据与证明

A、E为同维有限实对称矩阵，B=A+E。取1≤k<n，A特征值降序、g=λk(A)−λk+1(A)>0，P为唯一top-k正交投影，Q=I−P。子空间内重根允许；边界重根不满足这一目标的唯一性。

**不变性：** QEP=0当且仅当EP=PE。证明：对称性给PEQ=(QEP)^T；于是E=PEP+QEQ，且EP=PE=PEP。反向交换时QEP=QPE=0。A与P本来交换，所以B也块对角。

**排序：** 在这个不变块前提下，P仍为B的唯一top-k投影，当且仅当

$$\lambda_{\min}(B|_{\operatorname{im}P})>\lambda_{\max}(B|_{\operatorname{im}Q}).$$

限制算子是各自子空间的k×k和(n−k)×(n−k)表示，不是把完整PBP矩阵的额外零特征值拿来算最小值。证明：B的谱是两块谱的并集；严格隔开意味着全部P块特征值恰是最大的k个；若相等则边界可混合、无唯一top-k，若逆序则至少一个Q方向超过P方向，原P不再是top-k。

Rayleigh极值给出充分证书

$$g+\lambda_{\min}(E|_{\operatorname{im}P})-\lambda_{\max}(E|_{\operatorname{im}Q})>0.$$

因为P块最低值≥λk(A)+λmin(E|P)，Q块最高值≤λk+1(A)+λmax(E|Q)。该保守式失败不意味着真实块谱一定穿越，必须回查实际块谱。这比只看||E||/g多利用了结构，但检查成本未验证。

## 近似不变块：只把跨块量当扰动

一般E不交换时定义D=PBP+QBQ、F=PBQ+QBP，B=D+F。D对P/Q块不变。记

$$h=\lambda_{\min}(D|_P)-\lambda_{\max}(D|_Q)>0,\quad C=QEP.$$

在P/Q正交基中F=[[0,C^T],[C,0]]，其平方为diag(C^TC,CC^T)，故||F||op=||C||op，||F||F=√2||C||F。不能把只测某些条目的平均误差当这两个范数的上界。

令U为P正交基，Uhat为B降序top-k的选择正交特征基。Yu等Theorem2应用于D与B，得到

$$\|\sin\Theta(U,\widehat U)\|_F\le {2\min(\sqrt{k}\|F\|_{op},\|F\|_F)\over h}.$$

P是D的top-k投影因为h>0。边界若在B重根，此界允许选择的top-k子空间，**不认证其唯一**。Weyl另给B的边界间隔≥h−2||F||op，严格为正时才确认唯一。投影误差可保守取β=min(1,该Frobenius角度上界)，因为同秩正交投影差的算子范数为最大主角度正弦；不能直接把上述式称为无√k维度因子的算子界。

这一方式允许块内变化很大而跨块很小；若h≤0，P已经不是D的隔离top-k，不能沿用这个证书。h很小或上界≥1时也可能无信息，不能据此断言真实误差大。

## 公开解析正例与反例

| 情况 | 正确判断 |
|---|---|
| A=diag(2,1)，P=e1e1^T，E=100I | E范数100远大于g=1，但跨块0、B=diag(102,101)，P保持。标量平移不改变任何特征子空间。 |
| 同A，E=diag(−2,2) | 与P交换但B=diag(0,3)，谱排序穿越，top-1变为e2；仅查交换条件会误用。 |
| 同A，E=diag(−1,0) | B=I，原P是不唯一选择之一；不能宣称唯一top-1复用。 |
| A=diag(3,3,1)，k=2，P=diag(1,1,0)，E在P块为[[0,1],[1,0]] | P块谱4、2，Q块1；内部基改变，但P不变。逐列比较会误报。 |
| A=diag(2,1)，E=[[100,1/10],[1/10,100]] | D=diag(102,101)，h=1；||F||op=1/10，B边界gap≥4/5>0。k=1角度上界1/5；准确角θ=atan(1/5)/2，sinθ约0.09854。这里解析公式非执行测量。 |
| A=diag(1+δ,1)，E=diag(−δ,δ)，δ>0趋零 | 跨块0仍穿越；绝对误差小不代表排序稳定。 |
| 非对称K/QK矩阵 | 拒绝直接套实对称特征投影结论；需协方差/Gram或相应奇异子空间理论，并检查对象改变。 |

## 近期研究筛选：交互项不等于随机噪声借口

[Tran–Vu, arXiv2510.22393v1](https://arxiv.org/html/2510.22393v1)，2025-10-25提交。arXiv当前列 *Communications in Contemporary Mathematics2025* 与DOI10.1142/S021919972550035X；本轮核对v1§2，未核对期刊最终文本。它是相关2025扩展，不冒称最近30/90天论文。

Theorem2.1是实对称、leading-p的确定性界：r为满足|λp−λr+1|≥|λp|/2的最小整数r≥p（使用原文的索引定义，须确认该r有定义），σ1=||A||op=max_i|λi|，x=max_{i,j≤r}|u_i^TEu_j|；本段||·||均为谱范数，δp=λp−λp+1，要求4||E||≤δp≤|λp|/4，结论保留24、r²和log项：

$$\|\widetilde\Pi_p-\Pi_p\|\le24\left({\|E\|\over|\lambda_p|}\log{6\sigma_1\over\delta_p}+{r^2x\over\delta_p}\right).$$

这里r不是随便用“压缩维度”替代，x也不是本文跨块C。该定理本身不需要Wigner；随机推论Corollary2.1另有分布和渐近前提。作者关于近似锐性的措辞是作者判断，本轮不验证最优性。不能删常数和r²/log后称数值收益，更不能把确定性量化/训练误差直接当iid零均值Wigner。

2026发现查询命中Spectral-LSH线索arXiv2607.19368，但原站访问失败；未核验版本、全文或发表状态，未采用其理论与实验。停止扩展检索，没有“最新论文已全部覆盖”的主张。

## 迁移与最小判别设计

对象映射：同一层/头、同坐标的协方差C_old=A，更新C_new=B，旧正交子空间P。保留的是对称算子、投影与块谱排序；不是原始K一定对称，也不是RoPE频率可任意融合。β只传播为相同q,k下|q^T(Pnew−Pold)k|≤||q||||k||β。它不控制舍弃补空间误差、near/far分区变化、softmax输出、V相关性或e2e准确率。

候选RES-H001：跨块扰动小且块谱分离时，复用旧投影可以少做重建，同时保持预先指定的投影分数误差。可证伪：在已认证h与范数上界下，观测投影误差超过β，说明实现、对象或证书至少一项错误。先锁定开发矩阵与误差容限、测证书/全重建/只看总范数三组，然后独立验收证书和计时，再冻结未用于开发的真实trace；同模型工具预算比e2e后才决定接入。费用、收益与真实模型可用性均未知，当前inconclusive，不改生产。

跨领域：固定正定质量M、对称刚度K的无阻尼振动，在同一质量坐标构造A=M^(−1/2)KM^(−1/2)。P可表示模态簇；块扰动若不耦合模态簇且频率平方不穿越，簇子空间保持。g、h、E的单位s^(−2)，角度无量纲；M变动导致坐标变化时不能直接比较，阻尼非对称模型也拒用。仅方程映射，无物理实验。

## 无定理名问题与验证状态

- “矩阵改动很大为什么方向没变？”抽取正交投影、跨块是否为0、块谱排序，标量平移例回应；不因总范数界失败自动重建。
- “两块之间没耦合，为什么主方向换了？”检查排序穿越或边界平局；交换只保证不变性。
- “两个库给不同基，是压缩信息变了吗？”比较投影/主角度并查外侧谱隙；内部换基不等于子空间变动。

上述均为公开手工结构检查，不是实测模型检索、未见题或原论文复现。没有CPU实验、Lean形式化证明、GPU或token测量。独立文档审查只核对来源、一般推导和解析反例。下一步需认证浮点范数/谱端点和完整trace条件，避免经验估计冒充证书。主游标和MATH-65暂停保留。
