# 2610.39790v1：双记忆互补与巩固的取舍

《Long-Term Agent Memory through Complementary Curation and Consolidation》，实际HTML页眉2610.39790v1 [cs.AI]，2026-10-29，Microsoft作者。完整阅读主文1–7/所有子节、参考文献、附录A–E、六表、Eq1–4、两图图注及两个完整curation提示词。图表数值以正文/表格为据；没有PDF逐页/像素审读或图2曲线点读数。HTML许可CC BY-NC-SA4.0，未复制作者代码或部署提示词。

## 方法与实现（§3、附录A–C/E）

离线三阶段：每次会话结束分别整理episode与relation，周期性离线巩固，再检索回答。Episode含title/summary/details/timestamp，索引details一向量；relation为(e,r,o,t,c)，对象关系附时间和上下文，索引拼接自然语言的tuple一向量。两个平面存储分别语义检索，不是知识图遍历，也不是本库不可变依赖账本。source context是抽取的描述，文中未给本库所需原文件hash/稳定事件ID、独立接受或自动完整依赖发现证明。

§3.3主方法每问取k个episode及2k个tuple，默认k10，理由为tuple较短。条目比2:1不保证精确相同token预算；正文§5.2称改变“两种记忆的k”但没有在该节逐项重申2k规则，应保留预算定义，不能改称总共10条或固定10token。没有显式重排序/纠错closure/最新修订优先的完备算法。

§3.2/Eq1–4：embedding聚类后，把同cluster内容交给LLM MERGE互补/冗余项、DELETE过时/冲突/被替代项，最后合并各cluster输出。附录C：text-embedding-3-small 1536维；UMAP cosine/n_neighbors10/n_components5/min_dist0；HDBSCAN Euclidean/EOM/min_cluster_size10/min_samples1。文中没有完整巩固prompt、离群/noise处理、合并后来源/依赖/版本映射或删除回滚规则，不能由集合式子推断生产实现的事务安全。相似不代表等价或过时，保留旧事实可能是回答过去时点问题所需；不能把“冲突”自动当无价值证据删除。

附录A：要求完整episode，又说优先细粒度；保留精确名字/数量/引语/感受，按会话日期计算相对时间。附录B：尽量穷尽triplet、代词实体化、防名字/物种混淆，强制尽力推日期，拿不准也倾向保留，context用于grounding。两个prompt是抽取规范，不是事实或时间算术正确性的独立证明；相对时间歧义/近似推断需保留原话与不确定性。A含图像caption/可见文字指令，但§7实际评测仅文本，不能称验证了多模态。B示例JSON末尾逗号属于提示词示例，未读实现不指控实际解析错误。

附录E将平面双存储与图/层级、逐turn CRUD/预测误差distillation区分；称session级摊薄抽取、固定topk省query额外LLM、巩固可每10–20sessions。是作者设计理由/例子，没有给完整调用账本或实际调度频率，不证明全部阶段便宜，也不证明“single session pass”只有一次LLM调用（两种curation仍分别定义）。

## 实验、指标和主结果（§4/Tables1–3）

LoCoMo1540QA/10对话/四类（不含adversarial类），平均24K对话token；LongMemEval-S500问，正文称平均115K history。以gpt4.1mini和4omini负责整理/巩固/回答、embedding如上。Table1说明LangMem/Mem0/RAG/Zep/Nemori基线取自Nan2025，非本次一套环境全部重跑；版本、提示/检索/价格/硬件/seed差异无法由排行榜排除。未见精确judge版本/完整评分prompt、重复次数/方差/置信区间及训练/验证独立调参划分，不能认证统计显著或普遍非劣。

主指标LLM Score与F1/BLEU必须分开：4omini总体ours .835、full .790、Nemori .744；但F1/BLEU ours .377/.274低于Nemori .495/.385。4.1mini总体ours .902，full .913更高；F1/BLEU ours .354/.249同样低于Nemori .534/.456。不能照抄“所有baseline/所有指标/所有类别均胜”。4omini singlehop .765低于Nemori .821和full .804，temporal .888低于full .903；4.1mini multi .872低于full .878、open .697低于full .781。粗评分提高不替代本库任务行为正确与独立验收。

