# 用softmax挑配置：熵正则解不等于原始代价最小解

稳定ID：`candidate.gibbs-regularized-menu`；版本1；document-candidate。检索2026-10-10；审核状态见绑定证据。仅按需文档候选，不增加常驻上下文/Skill，不加入canonical生产索引。未做CPU/模型/GPU/Lean/未见实验。

## 1. 对象、符号与准确命题

固定非空有限动作菜单A，M=|A|；每个动作代价c_a∈R有限、同单位，tau>0也有代价单位。q是A上的概率，H(q)=−Σq_a log q_a，log为自然对数、0log0=0。动作在此是**完整配置或完整联合分配**，不是自然语言句子；c可为预先定义的任务损失、延迟或显式标定的标量目标，不能直接把ms、token和准确率相加。

定义Z_tau=Σexp(−c_a/tau)，p_tau(a)=exp(−c_a/tau)/Z_tau，G_tau(q)=E_q c−tau H(q)，F_tau=−tau logZ_tau。有限菜单使Z有限正、p各坐标严格正。

经典Gibbs变分原理的有限形式：

\[
G_\tau(q)=F_\tau+\tau D(q\|p_\tau),\qquad
\min_qG_\tau(q)=F_\tau,
\]

唯一最优q=p_tau。**这是带熵奖励的目标G最优，不是原始代价E_q c最优。** 原始代价的最小值c*=min c由支持在最优动作上的分布达到；有非最优动作且tau>0时，p_tau的原始代价严格大于c*。

推导自足：log p_a=−c_a/tau−logZ，把它代入Σq log(q/p)，用Σq=1得到等式。KL≥0的有限证明见实际读取的`math.support-conditioning@1`（knowledge_ref metadata+content SHA256 `4358cbb6785d8b709037d448a5738354be5134ce8f64127931430f3d39f186fd`）：log t≤t−1；等号需q=p。也可由Σq log q严格凸证明唯一性。此处没有连续空间/非正规化先验/负温度扩展，也不是新定理。

## 2. softmin、平均代价和温度的三个不同量

因为exp(−c*/tau)≤Z≤M exp(−c*/tau)，

\[
c^*−\tau\log M\le F_\tau\le c^*.
\]

这是softmin的下偏区间。平均代价mu_tau=E_p c则满足

\[
0\le\mu_\tau−c^*\le\tau\log M.
\]

证明：取一个最优动作的delta分布作为G比较器，其H=0、G=c*；G(p)≤c*，所以mu_tau−c*≤tau H(p)≤tau logM。上界通常不紧，不把softmin F当执行动作后的真实代价。M=1时二者都精确为c*。

固定c、菜单和均匀计数基准，有限项可逐项求导。dp_a/dtau=p_a(c_a−mu)/tau²，故

\[
\frac{d\mu_\tau}{d\tau}=\frac{\operatorname{Var}_{p_\tau}(c)}{\tau^2}\ge0,
\qquad
\frac{dH(p_\tau)}{d\tau}=\frac{\operatorname{Var}_{p_\tau}(c)}{\tau^3}\ge0.
\]

第二式用H=mu/tau+logZ，dlogZ/dtau=mu/tau²后抵消。菜单全等cost时导数0，否则tau>0严格正。tau↓0时p集中到全部最优动作并在它们间均匀，mu→c*；tau↑∞时p→全菜单均匀。改变输入、模型或cost代理时，不能套此固定c单调性。

若r个最优动作，且M>r、每个次优cost至少c*+Delta（Delta>0），令S=Σ次优exp(−(c−c*)/tau)，则

\[
\Pr_p[\text{次优}]=\frac{S}{r+S}
\le\frac{(M-r)e^{-\Delta/\tau}}{r+(M-r)e^{-\Delta/\tau}}
\le\min\{1,(M-r)e^{-\Delta/\tau}/r\}.
\]

没有正gap不能宣称“指数消除错误”；抽样次优概率与模型任务失败率也不是同一对象。

