# Stratum — 2610.36153v1

实际精读2026-10-26版本全部可用正文I–VIII/II-A–C/III-A–B/V-A–B、唯一Table I/唯一Figure1图注、两处未编号公式（KV字节和S(v)）及31参考文献。无附录，未做PDF/图像像素审读。HTML119167字节和提取文本32710字符连续[0,14000)、[14000,32710)；精确原件hash见source.json。未读/执行作者复现包或实现，不能从摘要/本地缓存字数冒称provider token。

## 方法、假说与实装边界（II–IV）

E1六repo(Django/Flask/Redis/requests/scikit-learn/Vue)共17.6M cl100k_base token，文本70MB、4.17byte/token。十亿token文本约4GB、含索引约8GB；fp16/GQA的KV公式2×层数×KV头×head_dim×2byte，8B/70B/405B分别119/298/469TB。四五数量级只是表示成本推算，不是有人把repo常驻KV，也不是本库速度/账单对照；量化2bit仅缩一数量级。

E2在最新commit解析Python import graph，再按fix/bug/regression、非merge且至多20Python文件选最近至多300提交/repo，三repo752修复、中位2文件。一跳双向import闭包Django32文件/114532token/2.7%，scikit24/4.6%，Flask2/9.9%。它是代码结构代理，遗漏配置/运行时/文档/fixture；并非10%足够完成所有任务的实证。

E3加requests共852提交/3695共同修改文件对，直接import23.5%、任一方向传递可达52.0%、加测试名称52.7%，47.3%仍未连接。随机直接边0.9%（比例约26×）、传递16.3%。共改不证明因果依赖或阅读必要性；用当前图配旧提交有移动/版本漂移，关键词选样偏向明确描述的Python修复。

设计：本地SQLite typed graph存结构、历史co-change和agent经验(rca/失败)，HNSW384维近邻/文件hash watcher；控制分数S=w1G+ w2C+ w3时间衰减频次+ w4pin，15%空余触发淘汰、pin永留、邻居接口/暖节点摘要。权重与语义淘汰明确是未验证假说，不是已调优政策。9工具包含5读、remember写、3驻留控制；响应content/page/total_pages/has_more/remaining budget/提示，不静默截断。模型更换文本可用不等于embedding/排名无需重建，hash稳定也不保证实际前缀cache命中。

## 实验、消融缺口与负控（V、VII）

E4 CPU笔记本Core Ultra9/32GB/NVMe，百万synthetic节点约440Mtoken、500万边/384维、3.7GB、构建<4min。200次端到端向量k20+一跳+20节点读取中位1.70ms/p99 2.76ms，两跳中位0.95ms。仅规模/基本操作可行性，不含真实embedding检索质量、controller开销和持续更新成本。不能用该微基准代替coding成功率。

E5实装原型是SQLite lexical全文检索及4/9工具(tree/search/get/remember)，完整分页envelope；不是E4向量版本或完整控制器。8真实requests/Flask bug、修前树、删路径的症状，成功只要求命名人类修复涉及的root-cause文件，不是生成正确patch/通过测试/新任务迁移。Session1 Sonnet writer调查同一症状并写rca/failure，reset后不同较小Haiku reader。A保留全文lexical但去notes，B加notes，均3trial/task；P把全部8调查26notes混合、1trial；C整repo单次上下文且无工具、2trial。模型精确版本/全部配置以正文给出的粒度为限，未从名称猜版本。

Table I: A6/24、median18calls/6.5reads/196.6K input；B21/24、9/5/43.3K；P8/8、8/4.5/41.7K；C14/16、164.4K input/call。B相对A约4.5×较少reader input，C/B约3.8×但C是单call且工具条件不同。writer每任务median83K token、全8成功，未计入43.3K，真正多会话摊销、所有角色/输出/缓存费用仍未知。P pooled结果只一次、26个有限notes，不证明长期累积永不退化；B中IPv6题2/3失败而P该次成功不能归因其他notes。

作者单侧Fisher p=1.3×10^-5将24trials汇总；同8题重复试验有cluster/配对依赖，不能据此推独立跨任务样本量24、普遍p或成功率等价。B/C同87.5%是观察比例而非非劣检验。writer全成功且未控制notes质量，缺plain-session-summary对照；A lexical非embedding、模型大小不同和同症状重诊断限制结论。没有隔离page envelope/negative notes/co-change/semantic score/eviction的组件消融；RQ1–5未来计划明确待验，不写成已证效果。错误note污染、web写回注入、摘要忠实性、team共享也是未来缺口。

## 与本库关系及取舍

采用评价问题：现有MemoryLedger的失败/更正与定向交接能否在真实独立会话减少重复工作；分页范围/剩余项是否明确；比较任务包/只读活跃视图与全量读取时同时查依赖、更正、异议和最终任务质量。复用既有ledger/唯一TASK/导航，不另造Stratum池或可编辑任务链。源码图闭包不是语义充分性，hash freshness不是自动更正传播，已公开的旧负结果/冻结边界必须保留。

暂缓导入HNSW/新MCP服务/语义LRU/主动淘汰和重大agent_doc迁移：作者原型未验证核心评分，且本库没有同条件真实质量/成本数据。设计对本库仅候选假说；本次未生产改动、未实验复现、未测性能，不把43.3K输入或1.7ms迁作本库收益。真实宿主加载/全输入/终局质量/全费用/并发恢复仍open；同一SYSTEM99不新开轮。

独立复核待完成，本冻结稿0credit。正式结果检索371扫描/26错误/partial=false无候选，仅未注册新包增加错误等仍可见；不宣称全历史无此前读取，不以相似标题复用旧验收。作者复现链接doi:10.5281/zenodo.23615180已定位但未打开，不声称已核查数据/代码。
