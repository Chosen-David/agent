# SYSTEM-99 阶段J独立审核

当前方案结论：**approve Version13**，只限一次90秒既有账号ack探针；历史revise保留如下。当前结果：**仅接受失败/unknown记录，连通性failed/inconclusive**，见文末验收。

## Version11

决定：**revise，未批准调用**。仅审核既有账号的一次ack连通性探针；本角色未调用模型或新增代理，只写本文。HEAD仍为`48db42643844bbb0b9f7ab5935676fdfb75d661f`。

| 冻结对象 | SHA-256 |
| --- | --- |
| SYSTEM-99详情Plan11 | `db93820d4dd8648c14d8f8779a0236057b5f6027cb6f39c9719995b20da91b99` |
| backend-probe-plan.json | `78a3f8a52bcdd3e84a6a93c3502e2ffde5c5065d024f81319f3e645918258e97` |
| probe_backend_j.py | `d493e64bb4549f81ff500c9be16d461dcf0477bd9019e43816c0c5b302b5ed54` |
| backend-capabilities.json | `12d9f2ec4b44059739f182824a9e7e6fdcde2f7754c0a83e1ac2fbea6dfce0af` |
| codex-exec-help.txt | `0e82cfde0122715250e93dc65866caa956b2ac5b9d0b20ec4ad4f9e81486509e` |

已读Plan11、probe-plan、runner、capabilities及stage-I负结果。独立实际运行的CLI仅`--help`与`exec --help`，未发模型调用；argv所用选项均见当前help，未含bypass/search或新增可写目录。列表argv/stdin避免shell插值。help只承诺read-only用于模型shell、ignore-user-config不载CODEX_HOME/config.toml、ephemeral不保存session；不证明禁用全部工具/指令或零文件访问。安装/登录记录不证明后端可调用。

| 七域 | 状态 | 依据 |
| --- | --- | --- |
| intent | pass | 仅ack，不重答I或部署。 |
| guide | pass | guide只读，既有账号，不新增服务/权限。 |
| assumptions | fail | 实际进程cwd及指令预检不满足隔离承诺。 |
| prior_results | pass | I负结果保留；现有CLI证据仅安装/认证，不能复用为ack成功。 |
| acceptance | pass于判据 | 固定输入、真实退出/原事件/最终答复独审，失败保留，无手动重试。 |
| risk | fail | 异常/取消可能遗留已启动进程。 |
| resources | fail | 当前90秒等待另加5秒清理，可能超过总90秒。 |

三项blocking findings及最小修复：

1. `Popen`未传`cwd=cwd`，实际OS cwd继承仓库；`-C`不能代替进程cwd隔离。显式设置cwd，结果记录应证明与argv -C一致。
2. 预检漏`AGENTS.override.md`及CODEX_HOME/HOME的同类全局文件。派发前对空临时cwd、全部祖先及CODEX_HOME/HOME检查AGENTS.md/AGENTS.override.md，存在则不调用；只查存在性，不读认证内容。当前本角色存在性检查未见两类全局文件，但应在runner派发时重验。其它不能核查的默认harness上下文保持unknown，不称完整输入为空。
3. 当前90秒communicate后再TERM/5秒/KILL，且finally只关日志。改为monotonic总deadline（例如85秒运行+至多5秒宽限，总90秒前KILL），超时/取消/异常均只清理自有PG并wait，处理ProcessLookupError竞态，记录退出/清理结果。可用不调用模型的本地短进程核验停止逻辑；不得杀其它作业或重试模型。

主控确认Version11未执行，保存旧版后提交Version12。复审仅需核对这些差异、新hash及全部停止路径；这不是新权限请求。

结果仍需独审真实argv/stdin、原始0600私有stdout/stderr、事件/工具item、最终ack、零错误退出、无超时及进程清理；不能只信exact_ack布尔。只公开脱敏元数据/hash，不公开reasoning或认证内容。内部传输重试若可见则保留；精确模型/usage/cost未知就unknown，ack成功也不证明repository adapter、tmux、质量/费用收益或整批完成。

