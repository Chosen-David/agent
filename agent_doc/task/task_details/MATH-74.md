# [MATH-74] 熵正则菜单与原始代价、硬约束边界

Task-ID: MATH-74
Date: 2026-10-10

## Plan

EXECUTE持续学习2/4/5/6/7/8/9/10；复用research-explore，独立有界文档研究1200秒、最多两次普通独立审核session，主AI唯一作者。非受管DAG，无可信ReviewSession/result_verifier，不做CPU/model/GPU/Lean/未见实验。MATH65继续blocked，旧预算/失败/候选不变；不修改SGLang/guide/runtime/Skill/canonical。

candidate.gibbs-regularized-menu@1：有限非空M个动作、固定有限同单位代价c、tau>0，G_tau(q)=E_q c−tau H(q)；证明G=−tau logZ+tau KL(q||p_tau)，唯一Gibbs最优；区分softmin与实际平均代价，0≤E_pc−minc≤tau logM。固定c时dE/dtau=Var/tau²；proxy全动作误差epsilon给原始代价差≤2epsilon+tau logM，低温不能修复proxy反序。正gap/tie-count控制次优概率，菜单重复改变先验。硬预算逐动作先筛可行集，期望约束/多worker独立抽样不代替共享可行性。非均匀先验、排除最优边界只解释不扩成新求解器。

公开无定理名开发验收：c=(0,1),tau1得到bad=1/(1+e)，softmin<0但代价>0；复制bad到N个概率N/(e+N)；proxy反序低温选坏；资源2/4预算3且同loss均匀抽样，期望3仍半数越界；两态物理能量(0,Delta)与kBT同单位；有限uniform prior KL≤logM不coercive，拒绝最新连续action论文的radial-unbounded结论。公开解析例不当数值或模型实测；保留未见测试。

先完成真实知识/历史查询（120/partial/errors），少量卡核对；来源经典Mezard/Montanari作者2007-11-09 draft §4.4 Prop4.13和eq4.42/43（不能冒充2009正式页码）；近期2605.24939v1 2026-05-24相关intro/Assumption1/2/Theorem2，仅筛选gradient-flow/feature条件不套有限菜单或SGD。记录日期版本发表状态/阅读scope。候选双索引，TASK/coverage gap/history更新但canonical计数旧游标不改。

验收限定普通独立文档检查证明/解析例/物理单位/refusal/引用；后续实际逐层alpha-beta-gamma或多GPU调度需要固定联合动作loss、proxy误差/硬可行、工具/预算和模型matched A/B，不由本候选宣称提升。发布前fetch同步处理并发，直接main无PR，远端SHA/父/树核对。

## Progress

- main clean且已同步78d9a85；读取AGENTS/任务/角色/知识导航/持续状态及相关协议；无同主题任务，GUIDE空。已有MATH73完成，MATH65不恢复。历史查询和真实knowledge_refs已保存。

- 普通独立Plan审核approve，最终稿明确KL关于参数theta的径向无界性，绑定candidate/version/hash；源文和推导待不同上下文独立核对。

- 不同上下文独立文档复核APPROVE，完整最终hash/证明/7个公开解析例/物理单位/原文版本与页码核对见document_review.md；无CPU或模型实测，非可信结果验收。候选双索引、学科缺口、history追加，不推进旧游标/计数。
- 303受保护路径与78d9a85字节一致；JSON/advice与Plan哈希、历史前缀/游标、CRLF感知diff结构检查通过。按授权发布前fetch处理并发、直接main核对远端SHA/父/树；真实联合配置proxy/资源成本与收益仍待测。
