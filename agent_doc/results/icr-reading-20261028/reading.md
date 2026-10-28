# ICR：通信的纠错、保真与收益归因

2610.01042v1，*Beyond Final Accuracy: Auditing Communication in LLM Multi-Agent Systems*，Shixuan Li、Wei Yang、Peiyu Zhang、Anzhe Cheng、Heng Ping、Paul Bogdan。2026-10-01 04:34:59 UTC 提交。[正文](https://arxiv.org/html/2610.01042v1) · [版本](https://arxiv.org/abs/2610.01042v1)。本记录是同一 SYSTEM-99 / Plan54 的阅读检查点，不是整轮优化完成或本库性能结果。

## 实际范围与证据

2200检查点已读正文§§1–5、A/B、部分C、E/F及G开头；2300续读C.1/D及G–J，合计正文与附录A–J。主文Tables1–4、附录Tables5–24、Figures1–4图注；未查看PDF/渲染图、作者代码和原始逐题结果，未复现模型或统计实验。完整精确文本范围及SHA见inputs.json；参考文献只作导航，不充数。两次读取合计同一篇，独立复核与公开回读完成后才由30增至31，旧论文不重计。

## 方法与成立条件（§3，A/B）

- ICR先让三个agent互不观察地独立解题，冻结初始推理、答案和通道所需表示；每题六个有向sender→receiver组合均从原始记录开始，不传播修订结果。独立生成不意味着错误统计独立；这是单跳审计，不能代表多轮任务恢复。
- CR条件为接收方初错/发送方初对，PR为接收方初对/发送方初错；SR为双方初错后的恢复，SCR为双方初对后的保真。SI=(CR+PR)/2赋予两类混合状态相等权重，不直接测内部辨真能力。仅在混合方向分母相等时，其准确率等于SI；全体准确率还依赖四类初始状态权重。发送方答案正确也不保证消息所有论据正确。
- No Message仍让接收方再推理，区别于不修订的Keep Initial。按相同题目/有向对将通信结果与No Message配对，分别保留gain与loss，净差为(gain−loss)/N；两者都需要报告，不能只算救回的错题。
- 比较通道时冻结初始记录、receiver模型和策略；比较receiver策略时保持该通道的消息和传递接口。正确标签仅用于离线选择、分层和评分，不传给构造消息或修订模型。后验选择的审计人口与部署分布仍有差异。
- Full Text发送去除thinking后的完整response；StateBridge通常用末尾至多64个hidden states，经同轨迹Procrustes拟合/归一与词嵌入插值，缺thinking标记时有回退；LatentMAS重建包括thinking的全轨迹KV前缀并做10个latent steps。信息、接口及计算均不同，是机制适配，不能当原生系统复现或纯表示消融。

## 实验、对照与负结果（§4，C/D，F，I/J）

Qwen3-4B主文四数据集共有430个至少一名agent初错的问题、2580个有向事件；Answer Only只测混合方向，其他主文条件测全部保留方向。Qwen3-8B仅在MedQA/GPQA-D测混合方向，每类分别92/108个事件；两模型人口由各自初始结果决定，不可跨模型配对。HumanEval+为附录28题/168方向，每类CR/PR仅28个事件。

| 对照 | 原文结果与本次取舍 |
|---|---|
| Full Text vs Answer Only | 四主任务CR点估计升11.96–41.84pp、PR降15.79–37.93pp。配对区间中三个任务CR增加排除0，GSM8K下界为0；四个PR下降区间均低于0。四个SI差异区间都含0，不证明等价或“全文更好”。 |
| 相同No Message参照的得失 | MedQA Full Text为86gain/75loss/720事件，净+11；GSM8K为40gain/45loss/564，净−5。StateBridge等也有不同得失，不把更高CR直接当净任务收益。 |
| Structured Verification vs Critical Evaluation | 两任务各通信通道均CR降、PR升；MedQA StateBridge SI−6.47pp、LatentMAS+9.91pp，区间分别严格负/正；GPQA-D三个SI差异区间均含0。MedQA LatentMAS相对策略各自No Message的增量变化+11.21pp，区间[2.16,20.26]；其余该增量变化未排除0。不能全局替换接收策略。 |
| 随机传递参照 | 用既有Full Text/No Message结果的期望混合，拟合alpha匹配Answer Only的PR，不新增生成或逐题选择。四个匹配后CR差异区间都含0；不能证明低曝光机制或等价。 |
| 通道×策略 | StateBridge−Full Text的SI排序点估计随策略变化，但两任务交互区间都包含0（MedQA上界0）；不能用排序翻转宣称已证交互。 |
| HumanEval+ | Full Text CR21/28对No Message16/28，PR均26/28；StateBridge CR19/28、PR27/28。主文“所有通信降低PR”不适用于此代码补充集。LatentMAS CR24/28但PR17/28、SI低于No Message，保留伤害。 |

D.1将答案身份按Invalid→Prior→Sender→Third互斥分类；同时匹配双方时归Prior。Sender匹配不是因果采用，No Message也可能碰巧相同；程序字符串相同/不同不代表功能等价。valid-output change排除无效修订，但保留初始无法解析后变为有效的记录；不能将该分母与全体任务成功率混用。

## 统计、来源与可复现性限制（A/C/G–J）

1. 4B主文Acc†是全量估计：保留人口实测，加部分all-three-correct方向实测，再把其经验准确率外推到未观测方向；MedQA StateBridge没有该类观测，原文Table15仍给出估计，不能补造成实测。8B则假定所有未测方向保持接收者初始正确性，两种外推假设不同。早期A↔B两方向样本和GPQA中断采集没有记录为概率样本，G明确不报其置信区间；GSM8K各条件样本235/233也不全匹配。
2. 主对照配对区间用10000次question-cluster bootstrap；C中4B边际区间用2000次，J中8B边际10000次。共同保留每题相关方向/条件，六方向不是六次独立复现；不从边际区间重叠推断显著，不捕获未观测生成种子变化，含0不证明等价。
3. GPQA初始截断敏感性排除9题，CR/PR分母114→100，所有SI下降，LatentMAS落到No Message以下。I.5按六个condition×policy中的任一修订截断联合排除6事件后，两类各111；所有所报对照区间含0。该选择依赖修订后的结果，只描述选定子集，不替代保留全事件的主分析。
4. 生成上限在采集中从2048/4096/8192提高到16384，已正常终止的旧输出保留；八条修订仍在早期上限截断。种子按run/题/agent或方向派生且不含condition/policy标签，但未强制GPU确定性。重建prompt哈希和配置映射不等于全部历史源码快照可得。
5. MedQA使用本地300题，原选择过程/源题ID不可得；GPQA选项重排过程不可得；三个Hugging Face数据集重建loader哈希匹配仅支持该范围。无记录的独立题级开发集。ARC-C七个非四选项结构排除与正确性选择分开记录，不宣称盲测泛化。
6. 评分解析规则各任务不同，unparsed判错，非EOS与unparsed可重叠。HumanEval+用数据集test字段、独立子进程每题10秒全测试时限，未用官方EvalPlus harness；串行复跑改变一题正确性，报告仍保留原分数/初始分层。不是已经可靠复现的真实软件任务质量。

## 费用边界（E）

Table13只是记录的单条接收生成均值，各run并发/竞争不同；不能据秒数排名推导吞吐或加速。prompt token不包括全部latent-prefix计算，零额外构造generation call不等于零forward计算。StateBridge对齐时间计在初始阶段，构造计时不齐；LatentMAS导出payload=0与KV传递矛盾，作者明确当不可得而不报零通信。本库未测全输入、全角色费用或真实任务收益，不能把该表当成本基线。

## 与本库的关系与决定

静态核对communication.py：consume_handoff重新校验引用、绑定解析manifest和独立consumer请求及当前basis；ACK独立且不可覆盖，仅记录处理，未授予任务完成。impact报告已验证交接的受影响者，不自动发更正或继续任务。分页不会过滤correction，但不证明全局无待办；语义依赖完整性、权限/租约/取消、消费者所有权和外部动作幂等仍由宿主负责。通信工作流已要求保存返修意图、先publish再ACK且明确非原子；未确认需修的新缺陷，未增加第二实现。

采用为后续评价设计依据：冻结独立初始产物，同条件比较定向任务包与完整消息，保留No Message修订对照，同时记录纠错/正确信息损坏、配对得失、依赖覆盖及最终任务质量。适用前提是有可信完整输入、独立结果验收及全角色成本证据；这不是新实验执行许可，旧耗尽门禁不重置。

暂缓默认全文转发、统一验证prompt、latent传递、共享聊天池或删历史；论文没有提供对本库原位改动的已测收益。恢复条件是符合现有授权/预算的新验证方案和可访问的原生宿主，不能用静态哈希或局部测试冒充模型行为证据。不迁移agent_doc或修改人类guide。

先查结果：2610.01042，max_scan5000，325目录，无命中但25个缺record错误，status=incomplete、partial=false；不是旧阅读不存在的证明，未复用实证数据。现有knowledge同主题查询只命中推测采样残差精确性，token分布校正不等同语义纠正，拒用、knowledge_refs=[]；保留实际查询快照。

本次无生产修改、测试或实验模型/后端调用；独立阅读/源码复核是另一真实AI调用，不能称零模型成本，全部角色tokens/费用未知。手工复核不冒充受信ReviewSession/原生质量验收，历史登记保持unknown/null。真实宿主、完整模型输入、任务质量、全费用及并发/恢复等SYSTEM-99未决继续保留。
