本次冻结原稿经一次独立手工静态审核accept，限实际阅读/源码范围；主控随后采纳两处非阻断编辑建议，无第二次复审。以下正文保留“初读问题→附录回答”的结构：历史尚待/待核查措辞现已由附录续读核查逐项回答，“无独立角色/独审待调用”均指复核前快照；当前实际审核1次。完整反馈和原稿SHA保留，不冒充可信ReviewSession、实测或生产放行。

# Sentry 2610.02994v1：正文及附录阅读与适用性

SYSTEM-99 / Plan54，同批续接。正文阅读2026-10-29，作者 Changxiu Ji、Amy Lu（equal contribution）、Qizheng Zhang、Kunle Olukotun，*Sentry: Learning to Recover from LLM Agent Failures at Test Time*。arXiv v1提交2026-10-02 08:26:47 UTC（版本页web读取），正文https://arxiv.org/html/2610.02994v1，版本页https://arxiv.org/abs/2610.02994v1。HTML声明CC BY4.0，未确认仓库代码/数据许可，不集成资产。

实际阅读：1858正文normalized [0,37600)，本次附录[43354,60500)、[60500,77500)、[77500,95000)、[95000,100022)。覆盖§§1–6、A.1–A.8、Eq1–2、Tables1–19和Figures1–4文字图注；References中间未读。100022字符不是token。PDF像素、作者代码/原始数据/完整轨迹未读，未复现作者实验。先前部分与本次只对应同一论文，独立复核/普通发布回读前新计数仍为0。

## 正文方法与限制（保留先读时问题，以下附录核查逐项回答）

- 每步先判action schema；不合法则hard repair要求替代action，检查schema和环境接受。合法action后才用最近W5 reasoning/action/observation判断progress或reasoning-grounding失效；无失效不检索。不是“模型认为可恢复即可忽略授权/取消”。
- soft repair从外部playbook选相同failure type且至少一共同label，labeloverlap排序、最多k5；无sharedlabel回退同type最近记录。附录A8.2尚未核查recency/labeldiversity/更新细则，不臆测闭包或精确标签算法。
- soft recovery H10后判断触发局部失效消失并恢复observationally-grounded进展，无benchmark reward/最终成功标签。只把判为恢复的soft episodes写为type/labels/trigger/principle。detector/retrieval固定，self-evolution只指playbook更新。same-model verifier不等于独立验收，局部恢复不是整个任务成功。
- isolation指完整playbook不作持久背景；检索fewlessons仍进入当次conversation。未见如何从整个历史去除旧injection，不把“只在失败时暴露”外推为历史中旧指导绝不再可见。待附录/代码核查。
- Qwen3.5-9B用于task/detect/verify，补GPT-OSS120B；默认50/100任务只采样一次，五run随机executionorder。5run SD不是新抽任务或统计总体CI，online memory跨任务因顺序依赖。online-from-scratch与held-out不是同一基线/暴露规模。
- Main online四benchmark：WebShop100 reward；AppWorld100 per-task check pass；SWE-benchLite50 officialharness issueaccuracy；Mind2WebReplay100按参考顺序已完成比例。Replay为作者交互改编：错误action留在reference state重试、candidateinterface共享，不是官方Mind2Web step指标或真实自由Web状态成功，不能跨metric把平均gain当统一质量。
- Table1 Sentry .468/38.53/.30/.736 vs各最强runtime baseline .264/27.56/.24/.687，作者报relative77.3/39.8/25.0/7.1%，均值约37%，不是37个百分点/统一成功率。完整系统含额外判断/反馈/重试/记忆，不能把全部增益归给检索或token缩减。
- Table2 held-out memory在50初始化，50disjoint scored期间仍按各方法继续更新，不是冻结memory的零适应迁移。Sentry .495/.729 vsACE .335/.562，relative47.8/29.7；ACE+Sentry .555/.789。Base .186/.421不同于Table1 .170/.420，不能跨表作配对因果对照。
- 检测到939failure中81.7%恢复（action92.6/progress64.0/reasoning70.2），是系统选择触发事件及自身verifier，不是所有真实failure召回/恢复率。人体校验200windows含触发和taskmatched非触发：intervention agreement86%、recovery agreement81.8%仅99softwindows，helpful85.8%仅113issuedinterventions，κ.82–.89；采样、盲法与模型误标分布尚待A7，不外推部署错误概率。
- 200soft-intervention checkpoints两branch同state，有/无guidance、之后都无进一步干预，局部恢复33.5→60.5%，最终得分74gain/101tie/25harm。此配对比ReCoF离线预测更接近干预效果证据，但checkpoint采样、detector选择、分benchmark、后续stochasticcoupling、horizon/费用和统计尚待A6.1；没有读取就不认证因果范围或独立200。
- Table3 online消融WebShop/AppWorld每项均降，缺soft .272/26.85、缺hard .297/31.20；无needcheck .136/23.70（WebShop低于Base .170），无selfevolve .295/28.90、无specificretrieval .316/31.05、无verify .343/33.50。精确variant实现/调用数/额外budget需A6.2，不用单变量名假定只变一个有效因素。
- Table4同frozenplaybook/repairsettings下，额外persistent fullplaybook使WebShop .364→.296、Replay .651→.599，差-.068/-.052。Noexternalplaybook .251/.533仍有detector+repair；Fullonlineupdates .495/.729不能与frozen差异仅归给“曝光”。不把两数据域均值降推成所有全量读取有害，不自动删本库必要更正/异议/依赖。
- label减少/随机retrieval下降和k3/10、W/H敏感性为作者报正文概述，细值/设置待A6.4/5；未把这些当本库hyperparameter最优值。
- Table5作者报input+output19.01M vs12.32M=1.54倍，非token节省；各场景时延差+7.12s/-45.61s/-31.73s/+46.04s，不能称全部加速。初始化、独立角色、缓存、硬件/采集范围/每run成本细节待附录，provider账单未知。参数更大模型只两benchmark，不能称跨任意能力/规模鲁棒。
- §6承认同model检测/验收依赖、其它领域泛化、playbook冗余或特异性累积，提出置信/合并/修剪是未来方向，未验证不照搬自动删除/晋升。

