# 分块 softmax：可合并的统计量与不能省略的边界

ID: `candidate.softmax-block-merge`；版本1；状态：document-candidate，普通文档审核状态见绑定证据，不构成实验验收。检索日期2026-10-10。本文是按需加载候选，不进入生产知识索引或增加Skill；没有模型/GPU/CPU实验、Lean或未见验收。

## 1. 为什么只传局部 output 不够

面对“两个worker分别返回平均值0和10，要怎样合并？”先问它们各自代表多少未归一化权重。权重9与1时结果是1，等权平均是5；相同局部output也可配其他权重而产生不同结果。局部softmax把分母除掉了，无法从output恢复全局attention mass。near/far也一样：分区大小、max logit与概率总质量是三个不同对象。

这里解决的是**同一个固定attention row的分片合并**，不解决如何快速找到各层最优alpha/beta/gamma，也不保证分片检索覆盖完整支持集。与MATH72的输入条件化策略候选、已有`math.softmax-barycenter-error@1`（knowledge_ref复合sha256（metadata+content）`269f488663b18bde24bac5f9d15121d5b589d06c0b1e16b2ad82430d6de5f160`）的保留质量/输出误差关系衔接；后者不是合并算法证明。

## 2. 数学对象和准确前提

固定有限非空合法token集合J，有限实logits s_j，固定value v_j∈R^d；temperature、qk scale、位置变换、bias都已计入s。J被互不相交的块B划分，允许空块。所有worker计算同一query、同一head/value坐标、model/cache版本和合法mask；块集合的完整性、唯一性由调用协议保证。

非空块统计量

\[
m_B=\max_{j\in B}s_j,\qquad
\ell_B=\sum_{j\in B}e^{s_j-m_B},\qquad
u_B=\sum_{j\in B}e^{s_j-m_B}v_j.
\]

在实数数学中1≤ell_B≤|B|，u_B可以有负分量。局部output o_B=u_B/ell_B，自然对数LSE z_B=m_B+log ell_B。全局y=u_J/ell_J。logits、ell、z无量纲，u与v同单位，y仍与v同单位。

## 3. 合并定理与自足证明

对非空A、B，令m=max(m_A,m_B)，a=exp(m_A−m)，b=exp(m_B−m)。定义

\[
(m_A,\ell_A,u_A)\oplus(m_B,\ell_B,u_B)
=(m,\;a\ell_A+b\ell_B,\;au_A+bu_B).
\]

这是**本候选的自足实数推导**；normalizer二元运算来自来源1 §3.1式(4)，加权value扩展和下面的边界显式证明，非新颖性主张。

对互斥块，把a乘进各项得a exp(s_j−m_A)=exp(s_j−m)。因此新ell、u逐项正好是A∪B在共同max下的和。三块无论先合并哪两块，最终max=max(m_A,m_B,m_C)，ell与u都重写为三个原统计量乘exp(m_i−max)后相加。实数加法结合与交换，所以merge结合、交换；同理任意有限分片归约。这给出了语义不变量，而不是仅用几个样例证明结合律。

另一个可复核表示是非空state↔(m,Z,U)，Z=exp(m)ell>0、U=exp(m)u；merge就是(max,+,+)。此表示只用于实数证明，**不要在浮点实现中真的计算exp(m)**。

重复输入也能按多重集合合并，但它等价于给重复token增加权重，不再是原来J的attention。数学运算不检查token身份。全体token复制同一倍数只改变Z不改变y；局部不均匀重复通常改变y。

## 4. Empty identity、LSE接口与数值语义

推荐用显式empty标志E。定义E⊕S=S⊕E=S，E⊕E=E；只有非空state才进入指数公式。空state可在存储上写(-inf,0,0)，但不能盲算max(-inf,-inf)后exp(-inf−(-inf))；IEEE会产生NaN，即使随后乘0也不会自动修复。全部块为空时y未定义；库若约定返回0必须标注为接口约定，不是softmax定理。非法位置从J删除，不能把-inf当有限logit；NaN/+Inf不在定理域。

若接口返回(o_B,z_B)，非空块可合并：令z=logsumexp(z_A,z_B)，rho_A=exp(z_A−z)、rho_B=exp(z_B−z)，y=rho_A o_A+rho_B o_B。多个块同理。empty必须先branch，不能仅靠z=-inf在全空时自动成立。

如果kernel返回log2 Z，那么权重必须用exp2(z2_B−z2)，或先乘ln2换自然对数；若score预乘log2(e)且用exp2，审查整个单位链，不能把名字LSE当单位证明。若wire返回的是u而不是o，消费端必须走相应三元公式；字段名字output不能证明已归一化。

实数结合律**不意味着浮点bitwise结合律**。即使所有logit为0，单元素value=(10^16,−10^16,1)，IEEE binary64、round-to-nearest/ties-to-even且每次加法单独舍入（无fast-math重关联）的三元merge中分母都准确为3，分子(10^16+(−10^16))+1=1，而10^16+((−10^16)+1)=0；输出分别为1/3和0。这是公开解析开发反例，未运行CPU，不是某kernel的实测bug。

max平移控制exp正方向溢出，但不保证所有精度：sum可能舍入/溢出；差值本身可能溢出到-inf；小指数可能下溢；u可因大value溢出或抵消。论文对normalizer的“safe”不能提升为任意value输出的统一误差证书。特别是全局权重epsilon=exp(−1000)，value exp(1000)，真实加权贡献量级1；不能因epsilon很小就丢弃块。有限实数允许此例，目标dtype却无法表示该value，必须拒绝数值套用。实际机器误差需声明可表示范围、exp/sum/乘法误差、归约树和dtype，不能仅要求结果非NaN。

