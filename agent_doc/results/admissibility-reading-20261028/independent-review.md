# SYSTEM-99 / Plan54：2610.07309v1 独立原源与静态源码审核

Decision: **accept — usable-with-scope**。Blocking findings: **0**。

本记录只验固定阅读草稿及其对当前源码的有限映射，不是方案重新批准、实验验收、provider/runtime认证或SYSTEM-99结案。独立角色实际调用1次；无角色重试、测试、实验模型/CLI后端probe、安装、后台任务或旧耗尽门禁重开。全部角色tokens/费用unknown。未修改任何生产、guide、TASK或计数；28→29、发布与公开回读由主控另行负责。主控持锁；本角色没有获取或竞争该锁。

## 1. 固定审核对象与读取范围

项目：`/workspace/scratch/95d615402a52/agent-run-1202`。实际`git rev-parse HEAD`为`d738218300d2bec2ad61e802866c28726c719964`。只允许本报告路径写入；本次没有pull/fetch或修改目标checkout。

固定对象实测SHA256：

| 对象 | SHA256 |
|---|---|
| `agent_doc/results/admissibility-reading-20261028/reading.md` | `0964d3887865a51f8dcf29c9631c0251669b7f34c446087f7329417c3c5ead9e` |
| 同目录 `inputs.json` | `cf2c3c42ec5e21bee4722d07c260f45c8b34ccf5222cf5b4cc38aa5be9006990` |
| `.agent-runs/continuation-1758/2610.07309v1.txt` | `27701e8bae8a19bf43dd13f31de928df37a1dc7bd1188325fbc3c6873bfb996d` |
| 同目录 `2610.07309v1.html` | `33ef71543fb56bb1727e23a7ab25a6ab933dd883bfd2e5802e0b8c093835119f` |
| 同目录 `abstract.html` | `0ba64edb638ac07a3f28c59021ba3fe8f1fa37e1795f4acda71472a73817bc10` |

实际独立读取TXT的Python Unicode字符半开区间：`[0,20500)`、`[20500,39322)`、`[48197,64004)`、`[66407,79000)`、`[79000,89576)`；全文件89576字符。合并实际正文范围是`[0,39322)`、`[48197,64004)`、`[66407,89576)`。这覆盖main §§1–6、A–E/H–N，Equations1–26、Tables1–7/9–17、Figure1–3/5–13的范围内图注。`[39322,48197)` references、`[64004,66407)` F/G未读；未看渲染图片/PDF、作者代码、作者raw数据，也没有统计复算。TXT无换行，故采用字符偏移而不伪造行/页码。

HTML实际做section ID目录检查，映射S1–S6及A1–A14；没有将此目录读取冒称独立逐段HTML或渲染核验。另用标准库HTMLParser实际读取abstract页面文本，确认标题、五位作者、v1和2026-10-05 19:47:43UTC提交。主源正文阅读采用上述TXT，而非主控摘要。

精确原文导航：framework§3.1从字符9213；§3.2从11145；§3.4从15386；§4从21816；§5从31094；§6从38620；A从48197；B从49113；C从51623；D从59563；E从61012；H读取起点66407；I从68609；J从78603；K从81145；L从82668；M从83423；M.1从85813；N从87538。HTML对应`S3.SS1`/`S3.SS2`/`S3.SS4`/`S4`/`S5`/`A2`/`A3`/`A4`/`A5`/`A8`–`A14`。

治理实际读取：AGENTS全文；project_document_workflow的权威/guide只读/唯一TASK/来源绑定/恢复/独立验收部分；project_memory_workflow全文88行；knowledge_access_workflow全文52行；code_reading_workflow与paper_reading_companion_workflow；agent_communication_workflow85–130行；dual_main与decision_review的审核/授权/耗尽边界。部分大合并输出被工具截断，未将被截断部分计作完整阅读；本报告只引用已实际可见规则。TASK实际检查SYSTEM-99索引行103；SYSTEM-99检查Version54、开头目标/阶段及183–196行AJ计划与最新reading Progress，不声称重审所有旧阶段。GUIDE为空；实际读取guide/README说明，保护整个guide目录；`.agents/skills`未发现本地文件。未启动任何规划/调度。

## 2. 原文核对结论

