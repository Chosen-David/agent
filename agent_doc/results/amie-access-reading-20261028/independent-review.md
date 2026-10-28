# AMIE reading independent review

Verdict: accept（仅限已声明的阅读/源码适用性检查点）；阻塞发现：无。

本次为一个独立 AI 角色的一次人工原始来源审查；不是受认证 ReviewSession/provider 运行时证明。不把本次调用计为免费或零成本；全角色 token/费用未知。没有测试、实验模型、后端、探针或网络调用，没有新 gate、额度重置或生产实现。

核查：实际阅读已保存主文1–6、附录A–C/E–H的正文、表格、证明和图注；对应文本范围[0,39708)、[53813,83322)、[101213,111717)。D/I、参考文献、图像实体、作者代码与原始实验未读/未复现；1405与1500仍只是一篇。抽象页标题、作者、v1提交时间与记录一致。HTML原件及其相关结构已核对；没有从保存原件推断在线真实性或当前远端状态。

论文核查结论：方法、拟合/选择暴露、迁移、消融与标签辅助控制的边界记录准确；单目标固定条件的证明不支持未来总体效用保证。置信区间覆盖范围、来源映射缺口、候选扩池无操作/获取成本、历史适配事件、重复有用证据受损、未知GPU与非完整成本均有明确限制。没有把主表作者结果当本库实测或全系统收益。A.6保存HTML的提示框只展示用户模板/格式提醒，不能据此声称完整系统提示已可重现；现有记录没有作此声称，因此不阻塞。

源码独立核查：KnowledgeStore.search是有界词项候选；context以完整先决闭包为单位，放不下显式partial；check_refs只核身份/发布状态/先决项。MemoryLedger._revise建立新ID并保留旧事件、失效后代；_walk验证当前依赖与文档。basis_context保持消费者必需引用、所有candidate/rejected声明及祖先，完整依据预算不足拒绝；缓存提示只允许当前消费者已有且再次核验的依据。未发现reading.md对这些入口的关系描述越界。

知识使用：对knowledge实际执行只读search("retrieval memory context dependency correction",limit=2)、context(max_entries=8,max_chars=18000)、check_refs。快照767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18，context ready，身份校验通过。返回algo.qlora-memory v1/08684e7e9ae88964f84a9d275990341f2ed28dc78ae3fc3affeef8319d6eead3和ds.hnsw-recall-budget v1/8f736520925598cd563890785a162bc50b45891506c859ab1685434dbd10d11c；仅memory词项重叠，与本任务不匹配，拒用为科学依据。此次适用性依据为保存原文、实际源码和工作流，而非检索分数或校验通过。

治理核查：AGENTS、文档治理、知识接入及记忆工作流已读；指南为空且只读，SYSTEM-99 Plan54/当前Progress及唯一索引保持未完成。采用/调整评价原则与暂缓访问状态/选择器/删记忆/迁移的理由及恢复条件充分；不构成实验批准。未重审前26篇正文账本，不替主控认证最终公开发布。

发布条件：仅主控可维护获准四份公开文件及SYSTEM-99 Progress；公开回读后才可把同批26记为27。当前本审核不增加计数、不关闭SYSTEM-99，也不代替完整输入/任务质量/真实宿主/全角色费用验收。

Reviewed SHA-256（读时所有已声明输入哈希均匹配）：

| Path | SHA-256 |
| --- | --- |
| `.agent-runs/continuation-1405/2610.34977v1.html` | `05fe37b67f94ea9560d910186266fdad12a9f62c9ac23b4c976007a1ba43ba0e` |
| `.agent-runs/continuation-1405/2610.34977v1.txt` | `e0d1909f9f533254635fa49b1aa5a0d0da21e41a1fb0ae951665644f6a8476b5` |
| `.agent-runs/amie-reading-1500/abstract.html` | `aeeae73e7a479466f70b6854eabdd0ed848a5fa80616b3f8eb1cee14bc66c223` |
| `agent_runtime/knowledge.py` | `eb17aab6668435d6dea09b4010cc2410fbd66844e60fcfb1bef4d4817971eb01` |
| `agent_runtime/project_memory.py` | `1f0fe4edc8abf2371972817083c2c12cc33dbb07640ed57dffc2d8a744b35e41` |
| `agent_runtime/handoff_basis.py` | `20b4e127726f046b564086d2c5028ba92e986c6b796784a23cfe94971071f50a` |
| `workflows/project_memory_workflow.md` | `4522bd15ed5ade12e40f2f18a2c4c840a2a8f539d8625fae0aef177ced7566aa` |
| `agent_doc/task/TASK.md` | `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f` |
| `agent_doc/task/task_details/SYSTEM-99.md` | `cbdc50f3b5a903525c885a045b8d4203cbfb313e615da7e9b3dd40e75961853c` |
| `agent_doc/guide/GUIDE.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `agent_doc/results/amie-access-reading-20261028/reading.md` | `6339a433143e6a616c1ff3097104210b095194e9b066b8f82f782afe527d704c` |
| `agent_doc/results/amie-access-reading-20261028/inputs.json` | `343c2c41b10f455398baa4daea5be2e281b865187f79e1fa11a4e7894d5c0327` |
