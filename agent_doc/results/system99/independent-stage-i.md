# SYSTEM-99 阶段I独立审核

## Plan

当前决定：**approve Version10**，仅限回答与可核对输入声明的代码理解初探，见文末“Version10复审”。Version9初审approve已撤回、随后revise的完整历史保留；不得把新版批准解释为完整读取或无越界认证。

初审决定（已被下方revise取代）：approve，仅批准 Version9 阶段I、冻结 pilot-plan 和 rubric 所述的两次原生宿主只读代码阅读初探。每臂一个 `fork_turns=none` 新上下文、同一默认模型设置、完整指定包、三个问题、一次调用、无重试。不是 repository runtime/ReviewSession 部署或认证回执，不批准统计非退化、真实usage/费用、普遍质量/性能或 SYSTEM-99 整批完成主张。结果在独立验收前仍为 pending。

审核角色为宿主分派的 `/root/agent_pilot_i_verify`；本角色不派发实验AI，不改源码、任务、guide、包或rubric，只写本文。按本次交接禁止联网，未执行fetch/pull或发布；保留主控单写和冻结基线。实际读取 AGENTS、decision_review、review_main、项目文档治理、双主、结果复用与结果验收workflow、唯一TASK中的SYSTEM-99、完整详情Plan9/Progress、GUIDE及目录README、pilot-plan/rubric、builder/manifest，以及对应实际源码。GUIDE是零字节；README自述是此前明确授权的一次性AI说明，不把它升级为新的人工项目需求。当前授权边界来自本次宿主交接和已固定任务，不来自advice。

### 冻结对象

基线HEAD为 `48db42643844bbb0b9f7ab5935676fdfb75d661f`；开始时仅详情文件被主控修改、builder尚未跟踪，未冒称工作树干净。已独立核对以下实际SHA-256：

| 对象 | SHA-256 |
| --- | --- |
| SYSTEM-99详情全文 | `21790201c4d95310f7da41955b52c3cef0a47a8cadea96c158e63d7c0d4d59e4` |
| `.agent-runs/system99/pilot-plan.json` | `012747491bc523cd11ef386997ffb88d74aede089e21e70aef5482b941ab449c` |
| `.agent-runs/system99/pilot-rubric.json` | `3413fe0ffe6067fa67e7392b8dc202f6d60df2bdda84824cf9be8bd346a0c542` |
| `build_pilot_i.py` | `bff4ae3dfd641c446ef0f5c6cb59ca27c3a2f01ccf77a2693a01ee19e3f6ade4` |
| `.agent-runs/system99/pilot-i/manifest.json` | `edb6aa3f4819e89a28e2e2bd7899621d081648844c1b437f7ad138e2d6627705` |
| native-1包 | `cb5f2e118a7a60632664a4b6c45167a0e354538775800aa15142b3eefbf1e915` |
| native-2包 | `d16371d81eb745cad3e6aefa3957a49bc6fda49e4bb419a7738f64c01520ee09` |

manifest实际位于运行目录，不在 `agent_doc/results/system99/pilot-i/`。其中5份source、3份prompt source及builder哈希全部与当前原字节一致。独立内存检查调用既有 `compose_entries`，未运行builder重写包：两包分别包含完整full/compact prompt一次，切除该prompt后header/suffix完全相同；将native-2中两处共享协议引用换回固定原协议，整个包与native-1逐字节等价。正文源码与问题未发生额外差异。

原始UTF-8解码长度分别114107、106165字符，字节数173627、153381；各含136处CRLF。首次用 `read_text()` 检查会归一化行尾，所得字符数/重新编码hash不等于原文件；复核使用 `read_bytes().decode()` 后与manifest全部一致。这是读取方式差异，未修改任何原文件。派发路径、输出路径和归属标识可不同，不能把这些不可避免的宿主投递差异归因于去重处理。

### 七域核对

