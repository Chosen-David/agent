# Memory Tax 独立原源/源码审核（1657）

Decision: **accept — usable-with-scope**。Blocking findings: **none**。仅接受固定阅读记录的原文保真与有限源码适用性；不验收论文实验真实性、系统收益、SYSTEM-99完成、可信运行时/模型输入认证或历史登记。真实独立role调用1次，无重试；all-role tokens/费用 **unknown**。

## 固定输入与实际读取

项目 `/workspace/scratch/95d615402a52/agent-run-1202`，实际HEAD `fd9874ed9897444edd9ac23389ed5a6f3841ef07`，与派发一致。下列SHA256均实际重算匹配：

| 输入 | SHA256 |
| --- | --- |
| agent_doc/results/memorytax-net-reading-20261028/reading.md | 801c8eb5ef095be5101f40e18316ce1ced3dca4400f20f1eb181dc553ba7cc31 |
| agent_doc/results/memorytax-net-reading-20261028/inputs.json | c8397b77b5ee69259ee30c1e11335f35db01219b1f38a30b2262f1f2d7dd97ff |
| .agent-runs/continuation-1559/2610.34073v1.html | c0080c542596c6a458549d9140805bcb0f7b96b9283fd3aa363a94ebce855552 |
| .agent-runs/continuation-1559/2610.34073v1.txt | da87649c986e832b996b1c0448ed0970dbf4274a1034c93805f5b9ad9c323e36 |
| .agent-runs/continuation-1559/abstract.html | 3674e6335a0ad9530f611160214ed194781f3a95083d4c48db48610944735ade |

实际逐段读取固定txt字符区间 `[0,37800)`、`[60102,98718)`、`[123625,end)`，涵盖main §§1–8/Limitations、附录A–C/E–F、Tables1–26及范围内Figure1–17/27–29图注。文本为单行提取，采用字符范围而非伪造行号/PDF页码。直接抽查HTML的S6缺标签标记、A5.T18/A5.T20数值、A3.SS2 oracle选择段、A1.SS3单并发费用口径；直接读abstract缓存的citation标题/日期及Submission history（v1，2026-10-25 05:29:05 UTC）。这是固定缓存审核，无新增在线版本核验。

**未读/未验**：附录D `[98718,123625)`、参考文献正文、实际渲染图像、作者源码/原始实验数据、实验复现/统计重分析。图注阅读不等于读过图像；未对图内数值或视觉因果关系作认证。

先读取AGENTS.md与相关项目文档治理、伴读、知识接入、项目记忆工作流；按需读取独立审核/通信入口与相关边界。部分长工作流工具输出发生截断，因此不声称所有关联工作流全页覆盖。实际读取guide/README.md，GUIDE.md为空，整个guide目录保持只读。核对唯一TASK的SYSTEM-99未完成索引与SYSTEM-99 Plan Version54、当前相关Progress；本调用不维护任务或锁，不竞争主控所有权。父主控摘要不是本文事实证据。

## 原文核验与处置

| 项目 | 实际原文定位与核验 | 决定 |
| --- | --- | --- |
| 1轮/2轮参考 | §3 Table1标题/单元、§4.1及C.1/Fig10–12：主表差值对2rd，benefit/tax overlap对1rd。草稿明确区分。 | accept |
| 方法与范围 | A.1/Table4有40/200 PersonaMem、60/595 MINT及Luna 100/500 LME子集；A.2有turn/session chunk、BM25+dense去重/rerank、条件第二轮、Full Context截最早单元、两learned policy保留发布模型仅换QA。C.2 gold分析排除无gold题。 | accept |
| RS与预算 | A.4内容token曝光/可检索store归一、Qwen3.6 tokenizer、LLM检索时读入与未搜索metadata边界；B.3明确不等同绝对推理token。T18 Hippo1.28%低于RAG1.91%，T20 SimpleMem4.96%低于6.73%，T19也有MemoryOS1.36%低于1.48%。草稿没有将作者目标当硬满足保证。 | accept |
| 消融/配置 | B.1/Table6 BM25-only与Emb-only同时不rerank，不能单独归因hybrid；B.3/Table8 SimpleMem37.5→34.7、Hippo47.3→46.5；T7 Memory-R2默认79.6高于调整79.0。T9/T10的MemOS/LightMem仅选择性配置检查。草稿不宣称调参等价或普遍最优。 | accept |
| oracle与保真 | C.2/Table11–13：GPT-5.6 Terra与Claude Sonnet5得到query、answer、gold raw turn选单元，少量分歧人工裁决；A-Mem/MemoryOS/Hippo/MAGMA有确定映射。人工spot check确有extraneous/missing，不能把oracle gap唯一归为构建损失。另500 raw-turn人工注释对一对多用全部映射单元不经LLM过滤。草稿保留映射/包装敏感性及保真/检索分离。 | accept |
| accessibility/robustness | C.3迭代排除已取单元，graph/query refinement部分要重跑，median one-to-many similarity且并非所有retriever只按embedding。C.4非LLM retrieval固定证据，LLM retrieval换QA后重放。草稿没有把全部变化当纯QA敏感性。 | accept |
| 广化边界 | C.5/Table15：Q27B单backbone、LoCoMo去abstention、ES只QA、多模态caption化。C.6/Table16：train/dev experience与test freeze、top2 raw trajectory、BigCodeBench single-shot、Mind2Web offline gold steps。C.6.2/T17：不同world models、H100/50steps，非固定generator替换carrier。 | accept |
| 成本 | A.3为ingestion+QA全部LLM输入输出token，单并发等价time并保留endpoint浮动；E T18–20只三个dataset/backbone三元组，build/mant/infer与offline/online分列；C.6/T16体验库成本摊销。不是cache加权美元/物理RAM/全部工程角色成本，无法从短推理成本推总净收益。 | accept |
| §6尚未定位证据 | HTML S6两处确为`ltx_missing_label`空span，txt为Results in Table。所读范围未定位恢复/递归干预的量化表。草稿保持unverified，无补造表号或效果；D未读边界也明确。 | accept |
| 限制与因果 | Limitations明确非穷尽、进一步tuning、静态offline英文、费用限制/frontier与抽样。T5只有人类agreement比例，未建立样本量/重复区间/显著性或time归一公式。对固定参考的正确性集合分区是描述统计，不能独立识别具体memory操作的因果效应。草稿保留这些限制。 | accept |

