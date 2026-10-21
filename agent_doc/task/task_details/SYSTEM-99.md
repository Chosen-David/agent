# SYSTEM-99 系统级改进批次

Task-ID: SYSTEM-99
Date: 2026-10-20

## Plan

Version: 29

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

阶段H（CHAIN-CONTEXT-MEASURE）：只测现有接口，不改指令、runtime/schema或目录。先查旧结果并以只读探针观察实际三入口compose_entries、SYSTEM-99 task_view、顶层advice语料；独立审查后固定tiktoken0.12.0的cl100k_base/o200k_base编码、源码/输入hash，重跑离线计数并核对实际重复协议展开后逐字节相等。分开文本和实际返回JSON的开销，任务导航/全语料因scope不同不得比较为等价质量；不把字符数、离线编码、单条消息/忽略cache的输入当真实模型usage或费用。独立复核数据/代码及硬边界后可登记证据，不宣称性能或模型质量提升；缺真实宿主的质量/总成本对照继续open。新增相关论文正文记录，不以论文结论授权大迁移。

阶段I（CHAIN-CONTEXT-PILOT）：以当前宿主工具提供的两个真实独立新上下文AI做只读代码理解回答初探，fork不继承历史，不伪称部署repository runtime适配器。两包仅三入口共享协议是否由既有compose_entries去重不同，源码/问题逐字相同；原生派发的投递路径/输出归属另有差异。固定输入hash、单次调用/无重试、同一请求的默认模型设置、实际child ID/派发指令及完整原答。问题覆盖终态失效恢复、选择上下文保留异议/依赖、guide/advice授权边界。先独审固定任务包和隐藏rubric再派发，指令禁止修改源码、联网、读包外答案；range/hash是可核对的读取自报，不当provider完整输入或无包外读取认证，发现越界即failure，未见越界也不称证明合规。独立核对每题事实/范围限制，错误不因短而抵消。一个配对、三个有提示的问题，不能作统计非退化、普遍质量/性能或真实usage/费用结论；未暴露的精确模型版本、usage、完整工具轨迹和包外读取合规均unknown。Version9在发现缺完整轨迹后撤回原approve并revise，未派发；本版接受诚实边界而不补造认证。无生产指令/schema/目录变更，不自动推广导航或迁移agent_doc；完整加载认证、真实宿主部署、多轮协作及任务质量仍open。

阶段J（CHAIN-BACKEND-PROBE）：发现已登录的本机Codex CLI后，仅用现有账号做一次有界连通性检查，不是重答阶段I。先独审固定argv/stdin与90秒墙钟预算；隔离空cwd、read-only、never审批、ephemeral及忽略用户配置，不读项目/历史、不改全局配置、不加付费服务或绕过标志。只请求固定ack，不给项目任务；失败/超时保留且不手动重试，超时仅终止自己的进程组。原stdout/stderr私有保存，独审真实事件/最终答复/退出状态后只公开脱敏元数据和hash，绝不发布私密推理或认证内容。安装/登录不算可调用，ack成功也只证明该次后端可达，不证明repository adapter、tmux监督、恢复链、质量或费用收益。CLI内部传输重试如可见则保留，精确provider版本未暴露仍unknown；缺接口继续其它已授权工作，整批仍open。

阶段J的Version11在执行前独审被revise：runner仅传CLI -C而未设OS cwd、漏查override指令、超时清理可能超90秒。Version12仅修这三项：OS cwd与-C同一空目录，祖先及HOME/CODEX_HOME的AGENTS/override存在就不调用；预留10秒做finally自有进程组清理与回收，实测超预算/未回收为失败，不承诺操作系统硬实时。原v11/runner留私有快照，无模型调用。全局provider隐藏指令仍不能认证为空，probe只验连通性。

阶段J的Version12复审另发现默认SIGTERM会跳过finally；Version13仅增加可捕获SIGTERM/SIGINT的受控取消记录与清理，Popen完成赋值前延迟抛出避免启动窗口丢归属，清理期间忽略重复可捕获取消。不宣称SIGKILL/宿主关机可恢复。先补纯Python取消自测，再独审新hash，未获approve不做真实调用。

