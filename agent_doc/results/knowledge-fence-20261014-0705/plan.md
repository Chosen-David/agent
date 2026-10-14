# 知识段落 fence 修正候选

Task refs T11 / KNOWLEDGE-FENCE。用户授权同目标接口的小型质量修复、验收后直接main；无PR/新分支/force。main2393d96ea17b9e8db4999ab8ea74c1ad23ae9dc8，保留MATH-115及未提交研究；guide不可写。决策EXECUTE：修正已有sections“fenced code is not a heading”契约，接口/schema不变，不扩大到完整Markdown解析器。

原理来源：CommonMark0.31.2 §4.5规定关闭fence仅尾随ASCII空格/tab，backtick起始info不可含backtick。当前knowledge_index.sections仅识别前缀、长度，可能错误关闭含info的内部行，或误开非法backtick-info行，使代码内标题暴露/正常标题隐藏。新SkillDelta论文原始入口读取失败，未计精读/采用。既有52条论文登记只作历史，不重新认证或当本轮新阅读；本候选为局部正确性维护，不称新Agent算法创新。

先查结果：actual prior-search，230/partial=true/84错误，advice-context/cluster-planning/codex-pull-sync三候选与本parser/code/边界不符；拒绝复用为实验数据。已有普通fence单测不覆盖两种合法性边界。

生产者：固定案例覆盖backtick/tilde、关闭info、非法opening info、长短fence、不同字符、空白/CRLF、无close、0–3空格；10–20个有界案例+真实知识库sections对拍。冻结期望按规范而非候选实现生成。主要指标：标题集合/源范围符合预定oracle，全部正确且确有baseline失配改善；不称模型/性能收益。非退化：普通fence/control全通过；既有知识库预期未受bug影响条目完整输出不变；source行范围与原文闭合；根/独立Skill镜像一致。

方法：只在原fence状态分支检查tail合法性，维持其余标题匹配/树/分段字节；ENGINE_VERSION升级以拒绝旧SQLite缓存并触发已有重建路径。同步plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_index.py同字节，不写guide/历史输出。增加有意义的失败case与旧engine拒绝/重建测试，不扩大到HTML/container解析。

流程：独立计划审查→生成固定probe与baseline源快照/原始结果→实现与定向回归→独立源码/输入/全输出/普通-O验收→全库及Reader规定测试→报告/显式清单→重新fetch并发差异检查→main普通发布回读。若没有baseline失败或引入源范围/检索变化，保留负结果并不发布。缺实际独立认可只阻塞依赖发布，不假称部署受管runtime/监督器。单机标准库CPU，预算小于1分钟/测试调用（全库允许既有时长），不调用模型/GPU/付费服务。

allowed_writes：两个knowledge_index.py、tests/test_knowledge_index.py、agent_doc/task/TASK.md、task_details/KNOWLEDGE-FENCE.md、本run目录。主控唯一写源/任务；独立审查只写本run审核/独立数据。
