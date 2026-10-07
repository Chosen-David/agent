# 工程持续学习：两栖类细胞类型与同源边界

北京时间2026-10-07，轮次122522；核查5类来源，新增1张candidate，新增published科学卡0张。补充方法与供体层级尚未核完，不强行升级。没有动物实验、作者R代码执行、GPU训练、模型A/B、AI意识测量或模型权重修改。

## 任务、版本与实际运行

对应根TASK的EK-122522-01–03，主AI唯一作者，无委派。宿主先同步，启动`git status --porcelain=v1`无输出；本地HEAD、连接GitHub main和独立只读REST均为`907890831929a5d200d3fb64c6299449391a1ee8`。输入哈希见[inputs.json](inputs.json)，覆盖AGENTS、TASK及九项所要求的知识入口/目录文件；最近115246报告与验证记录已读，历史失败不改写为本轮成功。

决策EXECUTE；按用户“先补新增神经科学缺口”选择两栖类细胞类型。已有priority.next_domain=reinforcement-learning保留，下一轮RL，再概率论，再神经科学；数学顶层游标/history/open_questions、RL/概率待研主题、工程AI Infra→AI算法→数据结构队列均保留。

私有DAG经agent_runtime.core.validate校验，review→verify→publish有依赖、证据谓词、最多2次尝试与2700秒上限。该计划不是模型适配器部署。本轮读取既有维护live.json，active_round=`20261007-122343`、pid=61281、runner_pid=61295、interval_seconds=3600；本地文档轮次122522是产物ID，并非另一个调度任务。读回只说明现存心跳文件，本模型未独立验证WSL进程/tmux pane，不宣称启动新monitor或保证未来唤醒。宿主原桥管理固定周期、互斥和轮末对齐；本轮不增加Agent、调度、付费/API/GPU资源，不写.git、不执行本地fetch/commit、不改权限或SGLang。

## 来源、读取范围与采用/拒绝

[sources.json](sources.json)记录实际URL、读取版本、SHA256对象、日期、私有缓存与取舍。五类是研究论文、作者源码/归档、机构说明、作者出版索引和另一篇2026论文的元数据；一个仓库的多个文件不是多次复验。全文/源码不镜像入公共仓库。