阶段K（CHAIN-BACKEND-DIAGNOSIS）：承接J无事件超时，只调用已有CLI的doctor健康诊断，不重试模型请求或回答阶段I。固定一次`/opt/codex/bin/codex --no-daemon doctor --json`、空OS cwd、stdin DEVNULL、30秒执行及10秒自有进程组清理预算。先独审实际runner/方案及七域，批准后执行；raw输出0600私有保留，广告“redacted”不当隐私认证，仅按白名单披露check ID/status和通用解释。沿用受控SIGTERM/SIGINT清理，不宣称SIGKILL/关机或所有后代已回收。不得改全局config/auth、启服务/付费资源/调用模型；异常或超时保留且不盲重试。结果经独立六域核验，只说明本次诊断状态，不能推断模型可调用/usage/成本/部署或质量。已有检索partial/81errors的旧语料不作为当前诊断验收，批次仍open。

阶段L（CHAIN-MANIFEST-SNAPSHOT）：通信consume_handoff在envelope哈希检查后重新读取manifest，临时真实文件反例已返回并存储消息哈希不匹配的替换内容。仅把严格JSON加载扩展为可选expected_sha256校验，哈希和解析同一次读取的原字节；消费时传入不可变event引用，不靠再查一次路径修补ABA。保留重复键/非有限数/UTF-8、原consumer契约、所有refs检查、ACK独立和basis不可变性，不新增schema或OS安全边界。先冻结替换/ABA/读取后替换及普通编码负控，保存修前失败；独审方案后修复，独立代码/数据验收后才发布。全部本地临时CPU夹具，无模型/GPU/部署或性能收益主张；其它artifact读取不因此获得事务快照，host仍须消费前检查，批次仍open。

阶段M（CHAIN-RESULT-CATALOG-WAVE2）：继续阶段D已确认的历史结果可发现性缺口，仅批量登记当前81个缺record目录中可无歧义冻结的一组：顶层叶目录、含直接report.md/report_by_gpt.md/report.json/README.md、1..64个全部已跟踪普通文件且record仍不存在。当前固定43目录、618原文件/6108516字节，排序名称清单SHA256为d81fad885eadd022fa3e7243db383eaab98f0af4f91e56cf86273b28f8b3dbc5，排序`path<TAB>sha256`清单SHA256为a11c31a0d039645ff711e13b61a75576693b85285a2f2ab2ae9db4a9c6b9c3d4；准确清单和生成规则见catalog-wave2-plan.md。每目录只经现有register_history新增record.json，summary仅为run_id与报告首个H1，避免公共治理词污染词法排名；信任限制由origin/validation/trust_note结构字段表达。全部原文件逐项path/hash引用并须与49bd760基线blob一致，context空、measured_at空、contract空、validation unknown，不从旧pass/fail标题推断当前状态。先独审固定方案；首写前一次性重查全部冲突、普通文件/跟踪状态/数量/hash、summary和预期record大小。逐record写入非批量原子：中断续接只接受字段/refs/unknown状态与冻结输入完全一致的既有record，任何差异停止整批，不覆盖；提交前必须恰有43个新record。验收要求43原目录原字节不变、43 records可show且各自run_id查询可发现、题名特征查询不被公共治理词淹没、正式查询错误81→38并保持partial/errors可见；全部43执行decide_run只能verify_delta/unknown且verifier总调用0。18个嵌套报告、15个无标准报告、5个>64文件目录继续分型，不用空壳record消除错误。无runtime/schema/guide/旧报告修改、无模型/GPU/性能主张；阶段提交仍不算整批完成。

