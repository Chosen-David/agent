# 全局注意力质量区间与near/far参数证书_by_gpt

日期：2026-10-09；任务 MATH-57。任务级候选 ID：`candidate.softmax-event-box@1`，非 published 知识卡，非新科研定理。已有知识入口与索引不变；本文件为按需加载的迁移附件。

本轮补齐的是“分数有界→全局质量有界→局部输出误差有界”的条件式链路。它不能证明逐层参数已经最优，也不能用 mass 取代论文的端到端质量与计时。

## 入口、对象与索引

| 学科入口 | 问题结构入口 | 按需读取 |
|---|---|---|
| 概率/数值分析 | 全集分母缺失、支持条件化 | math.support-conditioning@1 |
| 数值分析 | 内积分数包络、存储实数与kernel目标 | math.floating-dot-enclosure@1 |
| 线性代数/概率 | 剪枝后的归一化输出误差 | math.softmax-barycenter-error@1 |
| 本任务候选 | 分数盒、事件质量极值、区间阈值决策 | candidate.softmax-event-box@1（本文件） |

实际 search/show 返回的 ID/version/hash 和强依赖保存在 results/math-mass-box-20261009 的 knowledge_use、floating_knowledge_use、output_knowledge_use JSON。先对象/约束/目标，再加载必要条目；不要求把整个附件或语料塞入每个 Agent 消息。

取完整非空合法索引 J、非空固定集合 S⊆J；温度 T>0、缩放/bias 已纳入无量纲 logits z_i。假设每个合法 i 有有限实数区间 l_i≤z_i≤u_i，且所有区间针对同一目标。attention mask 的非法索引从 J 删除，不把有限大负数当严格零。集合必须去重；S随一次输入选择也允许，但使用此证书时固定当前S，并有覆盖该输入/全部所声称输入的有效区间。

定义 p_i=exp(z_i)/Σ_J exp(z_j)，m_S=Σ_S p_i，C=J\S。不能把候选集的分母替换进去。若旨在dense kernel浮点输出的质量，需要该kernel整段概率计算的误差模型；本节仅针对精确softmax(z)。

## 一般推导：盒上的尖锐质量范围

设 A_-=Σ_S exp(l_i)、A_+=Σ_S exp(u_i)，B_-=Σ_C exp(l_i)、B_+=Σ_C exp(u_i)。空补集时B_-=B_+=0。

\[
\boxed{m_-={A_-\over A_-+B_+}\le m_S\le {A_+\over A_++B_-}=m_+.}
\]

证明：A=Σ_S exp(z_i)>0，B=Σ_C exp(z_i)≥0，m=A/(A+B)。∂m/∂A=B/(A+B)^2≥0，∂m/∂B=−A/(A+B)^2<0。取S下端/补集上端取得最小，反向取端取得最大。因此对独立盒两个端点均可达，是只用这些独立区间时的准确极值。对真实q/k等相关可达集，端点组合未必可达；仍为安全外包，不能宣称真实最坏输入恰达此界。S=J则两端恰为1；S为空质量为0但无法在S内重新归一化，必须拒绝剪枝输出。

这是正线性分式目标的初等推导。Vertex-Softmax一般固定系数目标取c_i=1_{i∈S}时得到此特殊结构：两个系数组无需求解一般排序问题。假设区间已提供，一次全量聚合为O(|J|)，不是完整系统O(|J|)或实测加速；生成所有区间可能比稀疏attention更贵。

计算全局far质量只需把S换成F（F为位置定义的far，不是“低分token”）。near应保留位置语义；“mass密集”是被保留的重要性集合，可能位于near或far。不要为参数求解混淆两个分类。若F为空，far质量为0；若N为空且J非空，far质量为1。

## 正例、边界与拒用反例（符号推导，未执行实验）

1. 两个合法token，S={1}，指数权重范围w_1∈[2,4]、w_2∈[1,3]（logit端点为各数自然对数）。精确盒极值是2/5与4/5。这是代入所得解析值，非Python/GPU实测。
2. 只有候选S={1}被计算，候选内部占比始终1。遗漏键权重M>0时，真实质量1/(1+M)可任意接近0。没有遗漏项上界，不能输出非平凡下界；返回unknown或[0,1]，不把采样最大值作为确定性B_+。
3. 相关约束z_1=z_2∈[−a,a]，真实m_S恒1/2；独立盒给[1/(1+e^{2a}),1/(1+e^{-2a})]。盒宽是丢失相关性的代价，不是公式错误。
4. 即使m_S很低，所有投影value相同则输出误差为0；若遗漏value与保留value相距很远，小tail也会造成大误差。所以mass只是有明确value几何前提的充分代理，不直接排序e2e质量。
5. near/far分别使用自己的最大值平移后，不能直接相加两组指数和。例如两组各一token、z_N=0、z_F=c，两组独立平移的和都为1，错误得到1/2，而真实near质量为1/(1+e^c)。须用同一平移，或正确恢复相对尺度。

## 浮点证书：需要覆盖指数、求和及除法

选同一个有限存储标量a（例如max_i u_i），在实数中所有端点同时减a不改质量。减法也须向外；不能先把l_i−a向内舍入，再声称exp端点可靠。分数区间、shift、exp实现、dtype、FTZ、归约与除法均写入目标与实现版本。