| 域 | 判断 | 依据 |
| --- | --- | --- |
| intent | pass | 原生新上下文有限观察是现有离线字符/token证据之后的最小下一步；不替换用户目标、不推广目录迁移或删规则。 |
| guide | pass | guide目录只读、唯一TASK保持未完成；用户当前明确决定和实际宿主权限约束guide的项目规划权威，AI advice不是授权。 |
| assumptions | pass | 差异确为既有compose_entries的精确协议去重，额外源码/问题相同；模型精确版本和usage均unknown，不假定运行库已接入原生宿主。 |
| prior_results | pass | 已读实际resume-search及既有阶段H独审：查询scanned252、partial=true、81错误、6候选。旧comm/context/语料记录不能替代新模型回答；partial不证明历史穷尽，旧pass不授信。 |
| acceptance | pass | 固定rubric可逐条回指源码；主控需保留两份原答和真实读取事件，独审按源码/轨迹/原答打分。任何包外读取、写入、联网、rubric访问、额外代理/重试或硬事实错误即failure，不能以短回答补偿。 |
| risk | pass | 仅读指定资料，不执行项目或改源码/配置；依赖顺序为prepare→review→两臂→独立验收→报告；失败保留，不能静默重试或扩张结论。 |
| resources | pass | 固定两次调用、三题、约174/154KB本地文本是当前有限阅读任务的合理规模；不新增模型/GPU/服务。宿主未暴露精确context上限、精确模型版本、token/费用和硬成本计量，不声称已测得或保证这些值。若实际工具截断/上下文不完整，该臂失败或inconclusive，不通过重试补齐。 |

### rubric与题目效度

| 题 | 独立源码核对 | 评分解释 |
| --- | --- | --- |
| R1 | `Engine.tick` 在新唯一终态事件重验；`_check_done` 检查真实handler证据并沿已完成依赖闭包失效；终态分支将失效done转为blocked并设requires_reconciliation；`_summary`保留围栏；`reconcile`核查当前审核、非cancelled/blocked、授权、依赖、证据与host reference。 | rubric准确。应说终态路径把A及依赖B围栏化；不能把中间failed误报为最终持久状态。恢复文件/新tick不自动恢复done或重放；reconcile是逐节点的显式接受，不是重跑。 |
| R2 | `basis_context`从selected、required及所有candidate/rejected取并集，补声明祖先和必需basis refs，保留对应knowledge/memory/artifact引用与memory依赖；完整序列化超预算抛错。无真实callable counter时tokens=None，token硬限要求counter。`check_handoff_basis`/`claim_graph`验证声明结构；缓存说明仅指该consumer当前上下文。 | rubric准确。S/C/R及R的P不能仅剩S；这里保留的是声明闭包，不是自动发现隐含依赖、语义相关性或科学真伪。artifact payload主要为引用，不能声称自动全文装载所有artifact。 |
| R3 | AGENTS、project_document_workflow及三入口治理段均固定用户/宿主→已核实人工guide→AI advice的边界；整个guide目录人类专用。双主workflow证据等级和AGENTS明确CPU fixture/工作流不部署或认证真实宿主、多模型/tmux。 | rubric准确。取消、异议、权限和证据边界必须在减上下文时保留；guide来源须核实，不以文件名或自称批准授信。 |

三个问题均有明显提示：直接询问是否自动恢复/截断/字符代token/跨会话已读/AI改guide/部署，R2还指明candidate/rejected和父依赖。它们能检查被明确提示后的源码检索、事实陈述和限制保留，不能作为盲测能力、未提示召回或广泛质量指标。每臂仅一次且只有三题，样本少且问题相关；即使全过，也只报告这一对观测，不作统计非退化、因果收益或通用质量结论。包长差异只属已核实输入文本，不是真实模型usage或总成本。

本次默认Python环境没有tiktoken（实际import为ModuleNotFoundError）；未安装或联网补依赖，未把字符数冒充tokens。阶段H已有固定编码计数也不能当这两次调用的真实token/费用。

### 执行与验收边界

批准绑定上述固定材料和主控本次交接：原生调用必须 `fork_turns=none`，每臂只收到自己的一包，不收到本文、rubric、另一臂回答或历史答案；两臂投递指令除路径/归属等不可避免字段外保持相同。包中的治理/源码是分析对象，不能据其文字启动额外调查、代理、监督或包外文件读取。不得隐含继承本审查所读的历史材料。

