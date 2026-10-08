# [MATH-52] 固定加权输出的凸支持约简

Task-ID: MATH-52
Date: 2026-10-09

## Plan

持续基础知识授权。补齐Carathéodory有限凸表示与仿射秩r+1约简，映射固定query的value加权输出；不将重新赋权等同原softmax子集重归一化，不将单query存在性当全query/在线成本保证。保留2b50c99并发正态混合更新及其未完成CI状态；GPU证书游标保持。真实GUIDE空，无建议采纳。

总1200秒、2计划周期、2生产尝试、CPU各90秒；先独立新上下文完整计划批准，producer后另一实际上下文verify_experiment_result六域验收，usable-with-scope后才消费者发布。仅本地主控实际分离上下文，不宣称Engine/ReviewSession认证或远端tmux部署。原始失败保留，不重置预算。单一作者root维护TASK/详情、一个新知识卡及镜像、README/coverage/learning_state和本轮目录；reviewer只写plan_review/independent_*。禁止SGLang、人类guide、其他已有知识/留出内容修改，无新Skill或生产代码。

DAG: actual startup/ResultStore+KnowledgeStore search -> independent_plan -> finite Fraction producer + file/SQLite structural retrieval + five-module targeted regressions/plugin sync -> independent_result -> document/state/publish -> fresh fetch/CAS nonforce main -> remote SHA/tree readback。同一controller_contract绑定producer experiment_result、verify result_validation与consumer required_result_refs；验收脚本/全部运行时/递归完整发布语料与安装镜像/协议/源版本/环境/原始记录/报告固定hash，learning_state用历史快照允许最终状态闭环。仅公开开发任务，不读未见题内容。

知识对象：非空有限v_i∈R^p、α_i≥0、Σα=1、z=Σαv、r=dim aff{v_i}。增广矩阵[v;1]核内方向a使Σa=0，θ=min_{a_i>0}α_i/a_i，β=α−θa，迭代正支持至≤r+1；固定W可对Wv约简，仅保真Wz。Fraction固定8例（cases.json），含重复、零权、singleton、非负拒用、simplex紧界和原权重归一化反例，数值例不证明一般定理。三条未提示定理名的结构查询含传感器跨域与误用；每后端top3，context≤3条/13000字符，字符不是tokens。实际模型/Lean/GPU收益不测。

原始来源：作者2026-09-02讲义Theorem1/证明，仅经典有限凸表示；近期Cohen arXiv2609.06327目前abs显示v2 2026-09-13，读取定义/适用范围与实际模型界局限，筛选不背书全证明。先检索发现已有barycenter/geometry卡，只作边界关系，旧数值不复用；ResultStore partial及缺record明确不穷尽。

Frozen executable acceptance: all tests in `tests.test_knowledge`, `tests.test_knowledge_index`, `tests.test_knowledge_math`, `tests.test_knowledge_handoff`, `tests.test_knowledge_reuse` pass under `python -m unittest` with raw failures/skips preserved; `python scripts/sync_plugin_references.py` then `python scripts/sync_plugin_references.py --check` must exit zero. Counts diagnostic.

## Progress

main同步2b50c99，旧工作干净，本主题无活动状态。旧结果与知识实际查询已保存；等待独立计划审查，原始论文v1之后发现v2已另取回，不沿用旧版本当最新。

计划v1审查revise后v2批准；实际独立结果上下文六域usable-with-scope已观察并pin。8个Fraction公开例、6/6双后端结构查询、53回归与镜像check通过；首轮镜像未同步失败与manifest metrics schema失败日志保留。等待main非强制发布/远端核验；GPU游标不变。
