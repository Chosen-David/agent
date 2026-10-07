# 2026-10-07 工程持续学习 112454

本轮神经科学维护核查3个来源：2023年PLOS Biology熊蜂单步开箱原论文及两份附表、2024年Nature熊蜂两步任务原论文、Queen Mary机构说明。准备1张复用卡 `neuro.bumblebee-social-diffusion@1`，远端发布0条：必需全仓检查未通过，未创建commit或更新main。2024年论文附录未完整核验，保留candidate。本地语料75条。没有动物实验、GPU/训练实验、模型A/B、权重修改或意识测量。来源窗口2021-10-07至2026-10-07，采用论文属于补缺的2023年原始结果，而非2026年新发表研究。

## 授权、输入与运行边界

根TASK的本轮要求为EK-112454-01、02、03；其他任务和历史勾选保留。宿主已fetch/fast-forward且工作副本干净，模型启动时只读 `git status --porcelain` 无输出、HEAD为 `18e0904c9e2b9343cf7163bd2cb38cb14c362ec6`；GitHub main读回相同SHA。输入文件版本/哈希见[inputs.json](inputs.json)。读过AGENTS、TASK、README、FORMAT、coverage、learning_state、upstreams、两类来源目录，以及最近神经科学/高等代数报告和相关协议。决策EXECUTE，主AI单一作者，无委派、无新增资源或定时任务。

真实小时维护的私有live读回包含active_round `20261007-112454`、interval_seconds=3600，心跳在本轮持续更新。Windows sandbox调用WSL status返回 `Wsl/Service/E_ACCESSDENIED`，因此本轮不能独立确认tmux pane/live或下次due，未宣称新监督器启动或完成部署。复用原调度，不停止它；宿主负责本轮结束、Git元数据对齐与轮间技能同步。模型不写`.git`，不尝试更改权限，不执行本地commit/fetch，也不绕过被拒绝的命令。

## 来源与采用/拒绝

完整URL、真实日期、读取对象/哈希与范围见[sources.json](sources.json)。原始全文、DOCX和工具响应缓存只留私有运行目录，不随报告镜像全文；博客哈希对应web工具响应捕获，并非网页HTML哈希。

