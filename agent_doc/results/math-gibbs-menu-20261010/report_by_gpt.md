# MATH-74：熵正则菜单的推导与迁移边界

新增document候选candidate.gibbs-regularized-menu@1，精确区分regularized softmin/原始平均代价。补finite KL恒等式及唯一最优、tau logM原始代价界、固定cost温度导数、proxy误差2epsilon+tau logM和gap/ties概率界。菜单别名和prior会改变随机选择分布；期望预算不保证单次硬资源可行。不是新算法、模型提升或已部署选择器。

具体迁移：各层alpha/beta/gamma/method的完整联合表或多GPU完整assignment可作动作，必须先核验联合可行、固定同单位端到端cost与proxy误差。局部layer oracle不等于全模型cost，多worker分别抽卡不保证不碰撞。若真实cost已知且只优化本次平均cost，argmin已有最优性，finite tau Gibbs反而有正则偏差；探索价值另需完整成本/质量对照实测。两能级物理映射保留Gibbs权重及自由能单位，不证明冷却动力学或推理能力。

公开无定理名开发题：二态负softmin/正平均cost；N别名导致bad=N/(e+N)；proxy反序低温选坏；memory2/4均匀期望3但半数违反上限3；两worker抽两卡半数碰撞；有限二态KL关于无限theta仍≤log2，拒绝连续action径向无界性。当前均为解析结构检查，不是CPU/模型/GPU/Lean/未见测试。公开题不再算未见，既有未见材料未访问。

历史查询120/partial/errors，首选命中旧corpus release不同scope，未复用CPU数据、不宣称全面排重。宽泛entropy词法命中RL/下降卡不适用；按结构进一步读取真实support-conditioning@1的非负KL/支持排除，完整pinned knowledge_refs与candidate hash保存。候选学科/问题双索引不接生产库，不改110/5/67计数及旧游标。MATH65暂停/失败/预算保留。

来源：作者2007-11-09 draft §4.4/Prop4.13/eq4.42/43，明确不引用2009正式版页码；2026-05-24 arxiv2605.24939v1筛选相关intro/Assumption1/2/Theorem2，有限正质量菜单不符合连续最大集零质量条件，不移植gradient-flow或regularized convergence到SGD/Agent。原文阅读范围与正式发表未核实边界保存。

审核/提交状态：普通独立Plan与不同上下文文档证明复核绑定记录；不宣称可信ReviewSession/result_verifier或数值实验验收。结构检查包括JSON、精确hash、旧游标/history前缀及受保护路径，不是模型能力测试。直接main发布前同步，远端commit/parent/tree在交付核对。

没有真实策略/模型/硬件收益证据，本轮不改生产行为或SGLang。下一步在固定真实决策数据、完整合法联合菜单与独立执行/验证资源上，按advice等预算比较静态/argmin/Gibbs及oracle，并计全部选择/校准/通信开销；若硬越界或实际劣于静态保留负结果并停止采用。