验收将独立读取实际native agent ID、真实调用/读取事件、原始答案文件和当前冻结源码；生产者自报JSON/pass/摘要不能替代。需核对完整包是否实际进入上下文、可见截断、越界读取和所有新增事实；任一硬失败须保留原答并报告failure，无重试。若宿主不能提供真实轨迹，边界合规为inconclusive，不能自行给pass。不得将此文字审核冒充repository runtime认证、真实cost或多模型服务部署。

六项结果检查的适用方式在看答案前固定：implementation核实际源码/派发路径；reference_boundary按上述独立源码映射及硬边界；data_integrity核两臂完整包/哈希/原答/事件一一对应且无漏项；numerical_sanity只核三题分母与逐项布尔结论，不生成不存在的统计量；measurement_validity仅承认有提示单配对，计时/usage/费用不适用且无此主张；reproducibility核冻结包可重建和实际调用身份/条件，随机模型重现性未知且不额外重跑。正式结果仍须另节追加独立结论。

compact verdict：`decision=approve; checks={intent:pass,guide:pass,assumptions:pass,prior_results:pass,acceptance:pass,risk:pass,resources:pass}; blocking_findings=[]`。

## Result status

初审时pending：当时尚未收到两臂真实调用ID和原始答案。当前结果见文末“Version10独立结果验收”；完整provider轨迹仍不可得，不接受模型质量结论。

## 宿主证据缺口复审（Version9历史）

初审落盘后、任何worker派发前，主控明确通知：根工具目前只返回原生child ID与最终回答，没有可调用的provider完整逐工具transcript或usage接口。worker可按固定chunk范围读取原始字节、返回range/hash；根侧能独立验证这些范围/hash与包匹配，但这仍是可核对的读取自报，不是宿主认证的完整模型输入或所有工具读取轨迹。主控明确尚未派发workers。本次复审不伪造缺失回读，不把自报升级成实际轨迹证据。

这使原初审“完整真实读取事件将提供”的必要前提不成立。原文中的字节/源码/rubric检查仍有效，但原Plan9的“独立核对实际读取”与pilot-plan的禁止包外读取硬验收，不能仅由child ID、最终答案和range/hash自报认证通过。未观察到越界不等于已验证无越界；在缺完整证据时该项是unknown/inconclusive。故当前为revise，而不是勉强approve后再声称全项通过。

| 七域 | 当前状态 | 理由 |
| --- | --- | --- |
| intent | pass | 小范围代码理解初探仍合理，用户目标未变。 |
| guide | pass | 原人类目录/授权与唯一TASK边界保持。 |
| assumptions | unknown | 完整输入读取及包外读取可核查的原前提，真实宿主接口不能满足。 |
| prior_results | pass | 252扫描/partial/81错误及不复用理由仍成立。 |
| acceptance | fail | 现冻结硬验收要求实际读取核对；当前只能取得回答、调用身份和可核对自报。 |
| risk | pass | 尚未派发；透明版本化缩窄可避免把缺证据写成pass。 |
| resources | pass | 原两调用/一次无重试预算可保留；精确模型/usage/cost未知，未扩大资源。 |

完整finding：

- blocking：true。
- target：`agent_doc/task/task_details/SYSTEM-99.md` Plan9阶段I的“实际读取”表述，及 `.agent-runs/system99/pilot-plan.json` hard_acceptance / verify节点证据承诺。
- feedback：实际可得child ID/最终答复和worker读取范围/hash自报不能证明provider完整输入或无其它工具读取，不能满足现硬验收；这不是模型回答失败，而是证据能力缺口。
- requested_change：由唯一方案作者版本化缩窄为“收到两份原生回答/输入声明的代码理解pilot”；显式列出真实host可观察的ID、实际发送的派发指令、最终回答，与worker声明的range/hash；后者单列为self-report。保留所有事实rubric、一次/无重试、任何已观察越界或硬事实错即failure；完整输入与无越界认证保持unknown/open，不能把本次pilot判成旧全项验收通过。若不接受这个范围，保持当前未执行检查点。
- acceptance_check：独立复读新版本完整Plan/pilot-plan，确认不再承诺不存在的provider轨迹认证、不把absence-of-observed-violation写成verified-no-violation；输入字节/问题/rubric若保持不变可复用上述hash检查。只在新版审查后派发，不靠口头说明继续执行旧冻结计划。

