# [MATH-53] 选定value的凸输出投影与误差证书

Task-ID: MATH-53
Date: 2026-10-09

## Plan

用户持续基础知识授权：一个有界经典主题及近期原始研究筛选。新知识math.convex-projection-certificate@1：有限非空C=conv{v_i}，固定z，非负单位质量允许重赋权；最小平方距离唯一输出y*，权重可不唯一。r=z−y，P=||r||²，g=max_i r·v_i−r·y≥0；D=2r·z−||r||²−2max_i r·v_i=P−2g≤optimum≤P。g=0 iff y为投影；所有顶点必须入max，signed/empty/线性span投影不等价。固定W只保证W输出。

前置dual-certificates@1，旧convex-support仅相关导航：此前存在性没有指定子集最低误差。旧结果实际检索partial，旧测量不用；GPU/CI及其他域状态保留。原始Boyd-Vandenberghe2004§4.2.3(4.20-21)及proof；上下界为项目完整配方推导。近期WildCat ICML2026 PMLR306 p108454–108484，读取§2.1/2.2/2.6/Algo2-3，kernel Nyström权重/改写values与本单query simplex权重对象不同，不能迁移证书或背书完整误差定理；未复現。

真实local手工DAG：完成fresh clone main/指南全清单/ResultStore+KnowledgeStore查询 -> 独立新上下文完整plan审查approve -> Fraction有限face KKT枚举12公开例及6双后端top3检索 -> 不同新上下文verify_experiment_result六域 -> usable-with-scope消费者知识/state/main发布 -> fresh fetch/nonforce CAS/remote SHA tree readback。不是Engine/ReviewSession或远端tmux服务；无真实model/GPU后端，不声称部署。没有隐含生产迭代，1200秒总预算从本主题首次检索目录建立开始，2计划周期、2生产尝试，CPU各90秒，验收失败版本化保存不重置budget。

cases与retrieval_protocol先冻结；独立结果绑定同一controller_contract在producer、verify、consumer。完整code/runtime/递归语料及mirror/源版本/环境/原始结果/报告sha；learning_state存历史快照以允许闭环。主AI独写本轮知识card/mirror、coverage/README/learningstate与TASK；reviewer只独写指定本轮independent*/plan_review*。严禁修改SGLang、人类guide、旧知识正文、未见题内容或新Skill/生产runtime。

公开新问题3条含配方混合跨域和signed/span拒用结构，文件+SQLite共6，context≤3项/12000字符，不折算token。数值例不替一般证明；独立证明审查不冒充Lean。冻结必做命令：`python scripts/sync_plugin_references.py`，`python -m unittest tests.test_knowledge tests.test_knowledge_index tests.test_knowledge_math tests.test_knowledge_handoff tests.test_knowledge_reuse -v`，`python scripts/sync_plugin_references.py --check`；全模块通过及镜像exit0，计数仅诊断，失败/skip日志保留。

## Progress

fresh clone tip d9812e8，目录维护后工作树干净，无本主题活动任务。GUIDE原文为空，全guide只读；未采纳advice。已有结果与知识检索保存，未消费旧数值。等待独立计划审查。
