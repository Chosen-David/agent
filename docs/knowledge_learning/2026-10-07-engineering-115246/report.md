# 2026-10-07 工程持续学习 115246

本轮核查4类来源，新增1张版本1候选 `neuro.cephalopod-arm-segmentation`，新增published科学卡0条。章鱼/鱿鱼腕部结构主文已读，但关键补图和原始定量数据未核验；吸盘神经节研究另留来源候选。作者分析代码固定到40位commit，许可不明且有待核对的SEM分母，未采用为实现卡。默认检索仍为75张已发布卡，另有1张candidate。无动物实验、作者代码执行、GPU训练、模型A/B、AI意识测量或权重修改。

## 授权、任务与实际运行

对应根TASK的EK-115246-01–03，主AI单一写入，无委派。启动时 `git status --porcelain=v1` 无输出；本地HEAD与连接GitHub读回main均为 `2e854cac85a6f69e3a15926173896fae74d8b7f6`。输入文件实际SHA256见[inputs.json](inputs.json)，覆盖AGENTS、TASK、知识README/FORMAT、coverage、learning_state、upstreams、engineering_sources、neuroscience_sources。最近11:24轮及宿主恢复报告已读；保留历史失败，不将宿主恢复回写成原runner成功。

决策EXECUTE；按本次“先补神经科学缺口”核查腕部控制，已有priority.next_domain=reinforcement-learning保留，之后按神经科学→RL→概率论轮转。数学顶层游标、history/open_questions，RL/概率论next_topics及工程后续AI Infra→AI算法→数据结构队列不覆盖。原有神经科学缺口不因candidate而勾销。

实际维护live读回的active_round为20261007-115246，interval_seconds=3600，有Windows进程alive记录；只证明该次读回，未独立检查WSL/tmux pane或未来唤醒。复用既有调度，不新建/停止监控。私有DAG通过agent_runtime.core.validate，review→verify→publish三个节点分别有证据谓词、依赖和最多2次尝试；这是计划校验，不是假装runtime注册了模型动作。宿主桥拥有本轮45分钟上限、固定周期与轮末对齐；本模型不写.git、不fetch/commit、不修改权限，不触及SGLang。安装技能由宿主在远端完整树验收后、两次运行之间处理。

## 来源层级、日期与读取范围

[sources.json](sources.json)保存URL、哈希对象、私有缓存位置、采纳/拒用理由和读取范围；下载全文/原图/源码不镜像入公共库。