LongMemEval-S Table2（4.1mini）：总体.855 vsNemori.746/full.656；preference却.500 vsNemori.867，assistant .982等于full .982（Nemori.929），temporal.858、multi.801、knowledge-update.902、single-user.953。总体强不表示偏好保留可靠。表中的上下文full101K、Nemori3.7–4.8K、ours3–6.9K，不与正文平均115K强行当相同token定义；范围/历史长度/模型实际输入如何对应未充分说明。

Table3明确4omini，每问平均Tokens：full21788、Nemori2745、ours2738；LLM Score.790/.744/.835。+9.1pp是相对Nemori的评分，约87%少token的已列数据来自这些问答token，不能把它说成4.1mini完整费用实测；§4.2在4.1mini结果旁称87% fewer tokens，但未单列同模型token表。不含所有整理/embedding/UMAP/LLM巩固/重试/检索存储成本和墙钟，不能把少entry或QA token直接当全链token/价格/latency收益。

## 消融与负结果（§5/附录D/Tables4–6/Figure2）

Table6组件：4omini episodic .776/relational .730/hybrid .835，multi .710/.750/.813，相对较强单项+6.3pp；temporal .820/.757/.888，+6.8pp。Single .765与Open .645只等于episodic，没有提高。4.1mini episodic .871/relation .837/hybrid .902，multi .847/.831/.872（+2.5pp）、temporal .918/.882/.952（+3.4pp），single +3.6pp/open +1.0pp。两路各有配额，单路与双路是否严格同token/生成预算未明；因此这些结果支持当前配置互补，不能将全部收益严格归为新表示而无额外证据预算因素。

巩固不是无损：4omini总体.835→.823，multi .813→.764、temporal .888→.875、open .645→.625，仅single .765→.797；4.1mini总体.902→.892，temporal .952→.934、open .697→.666，single .858→.861/multi .872→.878略升。不能照引言泛称巩固同时改善两个模型single/multi；4omini的multi明显下降。绝对1.2/1.0pp下降与相对百分比不同，正文“only1%”须限定口径。没有统计检验，不称无质量损失。

Table5 mcs2/5/10/20：条目compression30.9/21.7/16.3/9.6%，score .876/.896/.892/.898，clusters2208/693/325/144。较大mcs簇数/调用变少，压缩率单调减，但质量并非单调；mcs2相对未巩固.902下降2.6pp。默认mcs10的16.3%是作者所称memory store规模压缩（操作为条目合并/删除，原始计数未列；正文16.34%更精细表述），不是已测token、字节、时间或完整cost减少。cluster调用数量比例约15倍不证明墙钟15倍；缺每cluster大小/LLM输入分布、并发和完整计费。选择mcs5/10的权衡需真实质量约束，不能自动推荐最压缩的2。

Figure2正文：4.1mini k2已有.811，k10后plateau，k10→20<1pp；未读取曲线像素/隐藏点，不补其他k数值。同一基准上观察plateau选k10，不等于全任务最优或独立holdout泛化。Table4 gpt5.4/.906、4.1mini/.902、4omini/.835、Qwen3-8B/.762；gpt5.4 temporal .941低于4.1mini .952。骨干换动同时影响curation/consolidation/QA可能性，不能由接近的两个分数证明memory设计是唯一瓶颈或小模型无退化。

## 局限、来源与本库关系

§7承认只测文本、整理质量对骨干敏感（4.1→4o总体少6.7pp）；没有真实动作完成、工具失败、并发改写、在线纠正传播、重启恢复、许可/权限边界和多角色分工验证。QA提示已显露检索需求，与前一篇DolphinBench动作评估不同，不把两者分数/成本直接比较。参考文献只读本论文书目，不抵算其他精读。可用HTML未给作者实现链接，出现的LangChain链接是baseline非作者代码；未固定/读取/执行作者源码、数据或实验，不能认证可复现性/源码对应。

采用的仅是评价假设：今后同条件测试可拆开叙事/关系证据作用、严格统一token预算，固定默认/更高压缩的终局质量损失与全部阶段成本。复用当前MemoryLedger的immutable entry/显式修订/stale传播及按需定向交接。它是审计账本而非LLM语义记忆服务，不能为了相似聚类把原观察/冲突/历史撤销删掉。暂缓自动MERGE/DELETE、两份竞争memory权威、新embedding/聚类后台和agent_doc迁移；任何重大变动仍需有证据版本方案与用户对齐。没有对本库作模型或性能实验，没有生产改动，只有这一篇新正文待独审；旧全部冻结边界/失败与缺失原件不因此改变。