本库源码本次只读核查：maintenance_gate全文件；communication.py271–430和1–135；project_memory.py439–511完整index（一次输出截断，后用独立小块补全）；AGENTS与Plan前缀/guide/TASK版本另hash固定。Gate只有MaintenanceOutcome handled且前后fingerprint相同才ACK，pending/exception不ACK，quietlimit非deadline替代；恢复不归因于快照未变。mailbox分页含scope/hasmore/afterseq、read_pending SHA，consume_handoff仍须当前basis与消费请求，ACK另行执行；index省略正文但完整selectedsnapshot绑定，不保证语义相关集合完整。没有确认新的生产缺陷；这些静态范围不是实际宿主/完整质量/成本验收。

取舍pending：可继续比较“按当前失败选经验、真实局部恢复与最终质量分离、额外成本/伤害保留”的评价设计；**未采用新playbook、LLM诊断/验证、默认retry、记忆晋升/修剪或目录迁移**。现有MemoryLedger更正失效、basis门禁和唯一TASK继续权威，不能让AI判恢复产生user_confirmed或结果授信。

正式prior查询2610.02994 Sentry recovery lessons扫334目录partial=true/25errors，3候选combined-corpus delta-v2/v3/v4，冻结record SHA见raw。三者是知识语料集成，输入/任务/指标不匹配，拒绝作为恢复经验数据复用；partial查询/精确rg无Sentry原阅读命中均不证明全历史不存在。本次knowledge查询conditional failure recovery命中math.betting-test-martingale、math.fano-message-budget、math.frank-wolfe-output-solver；其固定条件均值/可预测下注、有限消息支持数、固定凸域与完整oracle前提未建立，拒绝用来认证恢复、token质量或调度收益，knowledge_refs=[]。快照767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18。检索只发现候选，不授信。

目前同批计数39不变。无生产修改、测试/作者实验复现、实验模型或独立角色调用、推送与性能结论；SYSTEM99及MemDerive/其它耗尽暂停门禁保留。本checkpoint为续读位置，不是第二任务索引或完成轮次。


## 附录续读核查