阶段N（CHAIN-RESULT-CATALOG-WAVE3）：继续分型阶段M剩余38目录，只登记11个具有单一顶层
Markdown报告、子树无独立报告或不同run身份且整树不超过64个已跟踪普通文件的历史目录。
固定358原文件/3349153字节；目录名清单SHA256为
4b9183b865b80a59978819cb20b7abc6733de18dcb1cd4619ed8b374bbbe7c11，排序
`path<TAB>sha256`清单SHA256为
cd94f4498658227686e55ce913690ea40dd8e5b6e10e3274782aa3203a2fc370；完整规则见
catalog-wave3-plan.md。每目录仅新增unknown历史record，summary严格取顶层首个H1，整树原件
逐项绑定且不得修改。旧失败/无效题名必须保留；comm20父目录因包含另一个已登记run而排除。
先独审Version18和固定方案，写前fetch重算；验收要求错误38→27、11个show/search/decide
及358原件hash成立、
verifier调用0、定向/全库/Reader/同步和独立结果审核通过。JSON-only、多运行/嵌套报告、
超64文件、纯计划/失败尝试及活动中的system99继续显式open；无模型质量、token或性能主张。

阶段O（CHAIN-TASK-SNAPSHOT）：任务契约当前先由 `digest(path)` 读取TASK原字节，再由
`requirements(path)` 按同一路径二次读取并解析；真实临时文件在两次读取之间替换、解析后恢复的
确定性反例，使绑定原文件SHA的计划接受了替换文件中的不同任务ID。仅将prepare/validate及
publication freeze的任务索引摘要与解析绑定到各自一次有界普通文件读取；validate必须从同一
原字节同时校验SHA和解析任务，prepare还须拒绝其任务快照与project-documents快照不一致，
publication须拒绝任务读取与已冻结候选树身份不一致。保留公开`requirements`
兼容、canonical/legacy解析、guide/advice/task-detail门禁及错误闭合，不宣称跨多文件事务或对抗
恶意OS写者。先保存修前接受日志并独审Version19方案；修后覆盖真实替换/ABA、无效UTF-8、
非普通文件、prepare中间变化、publication中间变化及原回归，全库/Reader/同步和独立结果复核
通过后才发布。阶段O不
处理剩余27个历史目录、真实宿主/多轮质量或usage/费用，仍不是整轮完成。

阶段P（CHAIN-RESULT-CATALOG-WAVE4）：Version21继续阶段N剩余27个缺record目录，只登记15个可由
现有`register_history`完整冻结的独立JSON/状态型历史包，共347个已跟踪普通原文件；目录名
和`path<TAB>sha256`清单分别固定为
`ee2c6faf0dde61b1101ebe5a5a64e5ee1aee9eb6f4ecf9b922149779c7ce56ed`、
`ea734d8c1b47b8350e86b5c07508a89087682ffe1c5a91cc7f3a9bb4397daeee`。
失败、blocked、preflight/registration rejected均保留原义，只生成unknown历史索引；内部重复
producer ID不能覆盖顶层目录身份。排除已被v2记录引用的math-linear失败包、活动/纯计划/父容器、
混合身份和超过64文件的目录。独立方案审核后才写入；验收要求错误27→12且partial/剩余错误可见、
15个show/search/decide均不授信、347原件不变、定向/全库/Reader/同步及独立结果复核通过。
精确summary与正式search/show/decide参数固定在catalog-wave4-plan.md；发布前main漂移则重算并
升级版本。不改runtime/schema/guide，不解决真实宿主、任务质量或费用，阶段提交不算整轮完成。

阶段Q（CHAIN-RESULT-SCAN-ORDER）：Version24修复结果检索在截断前使用文件系统原生枚举顺序的
不确定性。修前同一三条合法record与同一查询只反转`scandir`顺序，`max_scan=2`候选即从
`alpha,middle`变为`middle,zeta`；当前252目录加README在默认200上限下只扫描199目录。
方案只在5000项全局安全上限内完整检查、排序目录，再截取字典序前`max_scan`项；超过上限返回
空成员/partial并保持搜索incomplete、登记拒绝，不从任意前缀泄露候选。普通文件不再消耗目录
扫描名额，截断项之后的符号链接仍须拒绝。先独审[阶段Q方案](../../results/system99/stage-q-plan.md)，
再保存修前失败、实现及定向/全库/Reader/同步/独立结果验收。不改record schema、目录组织、
信任语义或剩余12目录分类。两次方案复审分别发现5000→5001登记边界和先建后查的崩溃窗口；
现返修为结果目录外的跨进程锁内重扫、容量/冲突判断与目录预留，且显式解锁失败也保证关闭FD；
4999→5000成功、5000新增拒绝、
已有目标可补record、并发期间不越界及异常退出释放锁均列为门禁。不主张模型质量、token或完整
检索性能，仍不是整轮完成。