| 来源 | 核验版本 | 处置 |
| --- | --- | --- |
| [Olson等，腕部神经分节](https://doi.org/10.1038/s41467-024-55475-5) | Nature Communications 16:443；接收2024-12-09，发表2025-01-15；PMC11736069 XML SHA256 `9168ea613daf461692981c3b5989e8495eb15185edca5e11a006ddd54f496e4b` | Results/Figs1–4图注、Discussion及相关Methods已核查；Supplementary Figs4–7、Reporting Summary、Source Data待核验，留candidate |
| [Olson等，吸盘神经节](https://doi.org/10.1002/cne.70055) | Journal of Comparative Neurology 533:e70055；XML在线日期2025-04-28，期号2025-05；PMC12036646 XML SHA256 `b285f4e97725d74c582bc4f90c1783c3f5a2f89cc3c61b108cc1857850b70388` | 阅读相关分子结果/Figs3–7、Discussion、动物/图像/近远端/神经分析方法及Fig8；完整视频/原始示踪和数据重合未审计，来源candidate |
| [UChicago机构说明](https://news.uchicago.edu/story/uchicago-scientists-reveal-nervous-system-secrets-give-octopus-arms-their-incredible) | 2025-01-23；哈希为私有web工具响应JSON，非网页HTML | 解释与导航；同论文宣传不算独立复验，功能平滑或进化最优表述不当实测 |
| [作者分析仓库](https://github.com/olsoncs/Neuronal-Segmentation-Cephalopod-Arms/tree/c8f1b836c1fe196874ab76da688f686a21ae3400) | commit `c8f1b836c1fe196874ab76da688f686a21ae3400`；完整tree `9eb0e6691bebf8b525d8f9f1ea05e928cf5793bb`，truncated=false；实际读5文件 | README、Measurement说明/GroupAvgSem、NerveAnalysis说明/functions；接口及许可检查后拒用实现卡，local_execution=not-run |

窗口2021-10-07至2026-10-07，所选原始文献属补缺的2025年研究，不包装成近期新论文。按2026-07-09至2026-10-07检索该窄主题，未核验到新的近期生物原始结果；日期过滤仍返回旧文和2026软机器人线索，未读取后者完整实验，不纳入本轮4来源或宣称穷尽。RL/概率论2026正式接收原论文筛查留下一轮；没有把未确认NeurIPS投稿称发表。

Springer补充PDF经普通TLS下载出现UNEXPECTED_EOF，web工具也不可访问；没有关闭证书验证或无限重试。缺失材料阻塞科学升级，不阻塞如实登记候选。两篇论文许可均记录CC BY-NC-ND 4.0，本轮只写原创事实笔记，不转载、改图或翻译全文。

## 候选观察、条件与拒绝推断

腕部研究是固定组织染色和解剖示踪；不是同时神经/行为记录。成体O. bimaculoides双性别、至少6个月，Methods分别记17只固定灌注、13只示踪和5只6周幼体血管示踪，批次重合未知，不相加成独立样本总数；比较D. pealeii为3只成体。性别没有分层效果验收。

近远端计数只用了两个个体各一条腕，每腕3个组织块，一腕acTUBA、一腕H&E。Fig1g两腕分别7.64/7.88段每吸盘，Fig1h n=48/condition是宽度测量，不是48只动物，个体与染色方法存在混杂。主文不支持“每段都是相同完整控制器”；不同出口覆盖不同肌肉区域，功能协同仍需干预。Fig3i 68%/32%与正文近似65%/35%分开保留，原始数据未复算。角域覆盖不是突触数、表面积、运动成功率或意识整合指标。

吸盘论文方法2.9明确复用前篇的吸盘宽度测量，不能把两篇尺度分析当独立重测；其13只成体固定灌注、少数whole mounts与3个神经节的出口分布不是大样本功能实验。部分GAD/VIAAT/DRGX标记未检出且其他组织阳性，是有对照的染色观察，不证明所有抑制/感觉通路不存在。局部反射、ANC协调与定向功能仍是解释/假说。两篇都未提供AI收益或意识证据。

采用卡中记录软件FIJI 2.1.0/1.53c、SNT 4.2.0、Matplotlib 3.7.3、MATLAB 2021b及原文显微设备位置；体素尺度、各图完整样本表、数据dtype仍未核验。GPU/LLM长度/batch不适用于此动物组织学。local_reproduction始终not-run，源数据统计与动物实验未执行。

源码检查：GroupAvgSem按组筛选数据，但SEM分母取完整逻辑标签向量长度；实际调用路径、数据形状和论文受影响范围未知，不能据此宣布论文统计失效。rootTip返回全部节点的均值位置，不能读成末端平均；unitVector只归一化前两坐标，第三坐标原样保留，不能直接当完整3D单位向量API。模块导入初始化ImageJ，本轮未导入执行。完整固定树未发现仓库级LICENSE/COPYING，已读文件也未提供许可授予；不抽取复用、不安装MATLAB/PyImageJ。README运行时间是作者预期，非本机测量。

独立自选算例244.8°/360°=68%。四值分两组的例子中，每组[0,2]或[10,12]，组内标准差√2，按组样本数计算SEM为1，而以全部4标签作分母则0.7071。仅核对算术与静态疑点，不是运行作者代码或重建原图。

候选支持补读任务、重复单位和接口诊断，减少盲目类比或未经许可的代码移植。AI启发明确为待验证假设：等参数/交互/计算预算比较相邻耦合、无耦合、随机耦合和集中控制，冻结未见形变/负载任务、误差/能耗指标；随机耦合或集中控制相当即拒绝特定生物拓扑收益解释。无训练预算对照、本机迁移或收益验证；显式复现和用户必做实验仍须执行。

## 真实检查与未修复项

查重结构问题“软体 腕部 控制 分段 吸盘 神经连接”实际命中小鼠、果蝇结构和章鱼睡眠卡，物种/测量/任务不符，未作为腕部结论证据，见[knowledge-use.json](knowledge-use.json)。自然问题“一条柔软的腕怎样把局部运动协调起来，吸盘之间的空间关系如何保留？”不命名方法；files/SQLite返回鸟类与麻醉相关卡，记录为未覆盖，绝不称检索成功。candidate在search、get默认入口与decision均隔离。

用既有熊蜂published卡检查缺条件→insufficient_context、匹配→reuse_for_planning、错误物种→minimal_transfer_check、显式复现→run_requested_experiment；全部automatic_skip_authorized=false。实际refs记录在[verification.json](verification.json)，仅用于接口边界检查，不给头足类候选背书。无需形式化证明；单一模型核查不是盲测或独立科学复验。

修改前后各运行7套检索目录。工程、RL/概率论、神经科学及熊蜂目录两后端Recall@3/MRR/context recall均1；旧基础Recall@3仍17/21，round2仍0.75，morphology的files仍0、SQLite仍0.5。三套旧目录原命令各以1退出，原始失败指标/日志完整保留，未调整默认参数或删除测试。逐题排序、上下文结果（排除耗时）与干净启动基线完全相同；本轮维护验收为非退化，不宣称旧漏检修复。完整指标和比较见[verification.json](verification.json)，可复跑[verify.py](verify.py)。

知识结构validate通过：76元数据条目，其中75published/1candidate；插件生成/闭包检查、SQLite重建通过。相关unittest：reuse 7/7、原基础数学5/5、plugin snapshot 1/1，Reader 3/3。Reader复用上一轮已安装的私有PyMuPDF 1.28.2路径，没有新增安装或全局设置。命令、真实耗时与全日志见[checks/final-commands.json](checks/final-commands.json)。本轮仅变更知识/来源/报告/快照，未改共享Prompt或运行时代码；未运行POSIX相关全仓suite，不以相关单测冒称全仓或GPU性能通过。

## 状态、下轮与发布

coverage保留未补齐的腕部功能等缺口；learning_state只追加对应领域维护历史，数学游标/旧历史/工程后续队列及RL/概率待研主题按原值检查。priority.next_domain保持reinforcement-learning，之后probability，再回neuroscience。下轮先查2026正式接收的探索/长时信用分配或离线评估原论文；本轮候选待补Supplementary Figs4–7、Reporting Summary、Source Data、SEM调用路径和跨文章数据复用，均不视为已完成科学覆盖。

发布前main读回仍为启动SHA，无并发差异；最终发布再核对一次。使用最新main的parent/base tree，经GitHub create_tree/create_commit和expected_sha、force=false更新，模型不写本地Git元数据。远端提交与完整树验收完成前，EK-115246-03保持未完成；发布回执在收尾另行记录。宿主只在全部工作文件与远端树一致后对齐Git索引/分支并轮间同步已安装技能；本模型不宣称已经完成宿主步骤。


## 发布收尾读回

维护实现提交 `7ad02cf49e1e3c4f4fa4874160d3c9e71f1278b8` 已按expected_sha=`2e854cac85a6f69e3a15926173896fae74d8b7f6`、force=false更新main。API ref、immutable commit及独立原生git ls-remote均读回同一提交；完整2712文件树为 `52122d2ff72cb2cc9236f6e8e5930500141a5259`，与工作文件按Git规范独立计算的树一致，无并发main改动。

首次只读hash-object计算把7个原有CSV的历史CRLF再次规范化，导致本地计算与树对象不同；未移动main，未改这些文件。逐文件核对确认它们的实际原始blob等于启动index及远端，按Git add对未变历史blob的保留语义修正验收计算，随后完整树匹配。该过程只调整私有验收工具，不写.git或更改仓库换行规则。

根TASK的本轮01–03已逐项验收，其他任务保持原状；learning_state对应领域追加“reviewed-zero-published”和维护提交，科学published_count仍0，候选不升级，数学游标与原队列保留。本收尾修改按最新main再读回、插件快照/格式/ref检查后单独非强制发布；最终收尾SHA在对话和私有回执读回，避免在提交内自指自身哈希。宿主轮末fetch、索引/分支对齐与安装技能同步仍须在模型退出后独立执行。
