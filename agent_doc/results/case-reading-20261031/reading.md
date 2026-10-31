# CASE — 2610.38800v1，When Relevant Code Is Wrong

实际精读2026-10-28 v1全部可用正文I–VIII/所有段落、Data Availability、20条参考文献、Eq1、TableI六行四指标、Figure1图注。HTML100921字节/提取全文30496字符连续[0,15500)、[15500,30496)；无附录，未审图像/PDF像素。精确原件hash和作者仓库固定版本见source.json。全文读记不等于作者实验复现。

## 方法与条件（II–III）

区分主题相关R(a,q)与部署d/时间t下的可执行参考适用性V(a|d,t)。Eq1用带时间戳证据E支持前提π则valid，支持否定则invalid，缺失/冲突unknown；需要足够权威、无冲突的证据，不因trace没出现而判停用。历史真实可保留为解释，但不因此适合作当前实现蓝图；区域回滚可以让同一旧REST在US无效而EU有效。来源、时间、scope和冲突要保留，不能机械“新优旧删”。

CASE从共同top-k候选建版本化上下文图(artifact/implementation/flag/deployment/service及guards/deployed-in/calls/supersedes)，用配置/清单/PR及有限开发者核对映射判断适用性；条件可能是cohort而非全局on/off。打包Act On有效、Verify未知、Explain过时/不兼容历史，保存指针/适用范围/时间和重要未决约束/测试。声称约1500token预算，不微调模型或自动改生产；核心同模型/候选/预算下减少不兼容实现是待验证假说。

## 实验、消融与局限（IV–VIII）

Java/Spring Boot merchant-trust是作者构造的合成示例，受真实市场平台案例启发，不是生产观测数据。15artifact/3部署/6任务，迁移、flag区域、稳定各2；时间只取当时已存在材料。US迁到GraphQL，EU又回滚REST，APAC cohort不明。BM25给每题top8候选，虽然条件名叫Semantic Only，实际为lexical，不能写成强embedding检索对照。

四条件为全候选当actionable、180天新近过滤、加原始配置但不作适用判断、CASE，另去Flags/去Lineage两个消融。所有条件共享候选/近似预算；前两类不分section而CASE只有Act On计actionable。P/R是六任务非加权均值；不兼容/未知是可执行artifact出现次数之和，不是独立artifact数或agent失败数。

TableI: Semantic Only P=.50/R=1.00/Inc16/Unk5；Recency .43/.43/6/5；Raw Cfg .50/1.00/16/5；CASE 1/1/0/0；w/o Flags .33/.13/0/0；w/o Lineage 1/1/0/0。EU回滚题新近保留4条全不兼容。去Flags把原可执行变未知、召回降至.13；去Lineage没有效果，因为fixture的Flags已决定全部路径，不能宣称迁移谱系有已验增益。固定repo请求换部署，Act On由US GraphQL变EU REST。原始配置条件只是不调整选择指标，尚未运行agent去判断它能否自行推断。

关系/前提人工整理，reference labels与evaluator同规则，作者明确完美P/R在fixture下预期，不是独立ground truth或泛化。没有下游编码agent/正确补丁/终局质量/用户任务成功/成本提升实验。没有模型调用、统计置信区间、多seed或大规模现实配置测试的证据。构图/维护/检索成本、配置冲突/unknown的代价、完整上下文传输和全角色费用仍待。稳定组件预计少收益是预期而非已量化效应。

## 作者固定仓库补充核对（非执行）

正文ref14确切链接rameshperiyathambi/case-merchant-trust。固定commit cc6129363e87e5d44b1478785667e397b3f25b08、tree51d9cd265b6fbe445435a19bf59fb505e2532c63，2026-10-23T01:18:37Z。实际只读递归目录清单、完整README6707字节及docs/metrics.md3101字节；两文件本地Git blob SHA1与固定tree一致，SHA256见source.json。未读Java实现/原CSV/标签/全数据或运行Maven/服务/作者agent。

README明确数据虚构、没有附带agent运行、人工映射/同规则oracle、BM25弱对照；许可待法律复核，未复用代码。metrics明确P在零actionable时记0，六题macro平均，解释去Flags虽Inc/Unk为0而meanP=.33并非矛盾；不能以汇总倒推出每题分母。它还明确所谓tokens为characters/4加固定60header估算，不是实际provider tokenizer或已加载输入。本库不得据此将1500或字节大小作真实token。未验证代码是否完全实现文档，仓库早于预印本，版本对应只到作者链接和已读文件，不宣称完整复现匹配。

## 本库关系与取舍

采用后续审核问题：ResultStore词法命中、MemoryLedger active、更正/依赖哈希、advice新近/导览都不能单独证明当前部署适用或授权；unknown需留给当前任务，而旧异议/失败/历史应按既有来源保留。复用现有知识/结果门禁、定向交接、唯一TASK和只读导航，不造第二任务池/全局可写聊天层。

当前Codex安装器候选是独立入口有界读取/合并大小防护，与CASE分类算法无因果关系；即使该修复验收成功也不能称CASE论文带来性能提升。暂缓导入CASE图/自动配置推断/三分区schema或重大agent_doc迁移：需真实宿主/配置范围和同条件最终质量证据。读记只筛选假说，不授予执行权限；论文原型的完美选择指标不关闭本库真实加载、并发恢复、全输入/质量/费用和旧Windows/FD等缺口。

独立复核待完成，本篇当前0credit；保持SYSTEM99同一批次，不重算旧63或用摘要抵十篇。既有检索372扫描/25错误/partial=true，三个词法候选均无可复用CASE数据，不当全历史不存在的证明。