阶段R（CHAIN-EXTERNAL-JSON）：Version26把外部JSON边界从安全读取贯穿到消费前事务校验。
显式文件以 `O_NONBLOCK|O_NOFOLLOW` 打开，在同一FD核对普通文件和大小，严格UTF-8/JSON并拒绝
重复键、非有限数与超过256层容器；consumer还须在建库、推进状态、写输出或启动verifier/backend
前校验实际消费字段。范围覆盖启动/恢复、交接/通信/记忆、manifest/result/publication、探针/维护、
knowledge/context与backend/setup；保持原字节SHA、TASK/plan身份、授权和错误分类。固定特殊文件、
精确大小、非法编码、顶层/叶层错形和合法恢复；父目录攻击、Windows真机及真实宿主不在新增保证内。
全库/Reader/同步和独立冻结树复核通过后才发布；无性能主张，SYSTEM-99仍open。

阶段S（CHAIN-SUPERVISOR-LOCK）：只修复supervisor的launch.lock/worker.lock在真实FIFO上
以写模式打开永久阻塞的边界。共享私有opener先保留原写入guard，再以
O_CREAT|O_RDWR|O_NOFOLLOW|O_NONBLOCK打开并同FD fstat普通文件，finally关闭；原launch
阻塞flock和worker非阻塞重复退出策略保持，不unlink/replace/truncate锁inode。
先保存两真实入口修前超时，再独立方案审核，覆盖FIFO/目录/symlink、guard后替换、
数据库/backend/tmux零调用、正常互斥、进程退出和异常释放、inode/原字节不变及fstat失败关闭FD。
不扩展到未证实同类缺陷的contamination锁，不改并发作者的论文交付修复；定向/全库/Reader/
同步与独立结果验收通过后发布。POSIX本机夹具不代表真实tmux/SSH、Windows、父目录攻击或
跨主机锁认证；沿用同批17篇正文记录，真实宿主/多轮质量/usage/费用仍open。

阶段T（CHAIN-TASK-NAVIGATION）：修复新引入摘要导航在本仓库真实规模上默认不可用的入口回归。
基线317项（34项未勾选）下，默认12000字符预算直接拒绝；即使每项进度末尾只保留1字符，
全量仍约80369字符，单任务fixture未覆盖该边界。默认只选择未勾选索引项，并显式返回总数、
已选数、省略的已勾选数及`unchecked`选择语义；不得称为受管active状态。筛选须发生在详情读取前，
首轮结果独审发现既有进度同时存在置顶和尾部追加，单一尾部会把旧Stage N误作当前状态；返修为
`task-navigation/v2`，在64字符总预算内返回中性文档首/尾片段，不声称任何一边较新，缺结构化
摘要/状态时要求打开详情确认。保留最终全局预算fail-closed；CLI使用与预算相同的紧凑JSON，避免
缩进输出绕过实际上下文口径。`--include-checked`用于显式全量审计，
通常还需提高`--max-chars`；默认摘要不验证被省略详情中的身份、格式、更正、异议或依赖，完整审计仍走
全量导航或snapshot/delta。用可控多任务fixture覆盖默认/全量/零未勾选/类型/身份/预算，并在真实
checkout烟测输出长度与计数；同步runtime脚本及项目文档镜像。沿用同批17篇正文，不宣称真实token、
模型质量或整轮完成；首轮独立结果验收的blocked记录原样保留，返修后须重新独立验收。