未发现需要revise/reject的阻塞项。原论文存在图/表交叉引用不一致，草稿正确保留而未重编号；这不是本文可修复的作者原稿错误。草稿不声称观察了被排除的图或作者raw数据。

## 源码适用性独立核验

直接读实际实现，没有运行测试/实验或将源码注释当运行通过：

| 路径/位置 | SHA256 | 观察与处置 |
| --- | --- | --- |
| agent_runtime/knowledge.py，get/_metadata约260–295；context355–407；check_refs409–430 | eb17aab6668435d6dea09b4010cc2410fbd66844e60fcfb1bef4d4817971eb01 | get/_metadata计算声明先决闭包；context按完整bundle接纳，放不下整bundle跳过并标partial；预算是entry序列化字符非完整模型token；check_refs验published、版本hash、声明先决闭包，applicability unchecked。accept草稿的有限描述；不能据此证明先决声明没有遗漏。 |
| agent_runtime/handoff_basis.py，claim_graph/check_handoff_basis约84–188；basis_context270–末尾 | 20b4e127726f046b564086d2c5028ba92e986c6b796784a23cfe94971071f50a | 选择保留required claims、所有candidate/rejected及祖先，consumer必需refs和closure进入包；unknown/unsatisfied前提不能supported；known refs表示当前消费者已有而非磁盘已读；包主要有artifact引用而非正文。硬限/身份检查不理解语义。accept，真实宿主持有完整输入与声明充分性仍unknown。 |
| agent_runtime/artifact_context.py，compare_artifacts91–165、restore_comparison168–末尾 | e38f36b6a5a0a4f8b115b2ff478069ae938b30d046674b9d8e9e85b91a3fc40e | 完整base总在同包；比较读取hash绑定文件，恢复核对独立host root/before/after refs及重建hash；支持full/splice/edits/identical但不等于当前磁盘fresh或科学验收。accept草稿。 |
| workflows/project_memory_workflow.md | 4522bd15ed5ade12e40f2f18a2c4c840a2a8f539d8625fae0aef177ced7566aa | correction保留原始观测并使依赖解释stale，声明门禁不能发现隐藏依赖；暂缓自动递归写回/删账本与现有治理相容。accept。 |

附带输入版本核对：TASK.md `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`；SYSTEM-99.md `46faf3500551793008bd8850d7eb466adf544449393239387ec0468697523c6e`；GUIDE.md `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；guide/README.md `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`。固定输入匹配不等于源码无bug或运行契约认证。

## 实际知识检索与拒用

本角色实际执行一次只读检索（设置PYTHONDONTWRITEBYTECODE=1，不运行模型）：
`python -m agent_runtime.knowledge --root knowledge search 'memory retrieval evidence preservation context budget applicability' --limit 3`。
返回snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`，backend `files-lexical-v1`，applicability unchecked。随后分别执行show并读取三项的前提与内容；各requires=[]：

- algo.qlora-memory v1 SHA256 `08684e7e9ae88964f84a9d275990341f2ed28dc78ae3fc3affeef8319d6eead3`：NF4冻结骨干/LoRA、65B显存的对象不是agent证据memory，reject applicability。
- ds.hnsw-recall-budget v1 SHA256 `8f736520925598cd563890785a162bc50b45891506c859ab1685434dbd10d11c`：ANN近似向量检索折中不证明本库完整依据包/模型质量，没有当前HNSW对象映射，reject applicability。
- infra.flashattention-io v1 SHA256 `5699ccfeb1b8bc75fb1ad5f859efda45297ed41553b2332895df07b5334b70d9`：dense attention/HBM IO不是agent memory净收益问题，reject applicability。

这三项是检索到且核对过的知识身份，不是采用的理论保证；adopted knowledge_refs=[]，无有效理论命中，不用词法memory同词关联外推本文。未调用context/check-refs机器验收，也未声称执行了；相关函数已通过上述源码独立阅读核验。无需运行这些机器门禁来支持当前纯源码/原文阅读结论。

## 接受与暂缓边界

接受评价方向：同任务原始检索参照与memory路径做四格结果，分开保存保真、候选可达、完整依据输入、最终模型使用与全角色费用。它是后续评价要求，不是本库效果结论或新实验许可。

暂缓并行原始检索、递归写回、学习selector、频率降权/删记忆、agent_doc迁移合理。恢复需要本库真实宿主、留出任务、完整引用/更正链、完整模型输入、同条件最终任务质量与全角色费用的独立验收；本文未产生这些证据。

本调用仅写本文件，未修改其它文件/生产实现/指南/任务/锁，未安装、未启动后台进程、未新建实验、未运行任何测试或旧门禁/旧CLI/PID/模型probe。不得将纯检索/人工源审计计作实验模型调用。实际role invocation=1；experimental model/backend calls=0；test executions=0；all-role tokens/cost=unknown；历史登记/runtime/provider认证unknown。手工独审不替代可信runtime/provider认证。

同批27→28只能在主控公开发布与可恢复readback后把1559与1657合计为同一篇，不能各抵一篇；本文不自行更新计数，不关闭SYSTEM-99，不恢复任何旧耗尽预算。