| 来源 | 实际日期与版本 | 采用范围 |
|---|---|---|
| [PLOS Biology原论文](https://doi.org/10.1371/journal.pbio.3002019) | 接收2023-02-02，正式发表2023-03-07；PMC9990933 XML；S1/S2 Table出版社DOCX | 采用单步双选任务的行为扩散、熟练度/偏好，以及统计与人为干预边界；CC BY 4.0，无实现代码复用 |
| [Nature两步任务](https://doi.org/10.1038/s41586-024-07126-4) | 接收2024-01-26，正式发表2024-03-06；PMC10954542 XML | 原始Main、Discussion、Methods及图表已读；附录训练/测试细节与重复示范蜂分析未完整核验，留candidate |
| [Queen Mary机构说明](https://www.qmul.ac.uk/news/latest-news/2024/se/bees-master-complex-tasks-through-social-interaction.html) | 2024-03-06；web读回文章正文 | 解释/线索；不作独立复验，不采用其将结果推广到广义累积文化的表述 |

近期筛查使用日期窗2026-07-09至2026-10-07的熊蜂社会学习检索，返回的相关Nature原文实际为2024年；其余预览多超出五年窗。搜索抓取时间不能替代发表日期；本轮没有核验到该窄主题的30–90天新原始结果，不能声称已穷尽近期文献。未把跨领域会议年份、未确认投稿或预印本改称正式接收。RL/概率论正式论文筛查留下一轮，既有待研主题不覆盖。

## neuro.bumblebee-social-diffusion

精确结论：2023年Bombus terrestris audax实验室工蜂采集者的单步双选开箱实验，示范组学习者更熟练并偏好示范变体，无示范组也会自行开箱。测量为行为视频，非神经活动。六个示范蜂群、四个无示范蜂群，6或12天，每天30分钟无盖预训练后3小时闭盒接触。确切个体年龄/性别分层未单列；学习者嵌套于蜂群，开箱次数不能当作独立重复。

Fig.2A为22对14名学习者，按学习后天数归一化的中位数27.9对1.15次/日（原文p=0.001）；Table 2的六示范蜂群示范变体比例均值98.6%。这些是论文报告，不是本机measured。视频30 fps/720p，BORIS 7.10.2编码、R 4.0.3分析；dtype、batch及GPU型号不适用于动物实验。原始Figshare release未固定、未重做统计；软件小版本之外的包版本未核验。

S2 Table实际提供三种随机效应模型。最低AIC选择bee ID（532.86），其day×treatment p=0.003233；colony ID和nested模型对应0.005488、0.004709。nested模型的treatment主效应p=0.061374，不能把交互与主效应混为一谈。day1/day3分析排除较晚学习者后为18对11名，与Fig.2A样本不同。

S1附表的R2/R3观察总数为223/1009，正文表1为219/1006，未通过原始数据裁决差异；卡片明确保留并不使用这些冲突总数作效果量。单示范实验人为阻止示范蜂使用非训练变体，观察蜂无此限制。控制蜂之间仍可能有社会信息。局部强化、刺激强化与动作模仿未独立鉴别，最大12天扩散未测试跨生物世代改进链。

2024年不同的两步串行盒中，15观察蜂5只通过无奖励测试，9个示范蜂被重复分配至部分配对；无示范的三个蜂群在36/72小时、12/24天接触中无开箱。其正文明确不能排除极罕见个体终生自行解决，也未检验两步传统长期维持。这些正文记录用于限定候选范围，不升级为完整方法审定的卡，更不与2023年任务称同条件独立复验。两个数据入口不同，不据同作者/同物种作独立复验保证。

## 知识用途、假设与未测项

本卡支持示范学习方案的前提检查、奖励/暴露混杂诊断和独立重复单位选择，能减少对已知单步行为现象的无信息增益探索。AI启发仅为待验证假设：等总预算比较有效动作示范、无示范、顺序打乱、仅终态/奖励位置暴露；包括训练/生成示范者成本，测未见任务成功率、样本效率、错误传播，按独立运行/seed汇总。若顺序打乱与有效示范相当，动作序列解释应被拒绝。本轮未运行该对照，也不替代显式复现和用户必做验收。

没有新增实现卡或下载执行第三方源码。已检查采用论文的许可和方法接口定义，成熟软件仅作为原实验环境记录；未把软件名称当固定40位源码复用卡，亦不宣称本机代码正确性/GPU性能。全文核对由单一模型完成，未做盲测、独立科学评审或全部补充视频复核。

## 检索、负例与验收

任务开始先实际检索“社会 学习 新行为 复杂 传递 昆虫”（neuroscience域）。命中章鱼睡眠、麻醉、鸟类细胞卡，因物种/任务不符拒用，没有把词法相似当本题证据。新增卡与所有前提引用见[knowledge-use.json](knowledge-use.json)：`neuro.bumblebee-social-diffusion@1`，sha256=`edd525eb72e80a9ceb4841f92017806307463c9d46cd174f6e97880eb6cfb1a0`，无强依赖。

新自然问句“观察同伴后学会开箱，怎样区分自己摸索和模仿？”没有直接命名方法；另检查群落伪重复、任务不匹配及无关负例。文件/SQLite均Top3完整命中。四种decision实际返回：缺条件→insufficient_context；字符串匹配→reuse_for_planning；两步任务替代单步→minimal_transfer_check；显式复现→run_requested_experiment。所有automatic_skip_authorized=false。校验内容身份不能代替生物学/AI适用性审查。

原有六个回归目录在修改前后各运行一次，日志、原始排名和失败完整保留。工程、RL/概率论、神经科学原有预期均完整召回；新增卡也通过。旧基础21题Recall@3两后端仍17/21，round2仍0.75，morphology文件仍0、SQLite仍0.5；与基线逐题期望召回/排名相同，未修复这些既知漏检。显式8候选包使基础目录上下文召回为1；round2仍失败（files 0.875、SQLite 0.75）；morphology只SQLite上下文恢复为1。没有修改默认参数或删除失败测试。

初次“所有候选列表完全不变”检查失败：新卡进入5个backend/query组合的非目标候选，旧预期条目仍保留原排名。差异见[完整候选变化](checks/nonregression-candidate-differences.json)。后续验收分别检查逐题旧预期召回/排名不退化和记录额外候选污染；不将二者混称候选列表不变。公开检索回归由作者编写，不是未见任务或实时模型效果评测。

知识格式、插件生成闭包、索引重建、引用哈希、来源缓存哈希、算术例、数学游标/历史和RL概率待研队列不变检查已通过。最终检查结果见[validation.json](validation.json)，完整命令与日志位于checks/。

全仓Windows Python 3.12检查运行511项：7失败、60错误、10跳过，不能通过发布门禁。真实错误包括fcntl不可用、符号链接特权不足、POSIX/Windows路径契约差异、隔离CLI的GBK输出错误及依赖导入失败；未改平台代码、放宽测试或提权。为区分新增问题，通过只读git archive将启动基线18e0904放入私有目录并运行同一命令：511项、8失败、60错误、10跳过。逐失败ID对比无本轮新增失败，基线另有一项开发评测时序失败；完整差异见checks/full-suite-baseline-comparison.json。这证明该次对照没有新增失败，不证明全仓已验收。

Reader首跑因缺少fitz导入失败。按已有requirements仅将免费PyMuPDF 1.28.2安装到本轮私有deps目录，未改全局环境，使用进程级PYTHONPATH复验3/3通过；知识复用相关unittest 7/7通过。原失败日志完整保留。当前没有可调用的Linux全仓验收通道，WSL status拒绝访问；不以局部通过代替全仓门禁。

## 下一轮与发布

priority.next_domain已记录轮转意图到reinforcement-learning，轮转顺序neuroscience→reinforcement-learning→probability。RL/概率论原待研主题、数学last_completed_round/next_topic/history/open_questions和工程后续AI Infra→AI算法→数据结构队列全部保留；新增工程/神经科学历史追加本轮并标validation-blocked、prepared_count=1、published_count=0，两个last_completed_round未前移。下一次RL先查2026正式接收原论文的探索/信用分配与离线评估；神经科学后续补两步任务附录、头足类腕部控制、鸟类终版和树突可塑性。当前脏工作副本须先接续验收/处理成果，不能直接启动下一轮覆盖它。

发布按用户Windows桥契约：检查完成后再次读回main，保留并发；GitHub create_tree/create_commit，以最新main为parent/base tree，update_ref使用实际expected_sha与force=false；独立读回main和完整内容树。本轮未满足检查门禁，未调用GitHub写工具、未创建提交、未更新main；[publication.json](publication.json)明确记录阻塞。

收尾读回main已前进至 `e7a908aaa2198d740dd4fcfc835b8e2931db16e5`，compare确认唯一并发文件为TASK.md：原ALG验收句修订与已完成INDEX-01–03追加。已取回精确SHA的TASK，验证本轮之外的本地尾部仍等于启动基线后，将远端尾部与本轮独立任务节合并；双方勾选/证据保留，不写本地.git。该并发不改代码/知识/测试，原检查证据适用范围未扩大。

EK-112454-01完成，EK-112454-02因全仓检查阻塞，EK-112454-03未发布。下一owner为可信宿主/主维护：在已有可用Linux环境运行两套必需unittest（保留本轮失败），通过后再次读取main、整合并发、复验受影响项并按原授权CAS发布；不需要新付费资源。待发布补丁与文件哈希清单保存在私有 `.agent-runs/engineering-112454/pending.patch` 和artifact-manifest.json。宿主不得把当前不匹配工作树对齐成已发布状态；保留工作文件和失败证据，轮间技能同步也暂缓。