最小透明观察办法：根侧保存真实spawn事件/child ID、完整派发消息原件和最终原答；worker按固定byte range逐块报告文件总字节、range、实际返回块的SHA-256及自身看到的截断情况，根侧逐一复算。这个办法只能提高输入声明的可核对性，不能认证provider实际把完整块交给模型，也不能穷尽其它工具调用。即使用独立只读reader写本地日志，也仅能证明该reader的本地读取操作，不能补齐provider全轨迹或其它工具读取；不建议为本次初探加架构来制造更强表象。

compact verdict（该次复审，现由下方Version10批准取代）：`decision=revise; checks={intent:pass,guide:pass,assumptions:unknown,prior_results:pass,acceptance:fail,risk:pass,resources:pass}; blocking_findings=[host-read-trace-unavailable]`。该时点无实验已执行，无原答分数。

## Version10复审（当前有效）

决定：**approve**。本轮重新完整读取当前Plan10稳定段与pilot-plan，独立逐行比较保存的v9原件，确认详情只改Version及阶段I段落；其它稳定要求未删改。未启动任何worker。

| 新审核对象 | SHA-256 |
| --- | --- |
| SYSTEM-99详情Plan10全文 | `c22fb192594507c15482a9ca623b298be8136f2a31a9ff38b8d246c1a9182c30` |
| pilot-plan Version10 | `1e9533991effe342cf1276b72396a5f7357f79aaaa9ab0e90d5669a90862f79d` |
| 保存的SYSTEM99-plan9-before-revise.md | `21790201c4d95310f7da41955b52c3cef0a47a8cadea96c158e63d7c0d4d59e4` |
| 保存的pilot-plan-v9.json | `012747491bc523cd11ef386997ffb88d74aede089e21e70aef5482b941ab449c` |

两包、manifest、hidden rubric及全部source/prompt source哈希重新核对未变，沿用前文精确差异和逐条源码检查。新版明确只接受原生child ID、实际派发消息、完整原答及可核对的range/hash自报；provider完整摄入、全工具轨迹、无包外读取认证、精确模型版本、usage/费用均unknown。硬事实/限制rubric未看结果后放松；发现越界仍failure，未见越界不能写成已认证合规。原阻塞finding通过版本化缩窄结论关闭，未谎称缺失接口已补齐。

| 七域 | 判断 | 新版依据 |
| --- | --- | --- |
| intent | pass | 做两份有提示源码题回答的有限观察；完整任务质量、部署和跨会话能力仍open。 |
| guide | pass | 当前明确交接、宿主权限与人类目录只读边界不变；不改唯一TASK完成状态。 |
| assumptions | pass | 已把不可得证据移出本次认证范围并逐项声明unknown；不再以worker读取自报证明provider完整输入。 |
| prior_results | pass | 先前实际查询及不复用理由保留；旧comm/context与离线计数不充当新模型回答。 |
| acceptance | pass | 独审真实ID/派发原件/回答、逐条源码事实与限制、自报hash/range；明确区分可见原生事件、可核对自报与未认证事项。 |
| risk | pass | 单次无重试、禁止写/联网/包外读取/额外代理；已知违规失败、未知保持未知，不以结论范围缩窄掩盖违规。 |
| resources | pass | 固定两新上下文、每臂完整原包与三题、同一默认请求设置；不增加调用/GPU/服务，未计量模型版本/usage/cost不报实测。 |

派发只在这个新版批准后进行，使用 `fork_turns=none`；每臂只给自己的一包、相同任务指令和必要路径/归属差异，不给rubric/本文/历史答案/另一臂内容。实际派发指令原件须保留，不能仅保存事后摘要。原始回答由根侧完整保存，worker的JSON/读取声明本身不是pass。完整回答缺失、明显截断或范围/hash不符都必须记录，不能重试或用新会话替换。