假设已经有经过验证的指数外包以及非负求和外包，得到aL≤A_-、A_+≤aU、bL≤B_-、B_+≤bU（均为移位后量），aL,bL≥0。安全下界可取向下除法 aL/up(aL+bU)；安全上界可取向上除法 aU/down(aU+bL)，只在所用分母下界严格为正、端点有限且操作前提成立时计算，然后与[0,1]相交。aL=0时下界直接0；无法获得正分母下界时上界取1，而非0/0。空S或空C用已证明精确事件边界单独处理。若下溢，降低证书等级或使用有保证的高精度/log-domain外包；不可把被flush的正量当数学零。

CUDA13.2.0官方5.5.9列出定向基本运算，但指数内建函数的ULP表注明来自非穷尽测试、并非保证。因此“expf后补固定ULP”不能仅凭该表充当全输入证明；Python/PyTorch高精度也不是自动严格外包。可选经核验的区间超越函数参考实现、受限输入域的已证误差多项式或正式保证的库；本轮未实现任何一种。GPU算法可先做diagnostic，字段必须区分diagnostic/certified/unknown。

共同shift防溢出不解决任意下溢；更高precision不证明最终端点向外；单次测试没有越界也不认证全输入。此前内積包络不能自动穿过exp与归一化。

## 局部输出与逐层求解接口

对固定value v_i和固定线性输出映射W，D≥max_ij||W(v_i−v_j)||（同一范数）为有效上界。只在S内用原精确logits重新归一化，已有卡给

\[
\|W(y-y_S)\|\le D(1-m_S)\le D(1-m_-).
\]

若保留集内部还用代理logits、其误差振幅有界w≥max(t−z)−min(t−z)，可由三角不等式再加D tanh(w/4)。该附加项的分母/支持必须是同一S；实际浮点输出和value量化缺陷另加有保证的误差项。D无穷/未知，无法认证目标误差。局部界不等于深层传播或最终任务精度。

逐层alpha/beta/gamma方法组合应冻结原实现含义，不在本文件重新定义这些参数。每个组合先输出它真正保留的S_l、完整J_l、分数目标及质量区间。接口建议：target_id、mask/position/hash、layer/head/query、config_id、S_hash、mass_lower/upper、value_diameter_bound、local_error_upper、certificate_status/reason、measured_cost及版本。求解器只在certified且local_error_upper≤预设ε_l时允许“局部误差预算可行”；未通过不等于e2e差，只是此代理无法证明。

通过收紧区间、重算遗漏块或使用位置块统一上界来降低unknown；每次记录B上界来源和合法键数量。块上界u_b给Σ_block exp(z_i)≤n_b exp(u_b)，是保守聚合，不能把n_b漏掉。完整覆盖成本、残差读带宽与证书成本都纳入实验预算；太宽就回退全量，避免以强制稀疏冒充成功。

## 可证伪迁移与验收协议（未执行）

| 验收类 | 新问题/对照 | 应核验 |
|---|---|---|
| 不提示定理名 | 只知道两组打分范围，能否保证遗漏影响小？ | 检索support-conditioning，确认完整J，再推导m_-与D |
| 跨领域 | 多机传感器按无量纲log-likelihood归一化，只上报部分设备 | 同一softmax事件结构；物理读数不是logits，原始单位转换另核验 |
| 前提失效 | 候选far占比高，直接判全局far质量高 | 拒用候选分母；保存unknown与恢复条件 |
| 数值参考 | 小盒顶点穷举与有保证超越函数参考对照 | 每个真值落在外包内；近阈值、极端动态范围、空补集、FTZ专测 |
| 实际模型 | 逐层证书方法 vs 最佳全层固定配置、经验mass配置 | 同模型/工具/预算，记录候选比例、输出误差、任务得分、P50/P95及总时间 |

开发例固定并公开后不得继续称未见。另留冻结未读测试；真实模型校准和测评分离，不能用测试任务挑配置。数学拒用与自主模型检索需要真实模型调用，本轮只有文档推导与独立审核，未执行检索验收、GPU或新增回归。成本token未测；已有命令是搜索读取，不是省token A/B。

## 研究取舍与续接

2026-10-09核查Rezazadeh、Davoodi的[Vertex-Softmax v1](https://arxiv.org/html/2605.10974v1)，2026-05-08提交，原始abs仅列v1，正式发表未确认。读取Sect2/3、6与AppD。论文给一般固定系数的盒优化；本文只采用事件质量特例的自行推导，不声称首创。AppD明确普通PyTorch数值路径本身不是proof-carrying浮点证书。实验成绩和端到端证书均不迁移或复现。

[CUDA固定版13.2.0](https://docs.nvidia.com/cuda/archive/13.2.0/cuda-programming-guide/05-appendices/mathematical-functions.html)只用于核对算术边界，不宣称最新部署版本。来源阅读范围见sources.json。

adopt：完整分母、实数事件极值及失败回退；adapt：将逐层mass从经验标签改为带状态的区间接口候选；reject：用候选占比或观察ULP表认证；defer：生产实现、通用Vertex solver、模型/GPU收益。既有next_topic保持不变，先获得真实post-RoPE trace、合法全集和可核验指数参考，再判断是否值得提炼published知识卡或接入消费者。
