# MATH-37/38：单步概率偏差到序列分布

日期2026-10-08 Asia/Shanghai；基线main `7aa8f763438a73770394143aa389cf0704447428`。先同步最新main，读AGENTS、空只读指南、唯一TASK、角色及知识持续状态；旧运行均completed。prior-results.json记录实际先查旧证据：连续状态传播及相关算法结果不能替代本轮条件核序列数据，旧数字未复用。

## 本轮补齐什么

`math.sequence-tv-coupling@1`在有限共同词表、固定长度和真实条件概率核下，把单步分布误差映射到序列全变差。统一共享前缀TV上界ε_t给出`TV(P,Q)≤1−Π(1−ε_t)≤min(1,Σ ε_t)`；不要求时间独立。另用P前缀、Q后缀的混合分布推导`TV(P,Q)≤min(1,Σ E_{P前缀}δ_t)`。后者指真实参考前缀期望，少量任意teacher样本不自动满足。

对固定有界序列奖励，期望差不超过奖励跨度乘TV。这不是每条输出质量保证，也不是方案提升证据。最大耦合存在性不能保证实际相同seed的两个实现达到它；极小概率TV也可能翻转greedy的argmax，使确定性输出分布TV为1。单步最大耦合也不一定是整段最大耦合，项目证明只用它给上界。

条目给出有限共同质量/残余耦合矩阵、混合分布三角界、奖励界和`E_P(1−Q(X)/P(X))_+=TV`的可复核推导。零P支持在P采样比值中不求值，EOS使用共同吸收/padding规则，n=0、ε0/1、互斥支持和奖励跨度0都列为边界。一般证明为非形式化复核，数值实例未替代证明。

## 迁移到indexer的成立条件

原问题dense/稀疏完整执行器的next-token核对应P_t/Q_t，包括KV历史、logit处理、停止规则和随机执行；选token重合度、attention mass和隐藏状态误差都不是δ。上一轮连续传播界与本轮概率界各有输入，尚未自动打通。

可证伪最小实验：冻结prompt/词表/采样规则/horizon/method，dense采样轨迹上两个执行器replay同一前缀；捕获强制token之前的概率，并核对评分路径与生成路径、支持和截断归一化。若用轨迹比值身份估TV，还需独立样本、正确概率与数值稳定性；噪声oracle不能当精确oracle。实际置信区间另沿既有Hoeffding知识核查。之后分别测greedy稳定性、自由生成任务质量和wall-clock；分布接近不是任务指标的必要条件。

跨域例子为历史依赖通信/可靠性告警的整段故障事件概率；条件核与事件结构严格对应，但核是否描述真实物理机制尚需外部证据。无物理实验。真实模型replay、GPU和e2e对照均未运行，不部署新生产行为或改动SGLang。

## 验证、检索与成本边界

独立六项验收与真实宿主inspect_result均通过usable-with-scope。48棵树/504个联合词串/456个前缀耦合/1615次生产者断言经重算，原raw字节一致；独立递归、短树事件优化、相邻混合分布、三元耦合与跨度11奖励等额外核对见independent/。18项manifest绑定与182个语料文件完整核对。配置、源码、raw、环境和验收协议预先冻结。公开CPU二元概率树使用Fraction，穷举所有短序列、核对概率归一化、单步最大耦合的边际与失配、两类序列上界、轨迹比值身份和有界奖励。反例包括未测前缀、greedy翻转及EOS；独立检查另外计算同分布不同耦合、零支持/KL方向与奖励跨度边界。

三个人工结构查询不提示定理名称，分别是整段生成偏差、历史告警协议、相同seed误用，经现有files/sqlite领域检索。人工抽取不是模型自主提取前提或拒用测试。6次两后端检索均将目标列第一；完整真实show包为3903 cl100k_base tokens，计数见cost.json；不包含宿主总上下文/网页/回归开销，也不是账单或token节省。

当前所有案例公开，属于开发证据；holdout-protocol.json只保留后续未用文档/轨迹协议，未声明已经取得未见测试成绩。无Lean或形式化证明。CPU elapsed_seconds仅是本机验证信息，无速度对照主张。

## 经典与近期原文

[Powell Durham Stochastic Processes2021/22](https://www.maths.dur.ac.uk/users/ellen.g.powell/SPnotes.html) §3.2的有限TV/最大耦合公式与证明为经典基础；异质序列界、奖励展开与任务映射在条目中自足推导。两本教材PDF入口访问失败，未记为读过。

[Total Variation Distance Estimation in Autoregressive Models](https://arxiv.org/abs/2607.19510)，核查最新版v1，2026-07-21，定向读取§2.2/2.3 Lemma1、§3.1、AppendixB.5。原文区分样本/精确logit/噪声访问，并讨论评分路径与生成路径不匹配的测量风险。保留测量设计启发与有限比值身份；没有实现其查询算法、复用系统成绩或复现实验。正式发表未核实，按预印本记录。

[Autoregressive Learning in Joint KL](https://arxiv.org/abs/2605.12316)，核查v1，2026-05-12；定向读取有界log密度比Assumption1、KL链式和分解/共享类别区别。其学习理论有独立条件，不应套作任意稀疏推理或相同seed保证；不采用其新学习结论。正式发表未核实，按预印本记录。

访问日期2026-10-08 Asia/Shanghai（UTC2026-10-07）。这是与本主题有关的原始来源定向筛选，不是全文或最新领域穷尽。

## 接入与续接

复用model-with-knowledge Skill及原知识CLI；学科probability-and-optimization/information-theory，问题结构conditional-kernel/sequence-distribution/maximal-coupling/bounded-reward/support-mismatch。无新增Skill或运行时代码。

独立六项检查位于independent/；真实协作回执加冻结hash由宿主checked callback核对后才执行inspect_result和发布。直接有界宿主维护，不宣称tmux/受管Engine/ReviewSession部署。74项知识回归通过（11.546s）；回归见regression.log，同步见sync.log，发布证据归MATH-38和learning_state。

下一步仍优先真实trace/生成概率接口与未用文档，而不是把新条目数当能力提升。本轮没有可证明值得部署的生产性能改进。

普通main实现提交`0e78330baf3261e20744a36c3c7490c0d937ec55`已fetch读回，树`36d8a1364c9f3c3758084f2cd74b02d2610d180c`与本地完全一致；未force。验收范围保持不变。后续：实际生成路径一致的模型replay及独立留出对照。