结果报告可在独立评分通过后写“本次两份回答在固定rubric下逐项满足”；不得写“完整输入已认证”“已验证无包外读取”“统计非退化”“一般质量保持/提升”或真实成本下降。若实际证据只支持一个子集，应逐项标注，不能把unknown统合为全项通过。

compact verdict（当前有效）：`decision=approve; plan_version=10; checks={intent:pass,guide:pass,assumptions:pass,prior_results:pass,acceptance:pass,risk:pass,resources:pass}; blocking_findings=[]`。这不是运行时认证回执、用户新权限或结果验收；实际结果仍pending。

## Version10独立结果验收

结论：**usable-with-scope，仅限固定资料与转存回答的核对、逐题评分及异常/负结果记录**。两臂全项rubric门槛未通过：arm1三题通过，arm2的R2有必需限制缺项，按冻结规则该题失败。配对质量比较为 **inconclusive**：arm1首次合并工具输出截断，随后同会话重复补读，实际暴露条件已不同；不能从这些回答推断去重保持或提升质量。任何质量/费用收益消费继续blocked。未补答、未启动新AI或独立模型重跑，未修改原答案或rubric。

### 实际对象与证据来源

主控通过本次真实交接提供原生工具返回的canonical task name `/root/pilot_i_arm1`、`/root/pilot_i_arm2`、一次各会话且无新会话/重答；保存的dispatch事件和消息对应这两个ID，`fork_turns`均为none。独立读取两份dispatch，除指定native-1/native-2路径外消息逐字相同，未把路径/归属差异视为去重效果。根侧可见原始final消息，`responses-i.json`是其中JSON值的完整转存和重新缩进，**不是provider字节原件**；本审核者读取转存值，没有provider完整transcript可独立比对。主控来源说明与这个能力边界一致，不能把保存的JSON文件本身当成宿主认证凭据。

独立逐字段比较公开 `inputs-i.json` 与当前运行区原件：manifest、dispatch1、dispatch2、events、Plan10和rubric六组对象全部相等。Plan10、两包、manifest、全部source/prompt source哈希与批准时一致；问题没有看结果后改写。原答arm1/arm2各恰有R1/R2/R3一次，无漏题或重复题。该结论针对当前保存对象的完整性，不冒称独立核实了provider原消息字节。

| 新证据 | 实际SHA-256 |
| --- | --- |
| `inputs-i.json` | `425d56826f48858918679b1d9faa0c3ed79db3f970a2d90c793904bd26cb1ca3` |
| `responses-i.json` | `0e802176d62a3dafdc144006c453d86b24ac682aef70c0454ed66be7218f771c` |
| dispatch-1.json | `ad1d84b878d536cba602bc8d910175493bb6e6043c3f9a08b551ed9c2a7161e8` |
| dispatch-2.json | `079459d4e87a218c05f73f6e103f52587948f896cf0a61fdf70a60f8c04003af` |
| dispatch-events.json | `9c133eaeab8bac3ba50a8d5c8ae1176c5c332135ee82d6d8d4bf7dde5606f9d0` |

### 冻结rubric逐项验收

再次直接读取实际 `core.py` 的tick/_check_done/_summary/reconcile/cancel路径，`handoff_basis.py`的basis_context/check_handoff_basis/claim_graph以及治理源段；没有依赖生产者pass或仅看JSON格式。下表中题号后序号即冻结rubric数组顺序，非新增判据。

