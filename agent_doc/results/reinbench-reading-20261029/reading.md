本稿经一次独立静态审核，结论revise两处局部表述：Eq11须限定未clip区间，observer须包含固定GUIDE/TASK/advice绑定。主控按原文/源码修正，未追加第二次审核；完整反馈保留，不宣称当前修订稿再次独审通过或可信运行时认证。原稿/inputs指定SHA保留在运行检查点。

# ReInBench / ReCoF：局部恢复预测不等于干预收益

SYSTEM-99 / Plan54，同批续接；2026-10-29读原始HTML科学正文，不是作者实验复现。论文为 Chiming Duan、Tong Jia、Yingxi Chen、Minghua He、Lingzhe Zhang、Ying Li，*When to Intervene? An Empirical Study of Errors and Self-Recovery in LLM Agents*，**2610.36471v1**。原始摘要页提交时间2026-10-27 01:26:53 UTC；搜索镜像更新时间不替代精确版本。[正文](https://arxiv.org/html/2610.36471v1)，[版本页](https://arxiv.org/abs/2610.36471v1)。arXiv nonexclusive-distrib，不当代码/数据开放许可授权。

实际阅读：§§1–6、Appendix A.1–A.4、Eq1–13、Tables1–2、Figures1–8文字图注；normalized text [0,57000)、[63500,78258)，参考文献中间未读。未读PDF像素、作者代码/原始数据/完整执行轨迹，未运行模型或复现实验。缓存字节/字符数与SHA见inputs；它们不是token数或真实模型完整输入证明。

## 方法与可观测性

- 任务轨迹保留goal和逐步reasoning/action/observation。错误是局部状态偏离；恢复是满足指定局部恢复标准的最早可观测状态，不要求任务完成，也不要求可辨识的认错时点。重复失败尝试在同一event，已经恢复后的再发错误才是新event。有效rollback/替代路径可恢复；LLM声称修好了不够。
- ReInBench有1259 traces、1403 errors、725 observed recoveries，其中553有recognition，172没有。OSWorld从1076 traces/360任务筛到986/358，表中3.7/4.5/Kimi各304/339/343 traces，errors588/343/271，recovered268/226/165；Web从300字段检查→291标注→273，GPT-5-2025-08-07 medium SeeAct轨迹生成于2025-08-13，errors201/recovered66。各阶段剔除及完成情况会带来选择偏差，不能假定随机缺失。Web缺原始screenshots/完整DOM，状态判断依赖反馈和元素元数据，不能对齐为同等可见性。
- 两个标注LLM（GPT-6.1-sol/GLM-5.3-Flash）独立输出，规则/LLM evidence check后，3名研究者逐条核查；成员可看模型标签和解释，但不看彼此判断，分歧/歧义全轨迹讨论至共识。保留追踪资料有利审计；共识不等于盲标一致性，没有看到pre-adjudication agreement/标注敏感性或全流程费用。
- target y=1是**现有记录终点仍未恢复**，并非无限时间不可恢复。ReCoF预先给定错误发生step，仅看最多5步到该动作之后observation，禁止未来轨迹/回溯错误描述；不是在线检测器，检测漏报/误报和延迟未包含。
- 固定Qwen3-Embedding-0.6B、SigLIP2、Qwen3-VL-Embedding-2B编码，文本/视觉/联合特征、reasoning首末差与视觉最近差；缺特征零向量加availability indicator。任务、模型身份、动作参数/重复等描述也进入专家，不能把贡献简单称为记忆学习。专家包括多视图、视觉、联合分类、MLP、partial-pooling/RBF和投票。RBF同模型η加权不是模型升级迁移验证。
- GLM-5.3-Flash temp0给binary contextual verdict，实际Appendix A.3看当前与窗口内最近上一张截图及5步文本；联合encoder可看interleaved window截图。不把概括的可用screenshots说明当逐模型相同完整输入认证。fusion向量[p,a,p*(2a-1),model onehot]，在标准化后未触发clip的区间内，interaction等价于依verdict改变专家线性系数；模型onehot本身是加性项，不是任意模型×专家interaction。
- experts训练在train、选择在validation；fusion在validation任务分组3fold，均值/尺度仅fit各训练fold、clip±8，model×class平衡权重、C=.01正则（包括bias）。保留fold模型，无最终refit；每模型用200次label-stratified bootstrap的OOF最优MacroF1阈值中位数，test平均3fold概率后阈值决策。bootstrap校准不是置信区间。

## 结果、消融与关键限制

1. RQ1：OSWorld659/1202=54.8%、Web66/201=32.8%恢复；timing仅600/66 boundary可辨识的恢复event，recognition分段509/44。报告恢复者中位2/3 steps、长尾78/48，不包括未恢复event的等待时间分布，不能推导最佳等待2步/3步或wall-clock SLA。不同数据的step单位不等同API耗时/费用。跨3模型shared错误任务上的恢复比例43.8/64.4/52.7；同任务不等同同错误、脚手架/输入暴露/任务难度完全控制。Venn百分比分母是至少一模型全恢复的union，不是所有shared任务；7.8%三者全恢复/52.9%仅一者，不能据此选模型路由。
2. RQ2：先前已恢复event与每个之后event配对613（same200/different413），later recovery56.8/76.0/47.5%；pairs可能共享后来event，非613独立事件。timing126same/181different，仅两者都恢复且边界可定位；faster-or-equal79.4/52.5%包括相等，不能叫严格加速。先前恢复不是随机干预，模型/任务/错误难度、存活长度和配对权重混杂，不证明经验产生因果收益。
3. 727 error-bearing traces分no286/partial161/complete280，task completion20.6/18.0/60.0%；256成功traces平均局部恢复71.9%、471失败37.8%，是每trace比例均值不是合并event比率。完全局部恢复仍40%任务不成功，无恢复也可成功；局部恢复、最终正确、全要求验收必须分开。无错误traces不在这些分母，不能外推整个任务总体。无随机对照/簇区间，不把相关性表述为改善证明。
4. RQ3仅CUA、task-disjoint train559/val228/test238=1025 events；与OSWorld1202 errors的177差额在声明段未明确逐项说明，不自补原因。test很小且3模型条件，不能称未知模型/未知环境泛化。非恢复positive，MacroF1不是成功率或经济效用。
5. Table2 ReCoF MacroF1为73.53±2.33/74.18±3.44/72.99±2.93，对最强外部baseline68.75/72.88/61.69提高4.78/1.30/11.30**百分点**；9.02%是作者报平均相对提升，不是+9.02pp。Recall non-recovery74.72/64.35/58.89，precision69.56/72.19/71.05，并非所有metric领先。五seed只改变fusion，专家与LLM缓存固定，不含数据split/encoder/LLM/judge全流程不确定性。
6. 无experts ablation保留verdict+identity，预测与Direct LLM一致；无interaction保留两信息源，MacroF1变71.14/61.50/69.74（均重新fit/calibrate）。Kimi无interaction precision87.42更高但recall38.89更低；不能说每项均改善，也不孤立证明某个encoder/专家家族有收益。PrefixGuard实际TFIDF4096+GRU24epochs，其他baseline按新目标改造，结果不是原系统端到端能力排名。
7. expert family/config/robust bootstrap selection使用validation，ensemble有200个70%label-stratified validation子集，某validation event只收未包含它的投票；但全validation已用于上游专家选择。fusion的task OOF不代表整条选择管线对该fold完全未见；独立task-test仍存在，不据此指称测试泄露。阈值bootstrap按event标签，不是task簇bootstrap。test概率均值与OOF单fold校准分布也不同，影响需测。
8. C/K/阈值offset敏感性是固定split下test曲线、五fusion seeds；±.01最大约1.43pp，不能称普遍稳定或用test曲线继续调参。未见任务簇bootstrapCI/paired significance或重复独立split；1.30pp差异不自动视为已证显著。
9. §4.4明确仅预测、不执行interventions。没有Wait/Intervene在线随机对照、检测到响应延迟、误干预伤害、额外步数、最终任务净收益/费用对照。LLM评估+多encoder+专家训练/缓存/预测/人工标注均需成本；这里没有完整硬件/时延/全部角色token账单，不能用MacroF1称性能/效率提高或免费恢复。

## 对本库的关系和取舍

本次源码静态查看而非运行：task_supervisor.worker 207–290、guard292–319、_terminal_receipt347–375；maintenance_observer全文件；dispatch_context、log_context、source_context、reference_context全文件。只声明这些范围，不认证ManagedEngine所有转移或真实部署。

- adopt为未来评价原则：错误发生→可见recognition→实际局部恢复→最终要求验收分离；没有可见认错不等于没恢复，报告称修好不等于实际恢复。按task/trace簇隔离数据，完整计入未恢复和拒绝/超时，记录不同schema/工具/模型/observation版本与延迟。这只是后续评价方向，**没有改生产策略或启动新实验**。
- worker在failed/source-changed保持maintenance owner存活，派发条件排除done/failed/cancelled；maintain可在授权内reconcile或版本化新链，注释明确不reset预算。guard crash retry与局部业务错误恢复是两层，不把论文error event当进程重启许可。_terminal_receipt重新核验历史终态并保留cancelled，失败为blocked；不是预测概率放行。
- observer绑定GUIDE、TASK、全部advice，以及宿主显式声明的tracked_paths/external，并比较两次snapshot，不自动发现完整依赖；hash变化不是错误/语义恢复证明，相同snapshot也不是无隐含依赖/ABA/全任务完成。dispatch needs_complete/history_required是宿主声明，不是ReCoF式质量预测或完整provider轨迹认证。log excerpt显式partial，不可拿未展示错误作为已恢复；source/reference显示与恢复协议不提供执行成功证明。
- defer ReCoF分类器/embedding服务、默认等待N步、自动干预/重试、失败状态放行、task/guide迁移。恢复条件：可信宿主完整在线观测、错误/局部恢复/最终质量独立标签、既有明确授权及未耗尽预算、同任务对照和全费用。安全边界、取消、用户更正、证据撤销和旧耗尽门禁始终独立有效；不能以自恢复可能为理由继续被禁止动作。
- prior result正式检索333目录，partial=true、25errors、3显示词法候选为combined-corpus v2/v3/v4，均不同任务/数据/终态/成本条件，拒绝经验复用；全文rg精确ID/ReInBench/ReCoF无命中不证明历史绝无阅读。knowledge query“failure recovery intervention”两麻醉研究候选的物种/成像/麻醉/DBS前提与Agent恢复不符，reject，knowledge_refs=[]。不把这种词法近似升级成数学/经验适用性。

本次无生产修改、测试、作者代码执行、实验模型调用或性能主张。手工独立静态复核状态以inputs和独审原反馈为准；不冒充可信ReviewSession/结果认证。所有AI角色token/费用unknown。已发表同批38篇仍只按既有记录，不因本稿自动增加；MemDerive不完整独审门禁及其它耗尽/暂停范围不重启。SYSTEM-99真实宿主、完整输入、任务质量、全费用、并发恢复仍未完成。