1. **accept：资格与相关性分开、历史查询例外有条件。** §3.2/Eqs1–3以三值Kleene conjunction区分admissibility与usability；来源明确历史查询可能需要旧状态。§3.1与B把namespace限定为可信主体来源而非topic/text推断，所需anchor在支持集内且内部打分不变才有rank不恶化；B明确排除不可信结构写入影响选择的graph selector。草稿没有将它变成安全定理或本库stale放行权。
2. **accept：未知、召回与分母完整。** §3.3区分evaluator unresolved和verifier abstention；E≤R≤W与最终target disclosure分别记。§3.4/Eqs5–10、C/Eqs13–26保持required anchors固定、最小达标前缀、所有前项收费；无anchor不纳入召回、零known分母undefined；lower/upper bounds、coverage与any/count共同防fraction稀释。unit infeasibility penalty的loss不能说成条件污染概率，source-macro乘积不能代替逐query平均。草稿均正确。
3. **accept：冻结路由与后验分析不混合。** §4、I/Table13、M/Table17分别标注165个开发候选/top100选择、冻结v1、top20的B=U→B=A post-hoc scoring correction、policy不依赖intent的released-field v2 untuned attribution、两reader预定及Luna sequential replication。没有重新调rank/超参的声称。开发96拆24校准/72分析，不是3767评估样本的同一总体。
4. **accept：主要收益由可达性贡献且成功很有限。** §5/Table2仅31.1%达80%recall；loss差-.085中-.074由feasibility贡献，原文明述87%。去掉scope后namespace upper risk .126略高于global .123；policy exposure .094→.101。Tables3/5/6及Figures9–10的随机等池、deep postfilter、gold-anchor oracle、同一609可行query、缺失judgment控制均有读取，不把oracle当部署方案或98.3% candidate score工作减少当latency。
5. **accept：标签有效性、false denial与过滤负结果被保留。** §4.1、§5、E/Table7的prohibited α=.0829、lifecycle α=.6703均与草稿一致；高raw agreement不认证policy ground truth。H/Table9/Figure7的1%必需anchor false-denial约束下Sol只有retain-all检测零，Gemini无测试阈值合格；不是“模型完全不会识别”。更多metadata/text过滤会损失recall/accuracy，部分Gemini stale disclosure增加；corruption bracket只针对网格，不是部署容错阈值。
6. **accept：关联与受控marker界限清楚。** §5、I/Tables10–12的1523配对天然reader数据仍因recall同时改变而非因果；RHELM仅七组，judge共享与200输出audit有限。J的GateMem exposure predictor/discordant route差不是随机证据，G3=G2因release无显式pre-query delete/supersede。K受控实验192pairs/384requests每reader、16scenario、stateless/interleaved，只改变该候选是否曝光；unique literal marker连refusal也算，不代表有用回答/内部因果使用。只有DeepSeek relevant-inadmissible区间排零，不可外推模型排名、总体泄漏率或安全。
7. **accept：成本没有过度归因。** M.1报告30795requests/$75.76、至少14.91M input/1.82M output tokens，历史部分receipt无token，项目支出>$500且含不可归属pilots/failures。B对source-execution hardware记录不完整的限制保留；CPU复核机配置不能补齐历史embedding账。草稿明确作者报告而非本地复现账单，也不声称完整engineering/all-role成本或本库收益。

### 非阻塞原文疑点 N1

§3.2一方面规定current记录ℓ=1，另一方面说任一输入unresolved得?；C/Eq24也同时列current→1和`state unresolved or intent unresolved`→?。对于`state=current, intent=unresolved`两行条件相交，优先级未写明。本文未读作者实现且任务排除作者code，不能补造实现解答。当前草稿没有展开或依赖这个交叉真值表，故不阻塞其评价方向；若以后实现同一evaluator，应先固定该情形的合同/原作者澄清。此疑点不等于已确认本库bug。

## 3. 本库消费者门禁与历史记录

固定源码SHA256：