阶段U（CHAIN-OUTPUT-LADDER）：把复杂解释升级为消费者先冻结请求、producer交付受控文字/图/交互网页/
讲解视频、结构验证、独立观察后交付的单一链路；普通短问答保持轻量。新增闭合 request/manifest、精确
claim 集、逐层角色/check 证据、确定性降级状态及稳定 CLI 退出码；manifest 绑定请求与产物实际 SHA，
producer 自报观察者永不形成接受。POSIX 首版逐路径组件 FD-relative `O_NOFOLLOW` 打开，拒绝父/终点
symlink、目录、FIFO、路径逃逸和读取期间变化；不声称 OS 沙箱、跨文件事务、Windows 覆盖或语义/
视觉质量。合同复用既有 visual explanation 流程并同步六个消费者，不替代 artifact index 或另造 TASK。
文档 profile 为独立 U2：固定平台/完整 wheel 锁和明确 PyMuPDF 许可选择、最终路径 venv、真实公开适配器
smoke 与 receipt；本阶段未实施 U2，不把候选摘要当安装授权，也不声称仓库已自带 PDF/Markdown/PPTX/
LaTeX 能力。阶段 U 仍是同一 SYSTEM-99 可恢复检查点，不计整轮完成。

## Progress

Version29阶段U1新增可信输出阶梯：消费者冻结请求与 claim/check，producer 交付文字/图/网页/视频
产物，结构验证后仍须独立观察；显式降级只到pending，自报reviewer不能接受。产物按POSIX逐路径
FD-relative no-follow读取并绑定实际摘要，六个既有视觉/论文角色复用同一workflow镜像。
首次独审退回祖先symlink、重复check ID、跨层证据及U2安装设计，返修并统一许可/POSIX边界后最终
接受U1为scope-limited。定向普通/`-O`各55项、TASK/项目文档相关145项、Reader3、同步/编译/diff
通过。全库两次1548项均仅
`test_managed_supervisor`当前`/proc` starttime瞬态失败1项（1539通过/8跳过），单项重跑通过/失败
交替；保留负结果且不顺带改无关supervisor。证据见[阶段U](../../results/system99/stage-u.md)与
[方案及独审返修](../../results/system99/stage-u-plan.md)。U2文档profile尚未实施，不能宣称自带
PDF/Markdown/PPTX/LaTeX；未测模型质量、token、费用或媒体质量，SYSTEM-99及整轮继续open。

Version28阶段T在并发main `1cf7258f` 新增摘要导航后固定真实规模回归：317项下默认入口返回2，
即使每项进度仅1字符全量仍约80369字符。独立方案复核要求区分未勾选与受管active、显式省略计数、
默认不替代历史更正/异议/依赖全量审计后实施。首轮候选默认紧凑JSON 11792字符，返回34项未勾选并
显式省略283项；显式全量317项可用，默认预算不足仍拒绝。专项普通/`-O`各14项、项目文档/同步
专项24项、全库1499项（1491通过/8跳过）、Reader3、同步/编译/diff检查通过；首次100字符候选
在真实树仍超预算，已保留为负结果并收紧80字符及紧凑CLI口径。首轮独立结果验收进一步以真实
SYSTEM-99阻断：旧单尾部把Stage N误作当前Stage T。现已返修为v2中性首/尾文档片段，明确无
时间顺序并补置顶/追加回归；真实输出11555字符，专项普通/`-O`各15项、全库1500项（1492通过/
8跳过）、Reader3、同步/编译/diff通过；二次独审独立重跑普通/`-O`专项、真实CLI、全量/预算、
兼容别名及同步检查后接受`usable-with-scope`。证据见
[阶段T记录](../../results/system99/stage-t.md)与
[首轮阻断](../../results/system99/independent-stage-t.md)、
[最终验收](../../results/system99/independent-stage-t-final.md)；不宣称真实token、模型质量或整轮完成。

Version27阶段S续接基线5b9bae0b；读取既有R结果后不重复修复JSON边界。新的真实start/worker
FIFO反例各在2秒子进程预算内超时，父进程已回收；独立方案审核已接受仅两supervisor锁范围。
候选定向5项（8个坏锁入口子例）普通/-O通过；全库1484项（1476通过/8跳过）、Reader3、
同步/编译/diff通过。独审普通/-O各39项及3负控接受有界恢复正确性；
[阶段证据](../../results/system99/stage-s.md)与[独立验收](../../results/system99/independent-stage-s.md)
记录范围，未重跑模型/真实宿主或宣称性能收益；整批仍open，普通发布/回读收尾。