本次读OpenAI Docs技能；按交接禁止联网，接口判断仅据本地实际help，不引用未获取官方页面。无需全库重跑或论文全文背书。

compact verdict：`decision=revise; checks={intent:pass,guide:pass,assumptions:fail,prior_results:pass,acceptance:pass,risk:fail,resources:fail}; blocking_findings=[process-cwd,instruction-precheck,wall-budget-and-cleanup]`。

## Result

pending / not invoked。

## Version12差异复审

决定：**revise，仍未批准真实调用**。v11三份保存原件hash与上表一致；当前新hash：

| 对象 | SHA-256 |
| --- | --- |
| SYSTEM-99详情Plan12 | `40ac421e457d4c467988a7fff44b8dc907b844e9669f73041bd56fde5b0b8353` |
| backend-probe-plan.json | `f02dbca5ab7c6cd0efdd682adeb37797201194d242e10144251be5d6aec03ca1` |
| probe_backend_j.py | `0eff72e9b5ed66a5d196e420320b4bdbe2015eaaf22511dfb418fc1a54374156` |

已关闭：Popen显式cwd与-C一致；祖先及HOME/CODEX_HOME两种AGENTS存在即abort；monotonic总deadline预留10秒，finally先TERM至多5秒、再KILL并在剩余时间wait，退出竞态/超预算/未回收显式记录。默认harness指令保持unknown，没有扩大连通性结论。

剩余blocking：默认SIGTERM会直接终止Python进程，`except BaseException`不会把这个信号转成Python异常，因而不执行finally。CLI已通过start_new_session进入独立进程组，此类取消可遗留CLI；上一轮“取消也清理”的要求尚未关闭。最小修复：派发前安装SIGTERM处理器，将其转入受控异常和finally清理，记录取消标识；现有SIGINT/普通异常/超时路径保留。不要求声称能处理不可捕获的SIGKILL。

最小复验：主控既定纯Python ack/忽略TERM超时/启动异常自测之外，加runner收到SIGTERM的取消例，核对自有PG停止和退出/取消记录；不调用模型、不换真实argv或探针身份。修复后只需新hash与这个差异复审。

七域：`intent=pass, guide=pass, assumptions=pass, prior_results=pass, acceptance=pass, risk=fail(SIGTERM cleanup), resources=pass`；`decision=revise; blocking_findings=[sigterm-cancellation-cleanup]`。尚无模型调用或ack结果。

## Version13差异复审（当前有效）

决定：**approve**。独立diff确认仅增加SIGTERM/SIGINT受控取消：Popen赋值期间记录信号，持有proc后抛ProbeCancelled；finally忽略后续可捕获取消并清理自有PG，最后恢复handler。之前cwd、指令预检、90秒总deadline保持；SIGKILL/关机不承诺处理，原阻塞项已关闭。

| 新对象 | SHA-256 |
| --- | --- |
| SYSTEM-99详情Plan13 | `649667edf8651a1266c3069e1047e0d64de709a569fde5e14e7b0801c2effaf9` |
| backend-probe-plan.json | `f81de4e488f9ec4196271f400b5ccf6495942cc52361db753bb282cd80e77293` |
| probe_backend_j.py | `be0335c00220ac2282a3b0449a444481da66452b73bb1f8b0203ae0d862db6b4` |
| backend-j-fake-tests.json | `693d565fc143f6b6fdd8675c68828127f70a61ca3929d7f4fd3b120a4e639fc0` |
| backend-j-cancel-test.json | `c9e02158970869f0c6e4f3e8d1109528cffa6e125e780946f4839e6d538f5efa` |

已读主控纯Python自测记录：ack退出0、忽略TERM超时后-9、启动异常FileNotFoundError；取消例记录signal15/ProbeCancelled、子进程-9且child_gone=true、约5.03秒无预算超限。它们是主控自测数据，本角色未把JSON自报当独立结果验收，也未重跑模型；真实调用后仍须核对原始日志与清理结果。保存的Plan12/runner12哈希与上节一致。