| 路径 | SHA256 |
|---|---|
| `agent_runtime/project_memory.py` | `1f0fe4edc8abf2371972817083c2c12cc33dbb07640ed57dffc2d8a744b35e41` |
| `agent_runtime/handoff_basis.py` | `20b4e127726f046b564086d2c5028ba92e986c6b796784a23cfe94971071f50a` |
| `workflows/project_memory_workflow.md` | `4522bd15ed5ade12e40f2f18a2c4c840a2a8f539d8625fae0aef177ced7566aa` |
| `agent_doc/task/TASK.md` | `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f` |
| `agent_doc/task/task_details/SYSTEM-99.md` | `2695fac1b1019d02b6a8b985149ee776fb964795b3ed2652e2b7b61553ac20b5` |
| `agent_doc/guide/GUIDE.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

实际静态读取位置：project_memory.py179–266、280–400、531–538（并用rg导航相关定义）；handoff_basis.py1–190、270–376。未调用MemoryLedger、不读私有数据库、不执行check或更正。这是**static source fact/inference**，不是executed行为证据。

- `_walk`189–227每个root/传递deps都要求active（210–211），绑定文档需当前有效（212–218），不是只看目录/hash。`_insert`230–264拒绝复用已有ID，非candidate依赖执行_check。`_revise`284–314新ID、新revision，旧项superseded、非superseded后代stale；禁止新revision依赖失效lineage；correct/accept316–326委托该路径。
- `check`328–343走_walk或兼容_check；`list`372–377默认active但提供all/stale历史导航；`history`531–534返完整entry及sequence序事件。**读取history/历史raw不等于它作为当前basis被放行**。workflow更正条款3–5保持原观测、不自动激活旧后代；当前active新解释若使用历史原件，仍需新身份、适用范围和独立验收。草稿对此已写对。
- `check_handoff_basis`144–187：可信request要求knowledge/memory标记、required refs子集、required_claim_ids必须存在且supported；memory required/supplied都经ledger.check。`claim_graph`88–141对声明前提与artifact、supported祖先闭包做结构限制，不判自然语言充分性/真实性。known无依赖兼容路径不能证明所有遗漏会自动被发现。
- `basis_context`270–376首先check，消费者硬预算另验；选择闭包保留必需项与所有candidate/rejected（304–330），memory水合及known hints还要当前check（346–364）。当前上下文hint不是曾读缓存，artifact refs不是模型收到正文；手工审查也不认证真实host、主体、权限或完整provider输入。

结论：草稿的“论文历史事实可适用不能直接映射成允许stale解释进入当前有效basis”与源码一致。**reject迁移主张**：不能由这篇论文新增自动historical bypass、默认current-only删除或文本过滤器；草稿已暂缓这些变化，无需返修。

## 4. 实际知识检索与适用性

实际执行只读知识查询（不是测试/模型/后端probe）：

`python -B -m agent_runtime.knowledge --root knowledge search 'retrieval admissibility authenticated provenance namespace lifecycle' --limit 3`

实际返回schema1，backend=`files-lexical-v1`，snapshot=`767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`，applicability=`unchecked`；唯一命中`impl.flashinfer-plan-run@1`，sha=`6298cd56a7d5fd2353b0b73ddfaece642584620cc8c53f5ba302dd5957d7f5cf`，score1只因lifecycle。**reject**：其对象是GPU paged/ragged attention plan/run，不能支持主体授权/记忆生命周期，也没有必要加载其全文。无适用知识refs被采用。

另一次rg文件检索`admissib|provenance|false.denial|namespace|retrieval|top.k|rank|单调|排序|召回`输出截断，仅作不完整导航，不声称全语料零遗漏。在导航后实际读了以下JSON和MD全文：

- `math.topk-margin@1`：JSON SHA `b8ead812eaa929e1a34514f9e205e951b02e3f21aef16b138fb4f8655b4c8814`，MD SHA `96415e0b70a02a5d045da4b0f230028f1b61bbc5572a602349816b878009aeb8`。**reject作为本任务定理依据**：它需要逐项误差与严格margin，本文是固定score下删候选的rank单调性，非近似score误差问题；未加载其Cauchy-Schwarz强依赖，因此未应用或宣称完成check-refs。
- `math.data-processing-task-sufficiency@1`：JSON SHA `53a6d9f9632c49ba13070d153d8e0fcfbb56f6db527010bbd037080b7328a84e`，MD SHA `35cca0800cfe7b17291970b8f29bee7765336e4dffe49aa540e7afcb22cfc58c`。**reject作为本库质量认证**：有限字母联合分布/Markov/任务后验条件在真实LLM输入未知，不能从短文本或哈希认证保留质量；仅保留“不能误用”边界，无DPI数值或部署结论。

知识查询未产生新实验数据、没有新建knowledge-use并竞争其它作者路径。使用证据完整记录在本唯一获准报告内，accepted `knowledge_refs=[]`。

## 5. 操作异常、未决与最终决定

一次辅助HTML解析尝试因`bs4`未安装而抛ModuleNotFoundError；没有安装、没有重跑角色或调用作者代码。随后直接用Python标准库HTMLParser读取已固定本地HTML并获得上述identity/section导航；这不改变正文审查范围。若干大合并读输出被工具截断，已用明确区间补读原源，未把导航或未显示文本算成已读。

最终：**accept本固定reading.md及inputs.json，限本报告实际正文/静态源码范围**；blocking findings零，非阻塞原文N1保留，不要求当前草稿返修。手工独立角色审核不满足受信runtime/provider认证，不改变历史登记unknown。SYSTEM-99/Plan54、旧额度、真实宿主/完整实际输入/最终任务质量/全部角色成本等未决保持。没有自行计入第29篇、关闭任务或批准新实现/实验。
