# SYSTEM-99 系统级改进批次

Task-ID: SYSTEM-99
Date: 2026-10-20

## Plan

Version: 7

用户2026-10-20澄清：一次小时唤醒、小bug或提交不算一轮。批次持续到声明实际用途内无已知重大缺陷/架构冲突、必要验收齐备；不能保证绝对无bug。通用、科研、旅行、代码阅读、marketplace均保留；人类guide只读，不新增付费资源。

覆盖真实入口/安装→任务准备与恢复→并发单写归属→交接/独立验收→记忆更正→advice/上下文→真实任务质量。同批正文精读至少十篇，旧阅读不重复抵数；前一阶段CONCISE-98的两篇属于本次尚未结束批次，需补八篇。实测与文献结论分开。

当前阶段A：修复实际checkout的TASK→snapshot→prepare/task_view断链。原16行只补链接前空格；5份详情只补准确身份/组织日期与Plan/Progress边界，原段落/状态/证据保留。新增真实checkout回归，不放宽解析器/全局验收。独立审查通过后才修复；新TASK/Plan哈希必须新run和reconciliation，旧运行/证据不追溯改写。prepare只生成当前索引的完整占位草稿，不启动、approve或重跑历史任务；缺guide/advice审核、host动作和认证回执仍拒绝执行。

v3并发整合：最新main8587b781新增MEM-INDEX-96和记忆目录功能；保留其全部来源/测试/结果，只对新TASK行补同类第17处空格。任务集合由初始316变317，真实快照/CLI/旧哈希拒绝及全库在最新源码上重测，不以初始验收覆盖新版本。审核者独立复核补充，不改该并发提交的验收原件或冒领其质量/性能。

阶段A验收：修前固定失败；索引仅空格/新登记行差异、详情仅治理插入；snapshot逐项覆盖ID/日期/文件；真实CLI prepare、局部task_view可读且stale/unknown拒绝；旧来源哈希失效，Progress追加不失效；全库/Reader/同步及独立代码/数据复核。只本地CPU/可逆临时文件，不调用付费模型或未知作业，不伪造tmux/ManagedEngine。主控唯一写源码/任务，独立角色仅各自results文件。

阶段B：CHAIN-ENTRY已独立用新项目实际安装复现。仅更正setup.py生成说明的两处Project A/doc/工作流库doc为agent_doc；安装/检查、用户内容保护、原子替换和角色行为不变。新增真实安装输出回归并保留修前失败，普通doc内容不得受损；全生命周期与独立复查后可发布检查点，不宣称Claude真实会话加载已验。

后续阶段：结果可发现登记、portable终态证据有效性、真实协作/更正/恢复审查，按确认问题版本化补方案再实现。检索/存储微基准不代替真实模型任务质量；受限后端或质量/成本关键数据未验证则整批保持未完成。阶段性发布是可恢复检查点，不计完成轮次，不以加文档/Skill数量代替能力。

阶段C（CHAIN-TERMINAL）：仅portable done的新可信事件重验当前完成证据及依赖闭包，失效的已执行节点blocked并需显式reconcile，保存旧evidence/attempts，不进入claim或自动重放；恢复原文件不能自动取消reconciliation。active链原failed语义、cancelled、重复事件及managed worker契约保留。验收使用真实临时文件篡改、重启、无关支线、缺失/异常verifier、恢复与取消负控；保护计划撤销后的终态处理须单独补证。先保存修前失败、独立计划审查后实现，独立结果验收后可发布阶段检查点。

阶段D（CHAIN-RESULT-CATALOG）：按catalog-plan登记代表性result-fd95，唯一旧目录新增record.json；14旧文件/失败/独审原字节不变，register_history保留unknown、contract=None、context={}、measured_at=None，不补造缺失私有日志。先查正式查询缺record/无候选，修后两种名称均可发现；show精确14 refs，decide仍拒绝自动复用。登记完整性独审后方可发布，整体覆盖后续分批处理，不能将82缺record全称损坏或自动授信。

阶段E（CHAIN-REVIEW-RESTORE）：保护链完成后，顶层审核拒绝必须将已done节点持久blocked/requires_reconciliation，沿用_check_done已有plan_review_after_effect语义；保留证据/计数，不清既有围栏。认证恢复、重复wake和重启不能自行接受旧完成状态；显式reconcile仍验当前认证/授权/依赖/证据，取消不可恢复。只补顶层异常分支，不改审核认证/预算、事件去重、active失效规则或managed接口。先修前失败，独立计划审核后实施；单节点/完成子集/全完成、混合DAG、撤销与取消/恢复/权限/事务持久化、原C及双主/受管兼容回归并独审；无真实宿主或模型质量主张。

