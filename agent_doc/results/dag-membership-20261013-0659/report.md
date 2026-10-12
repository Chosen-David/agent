# DAG 校验成员查询优化

同一公开 validate 入口在本机合成CPU场景中，独立首轮512节点耗时48.805554→14.466526ms（降低70.36%）；1000节点密集依赖1706.175503→126.066791ms（降低92.61%）。小输入producer退化4.50%、独立降低7.36%，均在预先10%非退化门内，但微秒噪声不支持小输入稳定提速结论。

## 变更与契约

实际入口 Store.create 调用 core.validate，复用本来用于任务ID唯一性检查的set。所有ID及当前dependency均为exact builtin str时查询集合；str子类及其他类型走原list，保留原错误次序/文本、重复ID、非法字段、判环和最终JSON验证。不缩输入域、不改变授权/重试/恢复/结果验收。

成员查询原O(E*V)，普通字符串候选期望O(E)，额外保留集合O(V)空间；判环仍原实现，不称整体validator线性。候选只有9行diff，另2个持久边界测试。首次计划只检查dependency类型，独立审核指出ID子类hash/eq风险，v1 revise保留，v2才批准。

## 证据

基线main6886c3ff3f4c5238d733d9da9ac349933f3020de，core SHA198753673877360b828ba89bccc68bba1da70996a0f26fd8d2b5f7049ed94298。候选SHA d137bd76e938283611e47acad4eec5bf8b706f9f3e3dcf9d0b264ba5df4196d8。check.py SHA694b962cad01769a734e1cc43c5b11b5202dc0f40f27f9776ebdb339a54c673e；producer和independent.json保留全部7对计时、输入hash和实际git baseline加载。

冻结2warmup/7pairs：1节点每样本1000次，512节点每节点前最多32依赖，1000节点依赖全部前驱499500edges。独立首轮两大输入>=10%改善/小输入<=10%退化门均通过，无改阈值/性能重跑选优。

541个公开入口差分覆盖512三节点图、反序/重复/非法依赖、字段、Unicode/空/重复ID、str子类；producer/独立普通及独立-O摘要一致；独立另10个hash/eq抛异常、无hash、错误顺序案例。review.md绑定全部实际文件hash。测试新增的OddHash fixture最初误以为原validator成功，实际原判环使用set会报dependency cycle；候选也相同。修正期望，不修runtime，不隐藏runtime-tests.log及full-tests.log首次1error。后续v2只重跑受fixture改动影响的回归，不重复性能。

当前测试状态pending：最终结果将在下面追加，未过全部适用检查不能发布。

## 研究输入与局限

本次沿用持续批次已有十篇原始论文机制对照：docs/continuous_optimization/rounds/2026-10-07-revision-handoff/round-w6.md记录10/10以及实际阅读范围；这是历史原始阅读，不冒称本次新读十篇或每篇全附录均覆盖。后续HDSO、SkillOpt、Budget-Web、ProcessEval、GroundEval、ReliabilityBench、OrchestraBench、Recova全文记录继续累积，未直接作为本优化收益证据。OrchestraBench促使检查公开实际入口/对照而非组件名称；ReliabilityBench/Recova促使保留重复、类型和异步证据边界。此次创新应用为本库依赖校验的语义保持成员索引复用，是已知数据结构机制的工程应用，不宣称论文算法创新。

官方Python set合同参考 https://docs.python.org/3.12/library/stdtypes.html#set-types-set-frozenset ，本次普通3文档跳至3.15，不把其版本当执行器版本。实机Python3.12.14/Clang22.1.3、Linux6.18.44、AMD EPYC9V74型号、9在线虚拟CPU，无独占/绑核/锁频。独立者-O正确性进程曾与首轮计时短暂并行0.27s，已明示，未重跑/删原始数据。大形状root与独立同数量级改善；小形状方向不稳，不主张稳定变快。

历史有界查询200目录、68缺record错误、partial=true，命中combined-corpus-v3/comm-ack-confirm/comm-batch均不是本次同输入timing证据，不复用，也不推断没有历史结果。

无LLM、GPU、服务、实际任务完成率/token/费用或Store/tick端到端性能实测。密集形状是压力输入，实际工作负载频次未知。独立模型代码review是宿主实际不同调用，不是ManagedEngine/ResultValidationHandler可信adapter部署回执。没有安装/启动后台服务。持续目标不因一次本地优化完成而结束。

复现：在干净6886c3f基线应用此次core补丁，python agent_doc/results/dag-membership-20261013-0659/check.py；原脚本固定git基线，不用候选自造参考。性能计时不要与全库tests并发。

## 最终回归与并发整合

修正后runtime39/39通过；全库1177项，1169通过/8跳过，71.771s；Reader3/3通过，1.568s。原首次1error只在新增fixture，完整原日志未覆盖。完整大日志保留本机该目录，发布测试摘要包含哈希和退出结论，不假称远端拥有未上传的完整日志。

发布前远端新增396ed410052e3ccef93564b976c4902a6a56407e（MATH-103知识/记录），已ff整合且保留全部旧未提交目录。core.py及候选testSHA未变，受影响知识镜像独立定向检查另记concurrent-knowledge-tests.log。该整合不修改性能协议，不继承数学科学验收为本候选证据。

持续任务要求映射到原T11的Progress追加，此次仅bounded运行时优化，不重新标记历史任务或整个持续任务完成。未新增调度器、自动任务或旧论文重复读数。发布状态以随后真实commit与远端readback为准。

并发MATH-103知识侧定向test_knowledge_index 11/11通过（3.639s）。全库无需因无运行时变化重复性能；已完成的完整套件与当前core/test字节对应。
