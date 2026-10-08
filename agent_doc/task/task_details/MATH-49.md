# [MATH-49] 成对双线性风险与独立代理

Task-ID: MATH-49
Date: 2026-10-08

## Plan

用户持续知识建设授权；单一主题：成对q/k的联合四阶矩风险，独立代理的失效反例及相对度量证书。1200秒总资源预算、CPU测试90秒，独立审核各至多1个真实上下文、计划至多2周期、生产尝试至多2；无模型/GPU部署、无新定时器、无SGLang写入。先fetch并核对main a874726，发布前再次同步、非强制直接main及独立远端读回，保留无关未提交工作。

方法：column-vec与Kronecker经典基础；E||q||²||k||²有限确保D=E[(k⊗q)(k⊗q)ᵀ]；风险vec(H−M)ᵀDvec(H−M)，一般不等于Sk⊗Sq。若SPD代理D0存在且其相对残差算子范数η<1，得到(1±η)风险夹逼与代理最优解的(1+η)/(1−η)近似因子；未给一般paired rank-r全局求解器。反例：成对onehot的独立代理最优不等于真实最优；一般白化不保重塑矩阵秩；二阶矩有限不足联合四阶可积。物理迁移是共状态传感器电流响应，保留单位和支持转移风险。

验收预先固定：Fraction精确枚举3种联合有限分布、矩阵误差菜单和rank1/0/满秩边界，独立直接分数与D二次型/梯度恒等式；相对η=3/5的已知对角SPD证书与不满足η<1反例。公开无定理名查询含跨域与误用，文件/SQLite各3次top3命中；加载新卡及必要前提≤16000字符，不将字符当token。知识格式/必要相关回归/插件同步。未读既有holdouts内容并保持元数据原字节；公开算例/查询不称未见模型实测。

复用既有model-with-knowledge入口/知识与结果工作流；math.paired-bilinear-risk@1单一按需入口，维护领域/结构/学习状态。来源核查Higham作者文与ICML2026正式A3论文§3.1，更新日期/最终PDFhash/读取范围，版本不可验证候选排除。独立plan-review批准后才生产；producer→verify_experiment_result→publication同合同，六域验收。实际本地宿主分离上下文，不宣称Engine/ReviewSession自动认证或tmux部署。仅知识/合成/结构检查，无e2e收益则不改生产行为。

允许作者root写：新知识json/md及插件镜像、知识README/coverage/learning_state、TASK与MATH-49详情、本轮结果目录和自有运行状态。不写人工guide、旧证据、无关文件/源码。报告后独立验收冻结实际代码/输入/原始数据/语料/配置/输出/环境；失败保留、版本化返修且预算不重置。

## Progress

独立计划及六域结果验收usable-with-scope；36个精确开发算例、6次结构检索、52项定向测试、插件同步通过。递归证据补全，旧不完整清单保留；4条强前提闭包13279字符，token未计量。无模型/GPU/Lean/e2e收益，未改生产或SGLang。科学提交 bbee2b2245cc28649ee705313da0ca77464b5197，远端SHA及tree已由fetch/独立ls-remote核对；发布回执见本轮publication_receipt.json。保留既有GPU残差证书与其他学科游标。