- A.3：任务采样前排除环境/依赖失败及缺标注，保留集合固定但缺排除清单/总体适用率，不能声称全部安装/任务可用。Replay使用Multimodal-Mind2Web test_task Cross-Task，按annotation_id聚合并target_action_index排序，排除无positivecandidate步骤。每步展示全部positive及最多30negative，以label选择click/type/select，operation和TYPE/SELECT值须匹配标注；错误留原reference状态并回传annotation-derivedfeedback，非任意真实网页状态。该oracle反馈共同提供给所有方法，提升不能外推为无goldfeedback部署。
- Shared task backbone/cap384tokens是可比约束，不是完整算力/成本相等。Wink每5actions看8steps，AgentForesight官方af54908逐candidate反复审计，AgentFixer每envstep最多一次再生，AgentGuard累积transition统计阈值和3重复；monitor频率/上下文/辅助调用不同，整体比较不隔离单一memory收益。Reflexion218cf0e、ACE82709de、AWM8c0ff8c、ReasoningBanked80611为论文给短commit，本次未核远端对象/实际代码，不能当本次源码锁。
- A.4：全部API为Together；task temp.7/cap384，aux检测/验证/更新temp0/cap4096，原文限额并未给本库可直接采纳的全episode调用/步骤/费用合同。五run同taskset、freshgeneration、随机order；并非五个独立held-out task抽样。ACE+Sentry两playbooks独立维护、不合并；不是共享聊天池。held-out时各自不同规则更新，frozenexposure两条件固定相同初始memory、order/detect/repair/retrieve/verify，只多persistent full背景，支持该受控比较，非所有任务全读均有害。
- A.5/T6–10：primarymetric均值与整数success/bought/guided/intervention诊断同列，计数跨run如何汇总未明确，不反算全部raw。Guidancelift对各方法自身guidedsubset，对照子集各异，不能作为方法间因果优势；SWE recovered #只是binary下guidedtask指标，不是全部错误被修。GPT-OSS120B只WebShop/Replay，表未列重复SD；两域结果不证明任意模型/领域迁移。
- A.6.1/T11：200fork同prestate/history，之后两边都禁进一步intervention，H10局部判据后都跑到termination。67/121恢复，其中only12/66；最终25nointerventionbetter/74Sentrybetter/101ties，必须同时保留伤害。分benchmark抽样量、是否同task多checkpoint/簇依赖、随机数配对、局部判据的盲法/裁判一致性、差值幅度/效用及时间成本未给；配对设计更强于观察相关，但不能拿200当200独立任务、忽略detector选择或外推总体净收益。
- A.6.2：w/o softrepair同时切断新memory来源，因此非只去掉一次指导；w/o selfevolve在empty-start下memory永远空；w/o verify仍等待同H后存episode，隔离准入筛选但memory内容/后续路径会随之改变；w/o needgate所有validaction scheduled监控点都指导，调用量本身改变；w/o specificretrieval忽略type/label，selection细则未完全给。原表降幅是这些组合效应，不宣称组件互相独立因果贡献或可省掉授权。
- A.6.3/4：冻结playbook曝光是唯一故意差异，但不等token预算/截断风险控制，额外内容就是处理变量，不能据此证明semanticconflict完全归因。label-filtered k5是同Table2完整Sentry .495/.729的rounded .50/.73，不误判两表矛盾。k3/k10只均值较低；表中四舍五入后的mean±SD范围在边界接触，未提供显著性检验；Table15/16固定WebShop W/H测试，无明确独立调参holdout或多重选择控制，不能称普遍最优、bootstrap或统计显著。
- A.7：200window=每benchmark50，113trigger含99soft+14hard，87control来自同tasks/runs未触发step。stage1隐藏trigger且只给precontext，stage2对trigger再给guidance/continuation，verifierverdict始终隐藏；两名团队成员独立标后讨论共识，原始agreement94.5/90.9/95.6和kappa.89/.82/.82分别对应200/99/113，确实报告了事前一致性，不误写没有。该taskmatchedcasecontrol样本accuracy不能直接当部署precision/recall、自然failureprevalence或全体missrate；helpful是对指导本身评判，不以最后是否遵从为条件，localhelpful不等finalsuccess。
- A.8：deterministic标签检索非embeddingsemanticretrieval。精确同type+sharedlabel过滤、overlap降序/recency tie、超过5时尽可能每primarylabel最多2，fallback同type最近k。尽可能diversity不是硬quota/全覆盖承诺，fallback不保证语义匹配；topk限制条目数非entry字符/token/累计conversation或扫描CPU。没有删除旧injection的明示规则，不能称所有历史只暴露k条。未规定检索失效/用户更正版本传播，不能替代MemoryLedger不可变引用与basis。
- A.8.3是prompt skeleton而非完整benchmark schemas/可执行adapter；detector/evidence、schemaaccepted与permission/工具真实性/independent科学验收不同。Verifier对具体trigger局部进展、updater仅verifiedsoft成功，但samebackbone判断仍有误标，不能自动变user_confirmed或trustedresult。A.8.4例条目未提供逐条源轨迹/hash/correction生命周期；示例rep00003用reward措辞，与“verifier无benchmarkreward”声明如何衔接未澄清，未运行代码/数据，不据此指称实测reward泄露。
- Table5报total19.01M/Base12.32M包含input+output但未拆cache/reasoning/按角色及初始化/重试/采集错误，API费用/日期价格/硬件并发/时延raw缺失。展示各metric吞吐不能替代同质量/同token/完整walltime收益；本库所有角色真实tokens/费用unknown。

## 本库采用边界及剩余工作

本次额外静态核查project_memory.py284–345、handoff_basis.py218–269：correct文档要求实际用户来源，accept创建新verifiedrevision并使声明后代stale；只凭source字符串不会完成宿主真伪认证。basis_impact只沿声明localclaimDAG与memory依赖返回影响，不重写历史ACK或自动重跑。Sentry的same-model“已恢复”不构成这两条可信宿主依据，不能接成自动accept/correct。

adopt后续评价思路：同检查点有/无指导，保留gain/tie/harm和最终指标，另测全部检测/验证/更新/加载成本；按当前失败有界检索，与完整背景曝光对照，同时确保必须保留的更正/异议/依赖闭包。这里只是为未来实验选评价原则，尚未启动实验、实现playbook或迁移。defer自动LLM诊断/写回/淘汰、固定重试/放行；恢复条件是可信真实宿主、完整输入、授权与未耗尽预算、独立局部及最终质量标签/完整成本对照，先版本化方案独审，不能重置旧门禁。

本次只推进同一SYSTEM99阅读与源码审查，未发现新的已验证生产修复，不以论文作者结果冒充本库收益。正文+附录阅读完成，静态独审待一次单独有界调用；出版前仍39篇，不自动增计。未触及人类guide、唯一TASK稳定Plan或任何生产文件，保留MemDerive及全部旧耗尽/暂停门禁。真实宿主/全输入/质量/全费用/并发恢复等仍未决。