## 5. 公开开发验收题与跨域迁移

下表不向模型提示定理名；答案由本文解析检查，不是模型检索/拒用能力实测。公开后不得再作为未见测试。

| 问题结构 | 正确处理/可证伪结果 |
| --- | --- |
| worker A输出0、未归一化权重9，B输出10、权重1 | 全局1；直接平均5错误；只有output不足辨识 |
| 先分三个块再换归约树 | 实数表示一致；浮点逐项比较误差及dtype，不要求无条件bitwise相等 |
| A权重9/value0，B权重1/value10，A被重复一次 | 变为10/19；拒绝“merge可交换所以重复无害” |
| 上例丢B，或每块仅返回代理候选 | 只认证已保留并集上的归一化；输出0且无法推回完整mass |
| 两个worker都没有合法token | 显式empty；全局softmax未定义，不执行-inf减-inf |
| 不同head的output维数恰相同 | 坐标/语义不同，拒绝合并 |
| 离散Gibbs模型按微观状态分片 | s_j=−E_j/(k_B T)，T>0；v_j为同量纲可观测量，得到全局期望；温度不同的分片不可混合 |

Gibbs迁移保留指数权重、partition function及线性观测均值，能量/热能比无量纲。有限集合和同一Hamiltonian/温度是成立条件；不覆盖无限状态极限、积分求积误差、非遍历抽样或相变。此处不是把“文件重要性”当热能，不能据此删advice或授权重排生产任务。

## 6. near/far与多机调用契约：仅推荐验证

若完整合法J=N⊔F，near/far各算真实统计量，p_N=exp(z_N−z_J)，y=p_N o_N+(1−p_N)o_F（两块非空；空块按上节分支）。可以继续把F拆给其他worker并merge。若far method只捞取F'，最终得到的是N∪F'的attention，不是原全J；除非还有完整剩余统计量或经过核验的误差证书。用candidate自身分母估计“far总质量”无效。

建议每条partial携带request/query/head/layer ID、model与KV generation、position/mask/score版本、完整声明的token索引集合或可核验分片manifest、statistic类型、dtype、exp/LSE基底、empty状态、partition唯一ID。接收端核对预期分片集、去重同一结果/重试attempt、确认完成后再归约；同partition的两attempt不可当两块相加。hash只证明绑定字节，不证明mask合法或数学正确。这里是规范建议，没有实现或真实消息路径验证。

量纲正确的payload估算：每query/head三元统计量是d个u分量加2个scalar；(o,z)是d个output加1个scalar，加实际metadata。通信与kernel、队列、同步、重传共同决定速度。统计量是充分的，并不证明移动query比移动KV更快；必须在相同模型/数据/形状/质量和总开销口径下比较。

最小后续实验（当前未执行）：固定源码SHA、kernel参数/软件/GPU拓扑、dtype/位置规则；公开有限fixture先检验身份、empty、log基底、分片重组，再独立CPU高精度参考及真实GPU 1/2/4/8分片对比单次完整合法mask调用。覆盖同/不同max、极端有限logits、value抵消、all-empty、partial-empty、scattered选择、重复/遗漏、cache换代与重试；报告绝对输出误差与原参考value尺度，近零输出不用相对误差单独判定。确认性容差先由实际dtype/范围与任务允许误差确定，不能看过失败后放宽。任何身份/支持集不一致立即失败；数值超阈值保留负例并停止速度解释。最后才在完整链路测通信+调度+kernel+merge+同步总时间和模型质量，对照同预算最佳静态逐层配置；局部枚举oracle仍仅诊断，不能靠正确merge宣称参数求解器有效。保留另一套未用于开发的实际模型/拒用验收题。

## 7. 来源筛选、采用与限制

1. Milakov、Gimelshein，*Online normalizer calculation for softmax*，arXiv:1805.02867v2，2018-07-28；[记录](https://arxiv.org/abs/1805.02867)、[原文](https://arxiv.org/html/1805.02867v2)。已读§3 Theorem1和§3.1式(3)/(4)：给在线normalizer及二元并行merge。作者省略结合/交换证明，本文补足；未把2018的V100性能移植本项目。adopt基础代数，adapt显式empty和value边界；当前来源未核实另有正式出版。
2. Ma等，*Move the Query, Not the Cache: Characterizing Cross-Instance Latent and Sparse Attention Redistribution Across GPU Fabrics*，固定arXiv:2606.01502v1 HTML标2026-05-31；[原文](https://arxiv.org/html/2606.01502v1)。已读§3.2/3.3/4.1–4.3：作者用partial statistics跨设备重组，报告有限数值误差，并把成本拆为probe、transfer、compute、return、merge。HTML含Journal:TACO元数据，但没有核实正式接收/DOI；abs访问报错，latest-version未知，只绑定v1。defer系统采用；不把文中exact/bit-identical的有限测试解释为所有浮点归约都相等，不采纳其绝对延迟/倍数作本机数据。

截至本轮，没有新生产能力提升证据，也没有确认SGLang最新源码bug。真正新增的是合并前提、完整证明和可拒用边界的按需候选。数学推导经普通文档审核后只标derivation-reviewed；不标Lean/一般浮点认证/模型实测通过，不更改既有MATH65失败与预算状态。