| 评分项 | arm1 | arm2 | 独立源码依据与答案核对 |
| --- | --- | --- | --- |
| R1.1 新唯一终态tick重验及依赖闭包 | pass | pass | tick记录新event后调用_check_done；两答均正确覆盖A→B。 |
| R1.2 持久blocked/reconciliation围栏 | pass | pass | tick终态分支转failed为blocked并设requires_reconciliation；两答最终状态正确。 |
| R1.3 恢复字节/新tick不自动接受或重放 | pass | pass | _summary保留围栏、非todo不可claim；两答均明确。 |
| R1.4 显式reconcile当前审核/授权/依赖/证据/reference | pass | pass | reconcile逐项检查，A先于B；两答必需条件均有。 |
| R1.5 cancelled不可reconcile | pass | pass | reconcile拒cancelled，tick取消快路返回；两答均明确。 |
| R2.1 selected/required/candidate/rejected均保留 | pass | pass | basis_context集合并集；两答均列S/C/R及required。 |
| R2.2 声明祖先与必需依据引用 | pass | pass | included递归祖先，kids/mids/aids消费者引用并集及闭包；两答均列P和必需依据。 |
| R2.3 超预算失败而非截断 | pass | pass | 序列化后_require检查；两答均明确。 |
| R2.4 无实际counter时token未知，字符不冒充token | pass | pass | tokens=None、token硬限要求callable；两答均正确。 |
| R2.5 当前consumer缓存提示不证明跨会话已读 | pass | pass | basis_context注释和freshness检查；两答均明确。 |
| R2.6 声明闭包不证明语义相关性/不发现隐藏依赖 | pass | **fail：缺项** | arm1限制明确“只跟踪已声明依赖；不验证…语义相关性”。arm2限制只说“只覆盖声明的身份、引用、依赖及前提记录，不证明科学适用性”，可覆盖声明范围/不自动发现隐藏依赖，但没有明确保留`selection.scope`的“semantic relevance unchecked”。科学适用性与语义相关性不是同一限制，不能自动互换补足。 |
| R3.1 当前用户/宿主约束guide权威 | pass | pass | 两答均明确这些边界优先。 |
| R3.2 已核实人工guide优于AI advice，后者非授权 | pass | pass | 两答均明确；project_document_workflow也要求adopt/adapt guide_alignment兼容。 |
| R3.3 整个人类guide目录不可AI编辑 | pass | pass | 两答均明确；arm1补充只可mkdir空目录与源一致。 |
| R3.4 减上下文保留取消/异议/权限/依据边界 | pass | pass | R3均保留取消/异议/权限，且说明candidate/rejected/依赖与依据保留；两份完整答复的R2同时明确必需依据/缓存新鲜性，不声称可裁掉证据。 |
| R3.5 工作流/CPU测试不部署认证真实host/多模型/tmux | pass | pass | 两答均区分真实调用/ID/readback与仓库说明，未虚构部署。 |

题级规则是全部必需项通过才算该题通过：arm1为3/3；arm2为2/3，R2失败。共16项/臂，arm2最后缺项为限制遗漏，不是已发现的源码事实反向陈述。未发现其它硬事实错误；所引Engine/handoff函数真实存在且调用关系匹配。arm1引用MemoryLedger/check_handoff_knowledge仅对应包内可见调用点，并明确依赖实现未包含；本验收未把这些引用扩展成对包外实现的验证。R3文档标题作为source_functions/source_documents引用与源内容匹配，不把文档名误当可调用函数。

这些数值是固定清单计数，不是独立样本准确率或任何统计检验。R2缺项不补答、不改判据，也不能由其它正确项或更短输出抵消。

### 读取声明、截断与额外暴露

独立按原始bytes UTF-8解码复算全部范围与片段hash，保留CRLF：

| 臂 | 范围/hash声明核对 | 可见异常及解释 |
| --- | --- | --- |
| arm1 | 原文件173627 bytes/114107字符与raw hash匹配；10个补读字符半开区间连续覆盖[0,114107)，每块≤12000字符，10/10片段UTF-8 SHA匹配。 | 自报首次合并输出被截断（原token计数43688、外层26027），随后同会话逐块补齐并自报无可见截断。初次截断还由主控本次交接确认；不能把补读声明变成provider完整摄入认证。 |
| arm2 | 原文件153381 bytes/106165字符与raw hash匹配；9个字符半开区间连续覆盖[0,106165)，每块≤12000字符，9/9片段UTF-8 SHA匹配。 | 自报无可见截断；这是自报与文件范围/hash匹配，不是全工具或provider输入认证。 |

range是字符范围；arm2另列bytes_read=[0,153381]，两者单位未混用。没有把全文件hash或片段hash相等当成模型读完的证据。