阶段F（CHAIN-SEARCH-DRIFT）：仅允许已知v1完整字段、合法类型、默认有界扫描、partial=false/errors=[]且除scanned外逐字段完全相等的实时查询统计差异；完整计划哈希、原task和handler收到的prior_result_search均不改变，日志保留实际新查询及纯扫描差异分类。不忽略候选/哈希/排序/分数/状态/未知字段/查询策略或缺口变化，不放宽partial/错误响应，不自动复用或重审核。固定修前双生产者中央登记→各自独立算术gate→后继真实派发/重启反例及负控，独立方案审核后才实现；验证原有门禁、全库/Reader及独立结果，模型/部署/速度仍未知。

阶段G（CHAIN-CORRECTION）：仅补可重复的CPU跨模块验收与必要记录，不改runtime或记忆/通信schema。串接受保护计划、真实SQLite交接/消费者上下文/ACK、带声明依赖的记忆更正、完全终态新tick围栏、旧证据reconcile拒绝、取消、全新run/event/记忆ID与新审核后实际决策变化；原始观测/旧报告/ACK及无关支线保留。先查旧证据与保存有限探针，独立方案审核后纳入回归，再独立结果验收；探针原实现通过就登记验证结果，不制造生产修复。认证为CPU测试宿主，真实Claude/多模型/SSH/tmux、完整语义与成本质量仍待后端，不把声明引用门禁外推为自动发现隐藏依赖。保持唯一TASK与人类guide只读。

## Progress

基线dcc10b10537a3b410a25f6ef3f2c842a3c1777b4，已fetch同步，独占协作锁。发现315项任务的16行不合格式；空格内存归一后另有5份详情不合身份/边界；实际validate失败，新增三项入口回归修前均error。已生成阶段A独立审查请求。task_context已有接口，避免重复实现。尚无代码修复或整批验收完成。

新查询`task document integration canonical recovery`，limit3/max-scan200：scanned199/partial、64缺记录错误；combined-corpus-delta-v2/v4/integration-v3仅语料/旧文档集成，不复用为本阶段实测。当前目录私有before.log/plan.md保存初始诊断，公开结果按system99分工保存。

阶段A/B实施：16行空格、5份详情治理插入和setup两行入口说明已修；真实snapshot316、默认protected CLI草稿316项（6857986字节）可生成，未经human guide审核正式校验仍拒绝。旧真实索引SHA失效、316详情Progress稳定、task_view拒绝非法范围；原字节和混合行尾按逆投影保留。新checkout回归4/安装与相关专项43/全库1355（8跳过）/Reader3通过。详见[检查点](../../results/system99/stage-ab.md)，独立结果审查进行中，不标整批完成。

同一未结束批次正文阅读已由CONCISE-98前段2篇加本次[4篇A](../../results/system99/research-a.md)、[4篇B](../../results/system99/research-b.md)补齐10篇；不是把旧批次阅读重新计数，图表/附录未读范围和未复现限制保留。

[独立全链审查](../../results/system99/independent-chain-audit.md)还确认历史正式结果缺登记、portable完全终态tick的当前证据复核缺口；另有多生产者查询漂移待验证。316查询error列表相同，草稿重复量尚未转化为实际模型成本证据。真实Claude/多模型/tmux/SSH链、本机可调用宿主缺口未补齐，因此批次继续pending。

下一步仍用SYSTEM-99：先按原字节/真实哈希为代表性历史批次建立不授信的可发现登记并独立验收，再量化其余目录覆盖；portable终态补固定最小反例和独立方案审核，不能盲重放已发生作用或恢复取消；多生产者区分相关证据变化与无关查询统计变化。以上尚未实施，不把建议当修复。

并发main8587b781已整合，其记忆改动及结果原样保留；新MEM任务只补第17处空格，快照/真实草稿317项。最新Python3.12.14全库1366项（8跳过）与Reader3通过；不覆盖并发作者在其它环境的负结果。初始A/B独立验收usable-with-scope，最新整合补验/普通发布回读尚待收尾；SYSTEM-99继续未完成。