| 来源 | 实际核查 | 处置 |
|---|---|---|
| [Woych等，Science 2022](https://doi.org/10.1126/science.abp9186) | 正式发表2022-09-02；实际读PMC10024926作者稿的NCBI BioC XML，完整对象SHA256 `085a72b9c7dfffc79b3e7cbae4d4d2a7dc5c5d829aa3746d15a03ca07df2a418`；Results/Figs1–6图注、Discussion、Methods summary、data availability | 写candidate；单独补充Methods/Text、S1–S19和电影未读，终版差异未核 |
| [作者代码](https://github.com/ToschesMA/Salamander-telencephalon/tree/6ffbcbe5e6071bb3d0c333d959e4b0ef8d920921)与[Zenodo6780577](https://doi.org/10.5281/zenodo.6780577) | commit `6ffbcbe5e6071bb3d0c333d959e4b0ef8d920921`、完整tree `6b2d0a4c9be1a69475b51e9b4b2d668e3479b38b`，truncated=false；读6文件，含空开发README。归档v1.0.1日期2022-06-29，绑定预印本 | 不采用实现卡；明确许可、依赖版本、输入/参数与终版代码对应未核；local_execution=not-run |
| [Columbia机构说明](https://biology.columbia.edu/news/new-paper-science-tosches-lab-describes-neuron-types-salamanders) | 2022-09-14，完整可见文章；哈希针对私有web响应JSON，非HTML | 解释与导航，同论文宣传不算独立实证 |
| [Tosches作者出版索引](https://www.tosches-lab.com/publications) | 2026发表/预印本分栏；发现July2026 water-to-land预印本链接，全文403 | 近期候选导航；不从题名或索引提炼实验、不称已正式接收 |
| [Gumnit等2026 Current Biology](https://doi.org/10.1016/j.cub.2026.03.082) | EuropePMC元数据确认在线2026-04-22、36(9):2397–2412.e7；另有2025预印本DOI，期刊原文无法读到 | 仅来源candidate；机构解释不替代原始结果/方法，不确认Reelin跨物种因果结论 |

五年窗口2021-10-07至2026-10-07；2022论文补历史缺口，不包装成最近新发表。近90天2026-07-09至10-07检索及作者索引找到`10.64898/2026.07.25.740661v1`线索，但实际posting date、实验与接收状态未核。日期过滤也返回旧文，不声称穷尽。未筛查本轮不依赖的RL/概率2026会议论文；留下一轮，不将未确认NeurIPS投稿称发表。

EuropePMC全文XML先500、HTML403，NCBI BioC正常取得作者稿；Science独立补充PDF与bioRxiv全文403后停止该路径，不关闭TLS校验或无限重试。作者稿仅有text-mining/fair-use说明，仓库未发现明确代码许可，公共产物只写原创事实摘要和核查边界。

## 候选观察、前提与实现诊断

新增`neuro.salamander-cell-type-homology@1`为candidate、source=unverified、local_reproduction=not-run。原稿Results/Fig1的36116质控细胞、29294分化神经元及47/67谷氨酸能/GABA能cluster不能算动物重复数。样本包括变态后P.waltl与36/41/46/50幼体，Fig3为20261端脑细胞；性别、动物数与合池尚需补充表，不能将不同阶段合为同一状态。

主文结合HCR/ISH、iDISCO light-sheet空间定位、发育计算轨迹与ex-vivo示踪。Fig2的200/50/500µm是比例尺，非体素尺寸；Fig6图注的VPa/MP/LPa n=4/2/2不相加为独立总动物数，24–48h示踪不是行为干预。GPU dtype、LLM长度/batch不适用于这些动物组织测量；scRNAseq硬件/软件精确版本与原数据快照未核，不能填默认值。

Fig4的65整合群支持比较分子特征，但共聚类既可能来自共享调控因子，也可能是趋同效应基因。Fig5未映射群不证明物种绝对缺失细胞；正文还保留祖先状态/次生丢失等替代解释。Fig6解剖投射不能单独证明功能等价，伪时间不是谱系追踪。Harmony/SAMap/scVI敏感性在正文有报告，本轮未读S11/S12/S17，不冒称核完消融。其他物种既有数据及同数据多算法不算独立动物复验；本轮未审计与2026文章数据重叠。

源码核查的一对一ortholog计数→SCTransform v2→CCA anchors/IntegrateData→Spearman距离/Ward.D2与论文主流程相关。三物种脚本nDims=80、ngenes=2000是该脚本参数，不能代表所有图或运行；包含HPC绝对输入路径。label_transfer模板有空readRDS和未填date等参数，API需输入Seurat对象/ortholog映射及供体字段。taxonomy笔记的距离函数与独立脚本修改版不同，并记有workaround，不能假定入口等价。完整tree无LICENSE/COPYING、已读文件无授予；Zenodo other-open不能代替具体许可。未安装Seurat/R、未执行作者脚本或复算统计。

候选可支持补读/供体层级/整合敏感性任务安排，减少“表达相似即同源/同功能”的重复探索。AI共享核心与可分化模块只是待验证假设：等参数、数据、交互/计算预算对照完全共享、完全独立、随机分组、生物启发分组，冻结未见误差和遗忘；随机分组或完全共享相当即拒绝特定分组收益解释。没有AI收益、意识或权重变化结论；显式复现和用户必做实验仍须执行。

## 真实验证及局限

结构查询“两栖类 细胞类型 跨物种 同源 分子 发育 连接”先命中鸟类、小鼠和麻醉卡，全文已读且按物种/测量差异拒作蝾螈证据；见[knowledge-use.json](knowledge-use.json)。不直接命名方法的问题“两种动物的脑细胞表达相似，怎样区分共同祖先和独立演化？”在files/SQLite分别保存实际结果；相关鸟类卡可提示边界，但没有已验证两栖类答案。新candidate在search/get/decision均隔离。

既有熊蜂卡仅检查接口：缺条件→insufficient_context、匹配→reuse_for_planning、错误物种→minimal_transfer_check、显式复现→run_requested_experiment，均automatic_skip_authorized=false。真实refs与算术47+67=114、29294/36116≈81.11%见[verification.json](verification.json)；后者仅该质控集合细胞比例，非动物或全脑比例。

7套目录×两后端逐题排序和上下文（排除耗时）与干净基线完全相同；工程、RL/概率、神经科学、熊蜂Recall@3/MRR/context recall仍1。旧基础Recall@3=17/21，round2=0.75，morphology文件=0/SQLite=0.5；三目录原始退出1和漏检全部保留，不删除测试或调整指标。验收是非退化，未修复历史漏检。

知识validate通过77记录，其中75published/2candidate；插件生成/闭包、SQLite派生索引重建通过。相关unittest为reuse7、基础数学5、plugin1共13项通过；Reader3项通过，使用已有私有PyMuPDF依赖，无新增安装。真实命令/退出码/耗时/日志见[checks/final-commands.json](checks/final-commands.json)。本轮未改运行时或共享Prompt，未运行POSIX相关全仓suite，不冒称全仓或GPU性能通过。作者脚本构建顺序及验证limit参数两次设置错误已修正，保留[失败记录](checks/review-failures.json)。单模型自编检查不是独立盲测、科学复验或形式化证明。

## 状态、发布与下一步

coverage不因candidate消除缺口；learning_state只追加本轮工程/神经科学历史及priority证据，数学和其他队列保持。下一owner为既有小时维护主AI，先筛2026正式接收RL探索/信用分配/离线评估原论文；之后概率论。神经科学待补Science补充供体/性别/合池与S11/S12/S17/S18/S19、终版差异、CR2026及July预印本全文，AI迁移未测。

发布前再次读回main并整合并发；GitHub create_tree/create_commit、expected_sha/force=false发布，通过完整工作文件树与immutable远端树比较、API main和独立git ls-remote核验后才完成03。发布回执另记，避免在提交内自指自身SHA。宿主在模型结束且全部工作文件与远端树相同后才对齐Git元数据和轮间同步技能；本模型不宣称完成这些宿主动作。