## 3. proxy误差、菜单重复与先验

若全菜单逐点|chat_a−c_a|≤epsilon（同单位），用chat产生p_hat，

\[
E_{\hat p}c−\min c
\le 2\epsilon+\tau\log M.
\]

因为E_hatp c≤E_hatp chat+epsilon，E_hatp chat≤min chat+tau logM，min chat≤min c+epsilon。这个误差界必须覆盖全部动作，且包含真实决策时可得proxy；不是自动从训练MSE或局部layer oracle获得。若有正gapDelta且Delta>2epsilon，真实最优组与次优组在proxy上仍相隔至少Delta−2epsilon，可在上一节概率上界代换该gap；组内proxy可打破原tie，分母只需r个真实最优的proxy权重下界，仍能得保守(M−r)/r倍率。若Delta≤2epsilon，低温可能更确定地选错；降tau只减熵偏差，不消除代理误差。

均匀计数softmax依赖动作表示：一个bad动作复制N个别名会增加该行为总概率。cost=(0,1),tau=1，一good/N个bad时bad概率N/(e+N)，可随N趋于1。去重的是物理等价行为而不是擅自去掉独立候选或advice；等价性需核实输入/接口/效果。有限M理论不自动保证选择器对菜单编码不敏感。

可以显式指定先验r_a>0、Σr=1，用E_q c+tau KL(q||r)；唯一解p_a∝r_a exp(−c_a/tau)。对一个最优动作a*的delta比较器，原始代价差≤tau log(1/r_a*)，选r mass最大的最优动作可收紧。r_a=0会永久排除该动作，即使它真实最优；不能再拿全菜单min c作免费可达基线。复制别名若分摊同一行为的prior总质量才可保持行为级分布。均匀prior的KL目标与−H目标只差常数tau logM，最优分布相同，但F数值不同。

## 4. 物理对应与不能套用的地方

有限能量E_a、同一温度T>0，tau=k_B T（能量单位），cost=E，对应canonical Gibbs/Boltzmann分布。H是无量纲nats，物理熵S=k_B H，G_tau=平均能量−TS。固定V,N的canonical平衡自由能通常称Helmholtz自由能；来源的“Gibbs free-energy functional”是变分函数名，不能据此把它与固定压力的热力学Gibbs势混为一谈。

两能级(0,Delta)的高能态概率=1/(1+exp(Delta/(kBT)))；低温向低能集中。这里保留指数加权、partition sum、能量/热能无量纲及变分关系；不证明实际冷却动力学到平衡、有限时间采样混合，也不覆盖无限状态数/相变/连续微分熵。Agent温度只是同单位正则系数，不是真实设备温度，更不能从降低熵推出推理能力或系统质量提升。

## 5. 公开无定理名验收题与拒用反例

所有答案是解析开发检查，不是已运行模型/CPU实验。公开后不再作为未见测试。

| 新问题的结构描述 | 解析答案与边界 |
| --- | --- |
| 两方法cost0/1，以exp(−cost)抽样，为什么指标报负而平均cost为正？ | F=−log(1+e^-1)<0；实际cost=1/(1+e)>0。报告混了两个目标 |
| 把cost1方法复制N份，系统更可能选它吗？ | bad=N/(e+N)，是基准测度变化；不能说softmax仍代表行为均匀 |
| true=(0,1)，proxy=(1,0)，令tau很小 | proxy确定选择true-cost1；epsilon1，误差界保守有效，低温不纠正排序 |
| 单作业memory2/4，硬上限3；两个同loss方法均匀抽样，期望memory3 | 超限方法概率1/2；平均预算不是每次可行。需先排除memory4 |
| 两worker各在两张卡中选一张，每张只能一个作业 | 各自均匀选择会以1/2概率碰撞；必须动作表示为可行联合assignment或有真实资源预留，局部可行不是联合可行 |
| 分布softmax(0,theta)，均匀prior，theta→∞ | KL=log2−H→log2有限，参数无限而KL关于theta不具有径向无界性；不能套连续动作论文的径向无界结论 |
| 化学/物理两能级按热平衡分布混合观测 | 两态式成立，E/(kBT)无量纲；不同T或未知非平衡轨迹拒用 |