Version26阶段R已把共享有界读取接入真实外部控制文件消费者，并在首次状态/输出副作用前校验嵌套
结构。修后FIFO/目录/末端symlink、重复键、非有限数、非法UTF-8、超限、257层和错形叶字段均
fail-closed；launch锁可重取，manifest/plan/原字节SHA绑定及合法恢复保持。独审曾因optimizer角色
表校验过晚退回，返修后代码范围`APPROVE (zero blocker)`；最终冻结树验收计数写入
[阶段证据](../../results/system99/stage-r.md)与[独立记录](../../results/system99/independent-stage-r.md)。
普通及`-O`定向各55项、全库1479（1471通过/8跳过）、Reader3、同步/编译/diff检查通过。
本项无性能/模型质量/usage/费用主张；Windows、父目录恶意替换、真实tmux/SSH/模型/网络和跨机文件
系统未验证。整批及本轮继续未完成。

Version24阶段Q经两次退回和最终独立方案批准后已实现：5000项内全枚举校验、目录名排序后
截断，超限空集fail-closed；结果目录外跨进程锁将容量/大小写检查和新目录预留原子化。修前
三条回归均失败，修后真实多进程覆盖不同run、同run、大小写冲突、持锁进程终止、已有目录恢复、
锁文件symlink/FIFO/父symlink、解锁异常FD关闭及Windows首字节重试。固定真实树查询重复逐字节一致；默认200
现扫描200目录而非199。普通及`-O`定向各71项、全库1417（1409通过/8跳过）、Reader3、同步/编译/diff通过；
旧/新同机目录选择中位179.445→284.582微秒，明确记录为确定性与完整观察的安全开销而非提速。
[阶段证据](../../results/system99/stage-q.md)及[独立验收](../../results/system99/independent-stage-q.md)
已通过。剩余12目录未被隐藏或误登记。
另确认启动/评审/交接/document refs等外部JSON仍有无界跟随读取，FIFO可永久占住启动锁；该缺陷
进入同一SYSTEM-99批次下一阶段，SYSTEM-99及本轮继续未完成。

Version21阶段P经两路独立分类与方案退回修订后，登记15个JSON/状态型历史包；347个原文件
清单与基线不变，15条record保持unknown且不调用verifier。固定查询扫描252目录，缺record错误
27→12并保留partial/剩余错误；15个show/search/decide均通过。定向46、全库1406
（1398通过/8跳过）、Reader3和同步检查通过；调用脚本的PYTHONPATH遗漏与错误字段名失败已
原样说明并修正重跑。[阶段证据](../../results/system99/stage-p.md)经
[独立验收](../../results/system99/independent-stage-p.md)接受usable-with-scope；剩余12目录、
真实宿主/多轮质量、usage/费用及其它artifact边界继续open，本阶段不算整轮完成。

Version19阶段O以真实临时文件固定TASK双读竞态：绑定OLD摘要的计划曾接受瞬时NEW任务ID，
文件读取后恢复OLD。修复后prepare、validate与publication freeze均从一次至多1 MiB的普通文件
原字节同时取得SHA/UTF-8文本/任务项，并把task source、project-documents及发布候选树身份交叉
核对；修前反例现拒绝且不再二次Path读取。读取后替换、A→B→A、非法编码、超限、目录/FIFO/
符号链接及恰好1 MiB边界均有回归。生成的research-assistant项目文档引用已同步。定向174、
独审前补验40、`-O`定向125、全库1406（1398通过/8跳过）、Reader2和同步通过；
[阶段证据](../../results/system99/stage-o.md)经
[独立验收](../../results/system99/independent-stage-o.md)接受usable-with-scope。无模型质量、
token、性能或跨多文件事务主张；27个未登记目录、真实宿主/多轮质量、usage/费用和其它artifact
读取边界继续open，本检查点不计整轮完成。

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