arm1同会话补读不是新的native会话或第二份最终回答，但确实包含额外重复读取/暴露，不能抹去初次截断、也不能当作与arm2同样的一遍完整输入。原初审已明确工具截断/输入不完整不能靠补读自动取得该臂完整输入认证，本验收保留该项inconclusive。已保存材料未披露包外读/写/联网/额外代理；由于完整工具轨迹不可得，**无包外读取合规仍unknown**，不作“已证明没有违规”的pass。没有发现可据现证据确认的包外硬违规；若以后出现真实证据，相关验收必须失效并保留失败。

### 六项独立结果检查

| 检查 | 当前可消费范围的判定 | 实际证据与范围 |
| --- | --- | --- |
| implementation | pass | 阅读builder、compose_entries及真正被问的源码/治理实现；仅共享协议精确替换、来源哈希未变。评分逐项对照实际代码，非执行模型自评。 |
| reference_boundary | pass（含已记录负项） | 独立函数/治理映射作为参考；已识别并保留R2.6遗漏，未把声明结构验证升级为语义验证。 |
| data_integrity | pass于转存资料/自报核对 | 公开inputs六组对象与运行区逐字段相等，两原答各3题，19块连续/完整范围/hash全匹配；provider原消息字节/完整输入不可独立认证，不在pass范围。 |
| numerical_sanity | pass | 字节/字符单位分开、原hash/19块hash核算，题目分母3/臂、条目16/臂与冻结rubric一致；无NaN/Inf或虚构统计量。 |
| measurement_validity | pass仅于描述性观察；公平质量对照inconclusive | 有提示单配对、arm1截断与重复补读，不能比较处理效果/非退化。计时、真实usage/cache/费用未测，未作相关结论。 |
| reproducibility | pass于静态重建/核对；随机回答重现未知 | 固定包/源码/派发消息可核、JSON对象对应；不额外调用模型，不声称相同模型采样可重现。精确版本、采样参数和provider轨迹未知。 |

主控另提供 `.agent-runs/system99/pilot-i/prompt-tests.log`，SHA `86d972185ec4aadb66346ab673ca9a60728ca74e1099592c68a3edcae3755b9c`。实际读到14项CPU单测通过；本角色没有重复跑全库或用这些测试证明模型质量、真实usage或宿主部署。初次尝试读取上级目录同名log不存在，随后按实际pilot-i路径读取，不伪称缺失路径有日志。

### 论文记录G的有限核对

独立核对本地PDF SHA `8b4b6fecdf48207c3476c701b7f6da93e92409fae62f78f6466c9e5ae52a9606`、29页元数据、相应原文段落及已渲染p15原页图（SHA `be93ad1ae9d7e1db585115a77863385c38336304bd594aa099f02ce36b7d703f`）。记录G所列427=345+50+32、BCY regex tokenizer/top20前缀下界、45例每样本臂单轨迹、表16 RRF 0.3967/无seed0.3222/随机0.3437、seed与post-seed成本分列和不能推断patch成功等均与原文一致。p15明确small differences不构成统计解决的排名、工具无edit/patch/test；这些边界适用于限制外推，不是本库收益证据。

`research-g.md` SHA `a8cb3ff6f5bad719885c31621e54e8b0458996acccbeeab5b486130b3e9c981d`。本审核者没有重新逐页全文阅读该29页或作者数据复现实验；“§1–13及附录A–E已读”及累计15篇是生产者当前未结束批次的正文记录，不冒充本角色新完成15篇独立精读或本批次已结束。

### 可消费范围与阻塞项

允许消费：上述固定文件/字段/hash核对、两份回答按冻结rubric的3/3与2/3题级结果、明确的R2限制遗漏、arm1截断和重复补读、自报范围/hash匹配，以及这些观测为何不能支持公平质量比较。负结果合法保留，不要求修补成pass。

不得消费：两臂全项成功、去重导致R2遗漏或其它因果判断、等价/非退化/质量提升、模型真实token/cache/费用下降、完整输入/全工具/无越界认证、repository runtime或真实多模型/tmux部署、SYSTEM-99整批完成。上述主张blocked或unknown；本次不重试、不补答、不换身份消除失败。继续任何新实验须新版本与原授权边界内独审，原失败/转存原答不可覆盖。
