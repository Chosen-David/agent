# 独立结果验收：标量 Freedman 方差预算

Reviewer: `/root/knowledge_result`（宿主实际委派的新独立上下文）
Task: `EK-20261008-0915`
Current decision: **science usable-with-scope；publication blocked。整合后相对原始基线有1项逐查询退化，原冻结门槛不允许发布。下文较早批准仅为整合前历史，不再授权当前发布。**

本审核只写本轮 independent_cases.json、independent_verify.py、independent_results.json、independent_review.md；按主控补充授权在 /tmp 建立隔离 SQLite 索引。未改卡片、TASK、生产代码或旧 neuro 项。只读保留集公开 metadata；未读其目标论文、答案、图或结果。

## 核查对象与方法

先读 AGENTS、decision_review、project_document_workflow、FORMAT、result_validation、当前 TASK、本轮 plan/baseline/sources、新卡 JSON/正文，再读实际 verify.py 与 checks.json。初始目录检索定位了本轮与既有结果；原有开发数据只作为被复算对象，不冒充本轮新样例。新样例先写 independent_cases.json 并固定 SHA-256 `a46ed6d963fb3a6514d49857571581c6886f26278096c0c3800864bd8e238c7d`，之后才写、执行独立验证器。命令、时间、Python 版本、输入与代码哈希、逐例结果保存在 independent_results.json。

审核未运行或 import 生产者 verify.py。独立程序对其九个条件依赖正例穷举每条完整叶路径并追踪所有前缀，与生产者吸收路径合并算法不同；1024 步反例用非越界路径的整数计数补事件，与生产者累计吸收计数相互核验。九个分数与 1024 步完整精确分数全部一致，另独立重算其反例数值与根。

## 来源与证明

