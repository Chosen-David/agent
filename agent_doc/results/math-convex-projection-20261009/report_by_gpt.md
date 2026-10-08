# 给定token子集的最小输出误差与可复核证书

本轮补齐 `math.convex-projection-certificate@1`，接入现有按需知识入口。它回答此前凸支持存在性不能回答的问题：**给定已经选中的value，允许非负单位质量重赋权，输出误差最低是多少，当前权重距离最优还有多远？** 不新增Skill，不改生产runtime或SGLang。

## 数学结果及实际价值

C=conv{v_i}非空有限，固定目标z。平方距离投影输出唯一，系数不一定唯一。可行y的r=z−y，P=||r||²，g=max_i r·v_i−r·y，D=P−2g：max(0,D)≤p*≤P，P−p*≤2g；g=0当且仅当y最优。证明由经典凸一阶条件和完整平方展开给出，不依赖黑箱QP声称收敛。

Indexer对应：z是固定query的dense teacher输出，点集是原选中values。若D>0，则这个子集在指定simplex约束下无法靠重新赋权消除误差；若几何最小误差为零而实际截断输出差，权重/评分仍有探索空间。这能区分子集几何不足与权重不足。token overlap不决定该凸包距离。

具体例：原values=(0,1)，目标2，非负配比的最佳输出1，误差平方下限1。无约束线性权重(−1,2)得到目标2，不能当合法改进。另例C=conv{0,2,4}，目标4，当前输出2；若检查漏掉4，会误报误差4最优，完整证书拒绝。配方/传感器平均为成立跨域映射，协方差及未来query不自动保真。

固定线性T可以在Tv/Tz空间认证；有核时mapped误差0不保证raw误差0。改变度量、value表示、可行系数或目标后，旧证书需重新建模。

最小迁移实验候选：固定真实trace和支持预算，按原权重输出误差、认证凸包误差区间及gap比较候选集合，判断是否值得重新赋权。已知teacher是前提；求解成本必须另测。当前没有真实trace/模型数据，因此仅采用知识和边界，没有可靠生产性能改进。

## 经典依据与近期原始研究

经典Boyd–Vandenberghe《Convex Optimization》(2004) §4.2.3 pp139–140 (4.20–21)/proof；本轮投影及P−2g下界为项目完整特化推导，非新定理。[作者原书](https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf)。

2026-10-09检索正式ICML2026 WildCat（Tobias Schröder、Lester Mackey，PMLR306:108454–108484）。[正式论文入口](https://proceedings.mlr.press/v306/schroder26a.html)，固定最终PDF摘要见sources.json。读取§2.1、§2.2、§2.6及Algorithms2–3。其Nyström核权重和VS=WV、w=W1改变了value与归一化对象；不等于本卡在原values凸包上的single-query simplex优化。允许重构values后原凸包误差下界不一定约束它。仅做研究筛选/对象对照，未核验全文误差定理或复现模型/GPU实验，不搬用作者性能数据。

## 实际验收及成本范围

- 12公开Fraction案例通过：内点、边界、三角形外点、重复/singleton、空集与负权拒用、非最优gap、漏max反例及T核；小规模face KKT枚举与全顶点证书，非一般生产QP/浮点/Lean证明。
- 三条不提示定理名的结构问题×文件/SQLite后端，top3共6/6命中，含配方跨域与span/负权拒用查询。只是结构回归，没有模型检索或拒用实测。
- context加载新卡及dual-certificates强前置，实际6609序列化字符，预算≤3项/12000字符；实际token未测。时间/输出字节在retrieval/raw文件记录，仅诊断，不当性能收益。
- 53项知识/索引/数学/交接/复用回归通过；镜像同步check通过。optimization覆盖补记后再次同步/检查。未读取已有未见题内容，公开案例不能当未见测试。

独立完整计划批准在数据生产前取得；实际结果另由不同上下文做六域审查、固定receipt与宿主观察门禁。没有模型/GPU/e2e或任务成功率结论。保留原GPU/其他域游标和未完成CI项；下一步需要真实value/目标trace、可认证浮点计算及成本预算。