七域均pass：目标/授权/历史取舍未变，隔离与可捕获取消机制已补，真实ack/事件/退出/清理仍按冻结条件独审，90秒资源上限及失败不重试保持。`decision=approve; plan_version=13; checks={intent:pass,guide:pass,assumptions:pass,prior_results:pass,acceptance:pass,risk:pass,resources:pass}; blocking_findings=[]`。

仅批准主控一次固定argv/stdin真实探针，不补答I、不改凭据或全局配置、不部署adapter。失败/超时/取消/工具调用均保留；精确provider版本/不可观察harness上下文及费用未知，不因登录或ack推断质量/部署。此时真实CLI尚未调用，结果pending。

## Version13结果验收

结论：**usable-with-scope，仅接受这次失败/unknown证据**；连通性为failed/inconclusive，不能称模型后端可用。主控实际调用session44893的runner退出0，不等于CLI成功：子进程wait返回-15、timeout=true、约80.008599秒终止，未超过90秒预算。stdout/stderr均实际0 bytes，SHA均为`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；没有event、ack或usage。未手动重试，未补答I。

已独立读取私有stdin、invocation、summary、console及空原日志。公开inputs的plan/capabilities逐字段与原件相等，runner完整源码/哈希与已批版本相等；observations的summary/invocation/两组假进程记录与私有原件逐字段相等。stdin精确匹配210-byte冻结prompt；argv仅把placeholder替换为空/tmp路径，summary与invocation一致；源码Popen显式使用同一cwd，临时目录现已删除。未将静态代码检查冒充运行时provider完整输入认证。

| 证据 | SHA-256 |
| --- | --- |
| inputs-j.json | `6e2919502701c131982c4daaa937718baab8227bed21981601ea4275bcd67613` |
| observations-j.json | `c8bc45287b6669f957a342763003a61c676c3216549ea50cea8c0b7d4ba2a377` |
| 实际stdin | `306c0bbaa675c478524fb25af91b934afe9e14ea1e5414032b8fae89ae316be5` |
| invocation.json | `fcc69ea99126d6977728a4aac9788480f5a32c36105f913b9bc550d610e52ab4` |
| summary-private.json | `4c2937e8aa50b1d22d163cb334d702ea3939f62a767fff205a94f6f19b1d1cb3` |
| invocation-console.log | `4d35b116babe06529f836e75e90aa67e49cd1e9d31a6c729edadbc33ecdae0a2` |

| 六域 | 验收与限制 |
| --- | --- |
| implementation | pass于冻结实现：真实输入快照/runner hash未变，stdin/argv一致，finally对自有PG发送TERM/KILL并wait；不是仅信exact_ack布尔。 |
| reference_boundary | pass于失败判定：参考要求ack；实际无任何输出，exact_ack=false，零parse errors仅因空文件，不是有效事件流。 |
| data_integrity | pass于保存记录：公开/私有对象及hash一致，原stdout/stderr权限0600；真实调用来自主控宿主记录，无provider事件可进一步认证。 |
| numerical_sanity | pass：0-byte/hash对应、80.008599≤90、CLI -15与runner0区分；usage缺失为unknown，不能写0 tokens/0费用。 |
| measurement_validity | pass仅于有界失败观察：预留10秒后超时清理，不当性能基准。请求是否到provider、失败原因、内部重试、精确model均unknown；不可由空日志判定后端整体不可用。 |
| reproducibility | pass于静态输入/代码/日志复核；未重跑CLI。假进程自测不是模型实验或独立provider验证，实际连通性可重现性未知。 |

清理范围：同一runner调用的wait取得子进程-15且未报告cleanup_unreaped，支持leader已回收；代码在finally处理自有组信号。另一次exec的killpg(7,0)返回不存在，但PID namespace等价未认证，**不能证明原namespace整组已退出**，此项仍inconclusive，不伪称完整清理认证。无provider事件也不能认证模型未读文件或未用其它工具。

因此只允许消费“已安装/已登录CLI的一次有界ack尝试超时，保存日志为空及上述清理范围/未知”的事实。ack成功门槛未过、整组最终缺席未认证；不能宣称后端可用/永久不可用、repository adapter、监督恢复、模型质量或费用收益。没有reasoning或认证内容被公开；没有新增调用、全库重跑或跨仓库工作。