最新指令恢复同批续接，已读取集成独立复核116项通过与317项草稿门禁回执；阶段A/B补验完成，仅发布与远端回读待收尾。后续重大缺口仍保持open，不计为完成一轮。

阶段A/B已普通expected-parent原子发布并读回main 68e883e986c97ffbfc96602e96baafef46880e4d，树与本地冻结候选一致；安装说明、TASK和新入口回归blob逐项一致，native fetch同SHA。CLI无凭据，使用已连接GitHub接口，未强推。阶段C先查询terminal completion evidence reconcile：199扫描/partial，候选仅旧文档/语料，不复用为终态证据；真实文件/持久化最小回归修前3项5失败（含三个verifier子例），尚未改core。

阶段C Version4已独立approve后实现，最终6项修前8失败保留。修后专项74项、全库1372项（1364执行通过/8跳过）、Reader3通过，独立结果复核收尾中。Version4使先前CLI草稿只作固定历史证据，不当当前派发方案；当前无生产start、审核恢复或模型质量主张。结果登记覆盖另由同批catalog-plan只读调查推进，不新增竞争TASK。

阶段C独立回执usable-with-scope已回读：83项（82通过/1跳过）及额外当前有效保护/事务回滚/双独立根负控通过；原active/managed语义保留。仅当前有效审核的新可信tick有保证，终态审核撤销恢复仍open。阶段C普通发布准备中，整批继续未完成。

阶段C已发布并回读main9ab9becde217b74c50464155ab675dee9f422a60；本次fetch未变。Version5独立approve后完成D/E：[阶段证据](../../results/system99/stage-de.md)。result-fd95仅增不授信record，14旧文件与50c1ca1逐字节一致；两种正式名称查询0→1命中，decide仍unknown/verify_delta且不调用verifier，其余81个缺登记目录未处理。审核撤销后的旧done加持久恢复围栏，修前5项4失败1通过，修后专项79、-O新回归5、全库1377（1369通过/8跳过）、Reader4及同步通过；独立结果复核进行中，不宣称真实宿主验收。新增Chubby正文固定版本/章节/局限，同批累计11篇；整批仍open，查询漂移、通信/记忆到真实消费者、模型质量/总成本及跨宿主验证继续未完成。

阶段D/E独立验收已接受usable-with-scope：109项108通过/1真实tmux跳过、Reader4/同步通过，另补原围栏不覆盖、事务回滚、旧core固定失败、登记不可覆盖/不授信负控；全库日志与原字节独立核算，未独立重跑全库。仅本地CPU边界成立，普通发布及远端回读准备中；整批未完成。

阶段D/E已发布main789697f并回读。Version6阶段F完成纯scanned统计误阻塞修复：
保护CPU链A→独立gate→B→独立gate由B不派发恢复四节点完成；整个原task、
planSHA/回执不变，候选/缺口/unknown变化及日志失败继续阻塞。修前最终8项2失败；
修后14项、专项106、-O14、全库1391（1383通过/8跳过）、Reader应用3及同步通过。
[阶段证据](../../results/system99/stage-f.md)与[最终独审](../../results/system99/independent-stage-f-final.md)
绑定最终SHA，先前测试fixture错误与候选记录保留；仅有界CPU验收，普通发布收尾。
新增PlanFence正文固定v2/章节/消融/局限，同一未结束批次累计12篇。
下一步仍为通信/记忆更正到已完成消费者的恢复、登记覆盖与实际上下文/任务质量；
真实Claude/多模型/tmux/SSH后端及质量/总成本缺口仍open，不计一轮完成。

阶段F已发布并回读main d033c9f，Version7阶段G续接后接受独审
usable-with-scope：[更正链证据](../../results/system99/stage-g.md)及
[独立记录](../../results/system99/independent-stage-g.md)。新组合回归普通/-O各1项
通过，全库1392（1384通过/8跳过）、Reader应用3及同步通过；独审另做两个
围栏负控、计划/回执新身份与ACK保留核验，并核算完整日志。原runtime已通过
组合验证，本项没有新生产修复；取消旧链后新要求确实改变两消费者决策。
新增MemTxn正文固定版本/方法/消融/局限记录，同一未结束批次累计13篇。
本次fresh fetch仍d033c9f，仅五份阶段G文件发布收尾；实际模型宿主、上下文
token与质量对照、历史登记覆盖等仍未完成，不能把CPU验收算整轮收官。