不接受仅有“熵下降”“softmax最优”“温度趋零”“梯度变小”“收敛更快”等表面特征作为质量证据。没有真实同单位cost、共同菜单/支持与目标，只有类比，不启用生产策略。

## 6. 逐层参数/多GPU任务选择的有界迁移建议

在一次固定输入决策中，a可以是各层(alpha,beta,gamma,method)的**完整联合表**；先由逐点可核验的资源/quality约束生成非空可行菜单，再确定真实端到端目标c_a与proxy。局部layer误差可用于特征或诊断，但不等于全模型c；PP stage makespan、通信竞争、多层误差/队列会耦合。菜单包含未知cost时，上面的epsilon证书不能成立。最优联合配置不等于逐层各自最低proxy的拼接。

若true cost已准确知道且唯一目标是本次平均cost最小，直接argmin已有最优性，有限tau Gibbs没有该目标下的优势。Gibbs可能用于新实验的探索覆盖或另行授权的稳健正则目标；收益必须算入探索/校准的总成本，不能换目标后声称原目标获益。若head/topk只是内部attention权重，不是动作抽样，E_q c并不自动对应最终输出质量，需另建几何/端到端映射。

最小后续验证（当前未执行）：固定模型/trace/decision时刻、完整菜单与重复等价规则、quality与硬资源约束、统一loss/单位及校准/heldout划分。冻结proxy后，对照best uniform static、best layer static、输入条件argmin proxy、feasible Gibbs；同时保留完整菜单oracle作可达诊断。先判所有真实抽样动作可行，再记录真实loss与误差、proxy全动作误差、temperature sweep、重复别名/先验压力测试、选择及校准/重试/通信总开销。每个预算下报告平均任务loss、失败/越界率和总成本，禁止只报正则F。阈值须在看到数据前依质量目标/测量误差固定；任何硬越界失败，proxy反序/差于静态保留负例。未有同模型/同工具/同预算实测收益之前defer生产采用。

## 7. 来源、阅读范围、采用与验证等级

经典：Mézard/Montanari，*Information, Physics, and Computation*，[作者书页](https://web.stanford.edu/~montanar/RESEARCH/book.html)确认2009 OUP；本轮实际读[Part A作者draft](https://web.stanford.edu/~montanar/RESEARCH/BOOK/partA.pdf)，页脚2007-11-09。§4.4，印刷79–80/PDF79–80页，式4.42/4.43、Proposition4.13给变分函数与KL恒等式。绑定draft页码，不称正式版页码；其后连续例未采用。adopt有限变分结构；tau/menu/proxy/gap/alias边界以上自行推导，并非来源的Agent性能主张。

近期：Chen、Šiška、Szpruch，*Global linear convergence of entropy-regularized softmax policy gradient beyond tabular MDPs*，[arXiv2605.24939v1](https://arxiv.org/abs/2605.24939)，2026-05-24；截至2026-10-10官方记录只列v1，无已核实正式发表信息。[相关原文](https://arxiv.org/html/2605.24939v1)intro及Assumption1/2、Theorem2：研究log-linear policies与regularized gradient flow；可实现性和feature/measure前提是结论的一部分。其Assumption2要求每个方向最大化集的mu质量为0，在有限全正离散菜单中不成立。defer迁移其radial-unbounded/linear-convergence结论；不把gradient flow换成实际SGD或主AI任务调度，也不把regularized objective收敛当原始任务质量提升。

数学证明/解析例与物理单位只经普通独立文档复核；无形式化、数值运行或模型验收。实际knowledge检索记录显示词法entropy误命中，随后按finite KL结构读取准确卡，不能把相关度当适用性。近期筛选与经典补全各有边界，未改已有SGLang代码、canonical计数或MATH65暂停状态。