阶段G已发布并回读main874452cf；Version8阶段H完成现有接口离线编码测量，
[原始结果与范围](../../results/system99/stage-h.md)已独立验收usable-with-scope。
固定cl100k_base的三入口文本26927→19753 tokens，展开精确相等；两种编码、
文本/JSON分别计数。全读33份advice为104966/83045 tokens，但不是实际默认加载；
SYSTEM-99局部视图省略316任务行，不当完整任务包或等价质量对照。主控27项及
独立34项相关回归通过，独立实际重跑数据/负控通过，无生产runtime变更。
新增2607.27250v1正文/局限/附录精读，同批累计14篇。未测真实usage/cache/费用、
任务质量及跨会话更正/异议/依赖召回，不按静态计数删规则或迁移目录；批次仍open。

阶段I已实际派发两原生新上下文并完成独审：全文组3/3、去重组2/3，后者漏掉
语义相关性未经验证的限制。全文组首次工具输出截断后同会话重复补读，公平
配对质量比较inconclusive，未补答或用新会话替换。19分块自报hash核对通过
不等于provider摄入认证；[负结果](../../results/system99/stage-i.md)与原答保留。
原prompt回归14项通过，无生产修改或质量/成本收益。另读两篇正文，同批16篇。
已安装/登录CLI仅能力探测，不是已可调用；Version11阶段J仍待独立方案审核。

阶段J经Version11/12返修、Version13独审approve后唯一CLI探针完成：约80秒
无事件/ack/usage，超时后wait=-15，直接子进程已回收。整组退出认证因跨exec
namespace未知仍inconclusive；[失败记录](../../results/system99/stage-j.md)经独审
只接受失败/unknown，不当后端可用、部署或模型收益。无手动重试或生产改动。
同批正文16篇，但真实宿主、多轮任务质量、完整更正/异议/依赖召回、历史登记
覆盖和总成本仍open。下次先诊断启动接口，不重复旧失败探针或另起优化批次。

阶段K唯一doctor诊断6.09秒返回，21项报告16 ok/5 warning，独审仅接受
诊断观测；raw私有，J根因/模型可调用性仍unknown，未重试模型请求。
Version15阶段L发现并修复消费manifest双读竞态：原消息哈希与实际解析
字节绑定，物理替换/ABA原反例由接受转拒绝，ACK与任务契约不放宽。
[阶段证据](../../results/system99/stage-l.md)：新回归普通/-O各4、交接70、
通信45、更正链1、全库1396（1388通过/8跳过）、Reader3和同步通过。
[独立验收](../../results/system99/independent-stage-l.md)接受有限完整性范围，
普通发布及回读尚待收尾，不标整轮完成；正文阅读补第17篇，
真实宿主/多轮质量/成本、其它artifact全局快照和历史登记覆盖继续open。

阶段L已发布并回读main49bd760。Version17阶段M按独立返修后的方案批量登记
43个结构清晰的历史叶目录，618原文件与基线blob不变；43条只新增unknown历史record，
正式查询缺record错误81→38且partial/剩余错误保留。43个run_id/H1查询可发现；全部
decide_run均verify_delta/unknown且verifier调用0。定向55、全库1396（1388通过/8跳过）、
Reader3及同步通过；[阶段证据](../../results/system99/stage-m.md)经
[独立验收](../../results/system99/independent-stage-m.md)接受usable-with-scope。
没有旧结论复用、模型质量或性能收益；剩余38目录、真实宿主/多轮任务质量、usage/费用、
其它artifact全局快照继续open，本阶段仍不是整轮完成。

Version18阶段N方案经独审发现 `comm20-20261009` 内嵌另一已登记run后两次返修，最终只登记
11个单一顶层Markdown报告目录。358原文件/3349153字节与基线blob一致，11条unknown历史
record逐项绑定且不改旧失败/无效题名；正式查询缺record错误38→27并保留partial和剩余错误。
11个show/search/decide成立，均为verify_delta/unknown且verifier调用0；定向46、全库1396
（1388通过/8跳过）、Reader3及同步通过。[阶段证据](../../results/system99/stage-n.md)经
[独立验收](../../results/system99/independent-stage-n.md)接受usable-with-scope；独审另跑80项
定向测试。27个未登记目录、真实宿主/多轮质量、usage/费用及其它artifact快照仍open，整批
继续未完成。