独立实际浏览 [固定 arXiv v1](https://arxiv.org/html/1101.3039v1) 的 §1.2、§2.3、§3，以及[作者 PDF](https://tropp.caltech.edu/papers/Tro11-Freedmans-Inequality.pdf)的可读取文本。v1 的定理行出现双负号异常；§2.3 的指数超鞅尾界、§3 的 Bennett 指数及数值放缩明确支持负指数。PDF 截图调用失败，未取得原始字节，因此不宣称视觉原页确认、原 PDF 哈希或版本字节一致。

独立标量证明核对通过：积分余项随 d 单调，允许 d 任意负但要求平方可积；k! 的级数放缩成立。条件 mgf 及 M_t 的可积非负超鞅性质成立。首次联合越界 τ 的有限截断给 E M_(τ∧n)≤1，再取事件单调极限，足以覆盖无限离散时域，不需要宣称 τ 几乎必然有限。θ=x/(v+Rx/3) 在 x>0、v>0 时属于 (0,3/R)，代入恰给目标指数；x=0 单独概率≤1。反演为正二次根，v 为测量单位平方。R=0 的退化过程与 v=0 的排除均明确。

确定 x,v 和条件零均值是实质前提。V 是条件二阶矩之和，不是样本方差。任意停止时刻的事件是最大事件子集；保证联合概率，不能除以预算事件概率后仍保留 δ。仅 D≤R 不能将 −D 也当作上界为 R。双侧另有绝对值界时分配 δ/2 正确。完整展开无需把 related 导航边当 requires。

三个正文拒用例都成立：++ 的经验方差为零但 V_2=2；非对称增量翻负尾必须改 R；变化预算边界 b_n=2+sqrt(6n) 逐点满足 b_n²≥6n+2b_n，但独立精确有限递推重现 .060713409787025684>exp(−3)，足以拒绝未校准的逐时刻直接代入。

## 新样例与第一轮结果

1. 与生产分布不同的条件依赖两点律：a 由前一个创新符号决定，取 2 或 1/3；D=+a 概率2/5、−2a/3 概率3/5。128 条完整路径，7步、x=3、v=6、R=2；每个条件均值精确为0，二阶矩为2a²/3。最大联合事件概率4/25≤.569782824730923，终点事件为0，检出了“只看终点”的错误替代。
2. 一个公平符号重复10次：每步边际均值为0，第二步起条件均值非零。实际上尾1/2超过伪 Freedman 界，拒用通过。
3. 公平步行在前两步++时 τ=2，否则 τ=3。x=v=2 时联合概率1/4，预算条件下概率1；将预算减到1.99后联合事件为空。检验了联合/条件、停止与预算等号。
4. 新单侧分布 +2 概率.9、−18 概率.1，均值0、V=36。错误负尾 R=2 给界小于.1，正确 R=18 给界大于.1。
5. 新参数 R=2、v=13/7、δ=.2/.007，缩放1/7及13，反演与单位不变性通过；t=0、τ=∞、R=0退化解释及公式域拒绝均核查。
6. refs 检查确认无强依赖时仅需自身固定引用；三条 related 可导航，不造成假的证明依赖。旧哈希/版本拒绝；隔离 published 有效，主库 candidate 不可作为已发布引用。第一轮 candidate 检查在 get 处提前拒绝；后续验证器已明确使用 include_unpublished 再调用 check_refs，保证直接覆盖后者。原执行源码已按原 SHA 完整存入首轮结果。
7. 冻结中文新查询双后端 top1，无意义字符串均无命中。冻结英文 `adapted martingale difference predictable quadratic variation budget` 在 files 与 sqlite 的 top3、完整 context 都未命中新卡；原始失败完整保留，不能看结果后删查询或降低阈值。允许只补正常英文数学表述，保留失败，重新运行同一协议并复查旧回归；修复后该查询属于已曝光回归，不再称为对生产者未见。

## 旧检索与验收边界

已读实际 scripts/eval_knowledge.py、KnowledgeStore 和索引查询实现，并逐 suite/backend/case 核对 baseline 与 candidate 的 query、expected、raw Recall@3、context recall、no-hit。原始、round2、morphology 全部旧逐例上述必要指标无新退化；reciprocal rank 另列。三个 candidate 命令退出码均为1，继承 baseline 缺口；不得写成三个套件通过。计时不在本验收范围，也不能用这些词法测试推断模型建模效果。

原 plan 明确接受旧检索无新退化，而非修复所有继承缺口。因此继承失败本身不阻止本科学条目的零退化范围发布；第一轮实际阻塞是本轮冻结新英文检索失败（已在后续返修中解除）。主体数学、原开发数据与新合成测试可单独标 usable-with-scope。非形式化证明；有限枚举不证明无限路径定理、真实传感器收益或通用正确性。

最终整体批准还依赖主控完成新英文表达返修、旧逐例重检、卡片与包/refs最终版本绑定和必要全量回归，并在唯一 TASK 中映射本轮任务。目前 TASK 尚无本轮ID，已通知唯一维护者；不由本审核代理自行写入。

## 返修与第三轮独立复测

第一轮10组为9通过、1失败：中文/无命中查询正确，英文两后端失败。第二轮仅补常见英文 alias 后仍为9通过、1失败：files 英文 top1，但 sqlite 仍失败。随后生产者加入正常英文 scope 说明，与中文数学前提一致，包含固定预算与禁止经验方差代入的限定；没有改变定理、降低阈值或删除查询。第三轮有效执行10组全部通过。该英文查询修复后已曝光，属于回归通过，不能宣称首次未见测试全部通过。所有历史结果和各轮实际执行源码及哈希保存在 independent_results.json 的 prior_runs 内。

第三轮还通过当前 KnowledgeStore/indexed_search 独立执行全部旧查询，分别重算 top3 IDs、原始召回、按原 context_limit 构造的上下文召回和无命中结果，与生产者 candidate 原始数据逐例一致，同时相对 baseline 无新增退化。原套件退出1仍为失败；结果可用于零退化结论，不能用来宣称套件达标。

验证器扩展了 --corpus-root 参数，以供正式 published 根最终重跑；按主库实际 status 检查 candidate 引用被拒绝或 published 引用被接受。最早的候选检查拒绝发生在 get，第二轮已明确改用 include_unpublished 后由 check_refs 拒绝；第三轮亦直接验证 check_refs。根反演补充显式检查另一二次根为负。添加参数支持时一次独立程序的域检查循环遮蔽了 argparse 变量，运行在检索前报 AttributeError；已改变量名，异常与当次源码保存在 verifier_instrumentation_errors 中，不当作一轮有效检索数据或隐藏失败。

当前无数学/原始数据返修项。前述“当前真正阻塞是新英文检索”属于第一轮历史状态，已由上述同协议返修重测解除。仅限这里列出的有限合成检查、非形式化推导审核及特定语料的词法检索；不保证一般英文语义检索、生产模型或真实任务效果。最终status/proof改变后需再固定实际内容引用；主控仍负责TASK映射、打包、全量测试和授权发布回读。

## 最终正式根与集成验收

正式 `/workspace/agent/knowledge` 的第四轮10组全部通过；冻结用例文件未变。卡片现为 published / derivation-reviewed，正文与第三轮数学内容一致，插件镜像的卡 JSON/正文逐字节一致。实际引用：`math.freedman-variance-budget` v1，内容哈希 `bdf13e38bf31e2bb3079885c6afb5e2729d65811bca8722f0e134e524d314083`。最终验收输入包括卡字节、生产代码/原始数据、最终三组检索文件、全部命令和日志；actual SHA-256 绑定见 independent_results.json 的 input_hashes/final_integration.artifact_hashes。

从隔离根切正式根时，索引实现正确拒绝另一语料root的缓存（KnowledgeError）；独立程序改为每个root派生不同缓存文件名后重跑，未放宽索引校验。此工具接线异常连同源码已留存在 prior_runs 的 verifier_instrumentation_errors，不能省略为首次运行即成功。

独立读取实际 run_checks.py、final-commands.json 和日志：validate、sync、sync-check、index、diff-check 均退出0；全项目测试 **851项，OK，1项skip**，skip为需真实tmux/Unix socket且默认opt-in的测试；reader **3项，OK**。原始/round2/morphology仍各退出1，其继承失败如实保留。最终三组42条suite/backend/query的原始IDs、raw recall、context recall、no-hit逐项等于第四轮正式根独立查询所验证的candidate数值，且相对baseline无新增退化。

coverage只追加本项覆盖与限制，learning_state保留原next_topic和其他域游标，upstreams明确原始PDF哈希为null；旧neuro卡未在变更集合中。TASK已增加本轮ID和详情，主控将追加最后状态。README/导航仅介绍本项可用范围，没有模型收益声明。

**发布意见：允许在上述scope内发布。** 没有剩余数学、数据或本轮检索/集成阻塞；继承检索缺口、一次tmux测试跳过、无原PDF字节哈希、未做模型/GPU/形式化认证以及旧neuro lineage阻塞均必须继续披露。远端提交、推送、SHA读回和最终TASK勾选不是本审核代理执行的动作，交由主控按原授权完成。

## 并发整合后的最终裁定：禁止本轮发布

主控同步到并发 HEAD `59ad8d962ce934085f76171f651370ef5dcd9944`，新增 `math.floating-dot-enclosure`，语料变为99条/96 published。保持双方改动后，独立再次运行正式根。科学、新表达、refs及相对“该HEAD但未加入Freedman”的 integrated-baseline 检查均通过；但相对本轮最初 baseline 的完整门槛 **失败**：

- suite=original，backend=sqlite，case=english-alias，query=`dot product error inner product bound`；raw Recall@3 从1降到0，context recall仍1。
- 原 top3 为 `ds.faiss-exact-vector`, `math.linear-solve-backward-error`, `math.cauchy-schwarz`；并发新基线与整合最终 top3 都为 `ds.faiss-exact-vector`, `math.floating-dot-enclosure`, `math.linear-solve-backward-error`。
- 未含本项的 integrated-baseline 已复现同一退化，因此不是Freedman增量造成；但这不豁免原始全查询非退化门槛。42条对应比较与原始失败状态已保留。

新增的第五轮执行结果最初按“只接受本项边际scope”给出 usable-with-scope，同时明确 all_checks_passed=false；主控明确否决用边际scope替换原冻结门槛。本审核接受该裁定：将总体最终 acceptance 明确改为 publication-blocked，保留执行时边际判断、原源码及数据为历史。当前验证器也已改为原门槛失败即阻止发布，未在回退candidate后伪装重跑published测试。

**科学结论继续 usable-with-scope，整体发布禁止。** 主控将本项恢复candidate，撤回仅本轮的published覆盖/history/导航增量，保留其它并发工作、完整原始/返修/整合数据、TASK pending。不会修改无关卡或检索引擎来赶过门槛，也不推送本轮成果。此前“允许发布”只对应整合前snapshot，已经被新证据撤销。

恢复条件：并发引入的逐查询退化得到修复，或者用户明确接受版本化重编排的新验收范围；随后重新整合检索、固定新输入并独立验收。旧neuro lineage与其它已披露限制不因本项科学审核通过而解除。

## 候选隔离保存的最终只读核验

最终候选路径为 `agent_doc/results/knowledge-freedman-20261008T0915Z/candidate/math.freedman-variance-budget.{json,md}`，并未注册到canonical entries。JSON 为 candidate/derivation-reviewed；正文SHA仍为 `014a071af03dc39f71ff874cff3e126d5193463660dc0c59f37f2a59637bda1e`，与科学已验版本完全相同。独立确认主知识库和插件镜像的新卡文件均不存在；README、coverage、learning_state、upstreams、公开holdout metadata和旧neuro两文件实际字节等于整合HEAD，不以生产者preservation标签代替比对。

已读候选保存的6条命令/日志：候选临时语料格式、恢复后的正式库格式、插件同步检查、重建索引、知识专项74项测试、diff-check均退出0。整合后的完整851项测试为OK/1个原tmux opt-in skip，Reader3项OK。结果及实际哈希已附到 independent_results.json 的 candidate_preservation_review。当前不需要重复不受影响的科学枚举或把候选误当published重跑引用；此前published-root测试仅作历史。

最终交付为可继续的候选与审核证据，**没有发布批准、没有提交/推送**。唯一任务保持pending，恢复条件与责任交回主控。

## 新明确授权下的待审工件归档意见

主控随后转达用户明确要求持久保存待审工件，允许规则内提交工件但不发布知识卡。本审核将两种动作分开：**science usable-with-scope；知识发布 blocked；仅待审工件 Git 归档允许。** 此意见不把候选注册为published，不放宽原始非退化门槛，也不声称已经执行了提交/推送。前段“没有提交/推送”为当时历史状态。

独立核验 candidate-history-manifest.json 的5版/10个文件实际字节哈希；五轮独立执行记录中的10个候选JSON/正文输入哈希全部找到精确保存的版本，各轮完整验证器源码的SHA也全部匹配。不只保留哈希而丢失原内容。原始冻结用例、两轮检索失败、返修、两次验证器接线错误、整合失败及后来否决的边际放行判断均在历史中。

retrieval-diagnosis.json 的排名与原始数据相符；最小后续诊断只建议固定前后语料的逐lane排名审查，禁止改expected答案、塞入精确query或本轮改检索引擎。resume.json给出candidate路径/哈希、真实旧/新HEAD、原始门槛恢复条件、refs/打包/独立验收链和旧neuro不可重置的限制。当前resume版本与历史manifest及所有快照另绑定在 independent_results.json.archive_review。

归档范围仅限本轮result目录、TASK pending及detail、docs导航。公开论文元数据与人工合成数据未发现私稿、保留目标内容或凭据；对待归档路径执行常见凭据前缀扫描无命中，此检查不宣称穷尽所有秘密形式。主知识、插件和其它域内容仍保持整合HEAD。主控负责实际archive提交/推送与远端读回，并准确标注“待审工件归档”而不是“知识发布成功”。
