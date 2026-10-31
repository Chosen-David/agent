# Jev-LiteMAS v2：有条件复审的成本与漏放边界

精确版本2610.21411v2，*Jev-LiteMAS: Separating Decisions from Generation in Multi-Agent Workflows*，Kaixiang Wang / Zhaijiacheng Zhou（HTML署名Zhaojiacheng）/ Jiong Lou / Jie Li；arXiv v1=2026-10-15，v2=2026-10-16，URL https://arxiv.org/html/2610.21411v2 。HTML仍含ACM2018/Woodstock/DOIXXXX模板，不能当真实发表会议或日期。实际新读完整正文71993 Unicode字符，主文1–6/全部子节、References、App A/B.1–B.2/C.1–C.3/D、五表、三图图注、Eq1–15及Algorithm1。未看PDF像素或图内额外数字，不运行作者代码/模型/benchmark，不以摘要、检索或旧读记抵数。

## 方法：不能用选择标签冒充交接说明和修复反馈（§§3–4、Alg1）

专家生成y_t并把实际artifact与角色纳入state；Jev只在host给的legal expert+可选STOP中选一动作。被选专家以原任务、可用前作、反馈和本身role instructions继续；不预生成整条trajectory，并不意味着没有合法动作/role/config/上下文约束。普通handoff用最新实质内容，而不是只看谁运行过。全文未具体给出截断/恢复/依赖闭包合同，不能由“shared state”推出更正/异议无遗漏。

配置review point后先二值screen；pass释放本artifact，escalate才由generative reviewer独立重看同task/artifact/criteria，可能accept也可能给反馈。repair由expert执行，revision作为新artifact重入筛查，重复review/repair仍耗budget。局部pass≠STOP≠终局验收，Alg1预算尽走HandleBudgetExhaustion，非Finalize；伪代码未细定义该函数/执行原子性/外部效果fencing。

Eq12实测escalations含修后重复检查；Eq13 rho=pi*r+(1-pi)*f，pi是自然trace中需更正artifact占比、r检出率、f误升级率。固定每callcost简化Eq14 CJ+rho*CL，仅CJ<(1-rho)*CL时review stage省；全流程还要routing/expert/repair/重复check。Eq15漏放pi*(1-r)，漏放不进LLM复审，因此不能说“有fallback便必然安全”。注入集class比例不估计自然pi，低FPR也不说明高TPR。

## 实验协议、口径与主结果（§5.1–5.2、Table1、C.3）

AutoGen上固定专家pool，DeepSeek-V4-Flash或GPT-5作生成骨干、Jev决策，Qwen3-1.7B-Instruct作SLM对照。MATH/MBPP+/I3各seed42分层抽150任务；API-Bank150episodes含445预测点。MATH数学等价、MBPP+ EvalPlus base+extended全过的pass@1、API严格API名/参数/执行结果、I3 integrable二值groundtruth，invalid错；I3不是生成科学Idea的开放质量评测。API ACC分母445points，而tokens/latency/calls按150episodes，不相除当每正确point成本。

tokens来自provider input/output usage，聚合所有对应**generative LLM**调用；Calls亦只生成API，不含Jev/SLM tokens，不是全部模型总量。主文另估Jev延迟/价费，但未足够公开证明当前服务版本、cache/uncached完整收费分类/精确价表或全基础设施费用。C.3提供采样/评分/核算，未具体列专家rolepool/完整prompts/reviewpoint频次、默认budget/reasoning/temperature/每task重复种子与CI；不能冒称全细节可复现或统计非劣。

相对LAS，DeepSeek四任务：ACC ours/LAS=97.33/98.00、85.33/84.67、66.29/66.52、75.33/76.00；generative totals5433.2/6583、6903.5/8719、9869.3/16293、10233.8/22556，作者−17.5%到−54.6%；四项wall都少。GPT5 totals5990/7663、7542/8636、10074/16393、15626/25440，作者−12.7%到−38.6%；ACC差0/−1.34/−0.90/+0.67pp。GPT5 MATH反而30.04s vs25.91s（慢约15.9%），仅7/8更快；非所有任务质量提高，MetaGPT DeepSeek I3=82.67高于75.33且成本高。点估计差within1.34pp不是CI/预设非劣gate或同质量证明。

§1 profiling三MAS×MATH/MBPP+六设置：routing+review31.7–43.5%生成tokens，29.5–46.1%记录latency；LAS两任务40.4/39.2%tokens。是作者指定部署，不是本库主控/子agent成本。§5.5 GPT5下Jev1.13–2.21s，E2E占2.92–6.85%；所用价费估算占1.56–2.14%，总$0.00664–.01766/unit。仅读图注/正文数字，不补造每bar数据，不能外推实时价格。

## 消融、错误注入与负结果（§§5.3–5.6、Tables2–5、B）

组织对照Static/Heuristic/Planner-Replan，Jev I3/API=75.33/66.29最高；Heuristic58.67/64.27虽更省token更快，质量退化；Planner-Replan48.00/53.93且tokens最高。换router比较LLM、SLM、Rule，选择能力/执行路径/调用数一起变，不是纯模型速度实验。Content-Blind仅router屏蔽实质expert/tool内容，保留任务/legal actions/executionmetadata/interexpert通信，执行专家上下文不据此全清空。I3 75.33→57.33（−18pp），API66.29→57.30（−8.99pp，§1文字9.02与表不一致）；call2.47vs2.46、4.00vs4.13近似。支持实质反馈重要，不能说全局无损压缩/只靠摘要足够。

随机专家artifact注入task相关错误，非所有真实/恶意失败类型。Table3 Attack-MAS ACC46.67/39.33；cascade94.00/84.67，ASR3.33/4.00；MAD98.00/85.33、ASR0/1.33更好且昂贵。Jev–LLM94.67/84.00 vs cascade94/84.67，tokens10138/12430 vs8657/9736（少14.6/21.7%），wall45.14/76.32 vs34.19/58.35。Table4 clean Jev FPR4/6.67 > LLM1.33/5.33，attackTPR95.33/91.33 < LLM96.67/92；SLM FPR0/.67更低却TPR61.33/44.67差。保留MATH4.67%、MBPP+8.67%漏检与实际终局风险，不能拿typed输出充当正确性认证。ASR分母/注入器具体完整参数未在C.3详细说明，不补算成仅clean-success样本的条件率。

B.1生成call上限2/3/4/6：I3 ACC46.67/62.67/70/73.33，实际calls2/2.26/2.48/2.64；API56.18/57.08/64.72/65.84，calls2/2.93/3.96/4.46。更多上限不等实际耗尽，API tokens10.713/12.040/14.553/12.817K和wall16.12/20.63/18.34/20.16不单调。主表I375.33不同于B=6 73.33，不能猜默认上限/把两组当同配置重复统计。B.2 AAA→ABB→ABA I3质量75.33→76.67→78、token10.233→11.387→14.536K；API66.29→66.07→64.49反降，token9.869→12.924→13.518K上升。双骨干不普遍提高质量或节费。

## 局限、本库对应与采用决定

作者App A：预置pool不能新建/重配未知专家，低质量artifact比例高会增复审/修复成本。另有单采样seed、无跨重试CI、注入错误覆盖、未完整all-model账目、API粒度差异和上下文/迁移/恢复未定义限制；不把相同generative budget视为等总费用。未复现实验，全部作者数字只属该论文设置。

本库固定b18acdce实际静态阅读：Mailbox publish/publish_many定向routes、run/inputversion、ACKimmutable且非接受；consume_handoff重读manifest和原refs/consumer basis，impact返回受影响recipient，不自动ACK/更正执行；prepare_context使用既有basis_context。handoff_basis.check_handoff_basis只核identity/dependency/premise而非science acceptance，consumer-required memory/claim在主控侧，不能由screen替代。Engine.tick前后核plan review、租约/token/current/cancel，非幂等过期留ambiguous；这不证明宿主外部副作用已fenced。dispatch_context按显式完整性决定start/fork并保留write_scope/requiredrefs，不把共享history变成新pool。此次仅相关函数范围/代码hash核对，无并发执行/全链模型实验，未确认新生产缺陷，不称整个模块无bug。

adopt：后续profiling按操作区分机械合法性/路由/语义反馈/修复，保留实际artifact和更正/异议/依赖，分列provider实际input/output/cache/uncached、所有角色/decision calls/全费用与终局质量；允许无信息增量不扩advice。复用现有唯一TASK/MemoryLedger/定向交接，无新增重复prompt。defer替换主控/必需独审、引入Jev端点/廉价screen放行、自动routing/架构迁移；论文门禁不能授权放宽本库mandatory结果验收/身份认证/预算，更不能因typed verdict关闭真实宿主缺口。当前不可进行旧后端/旧模型试探或额度重置，缺全链真实输入/质量证据，不报性能提升。

补充官方网页仅2026-10-31读取intro：typed state问题可返回choice/score及概率/置信、另0–1 truth primitive，建议原子判断并由代码组合；产品说明不等同正确/校准/性能实测，更不固定paper使用的Jev版本。未调用API/配置key/安装服务；HTML未发现作者GitHub实验release链接，不把arXiv的LaTeXML反馈链接当作者代码。

既有结果查询378scan/partial=true/25errors，Jev/CAVERT的词法候选未验成等条件实证，不复用性能。DiscernMem2610.36652v1检索命中同批discernmem-reading-20261029，尽管重新下载HTML，未再计精读/独审或改旧记录。当前Jev正文读完但独立复核pending，0新增credit至接受/普通发布回读；历史66不重新认证，三旧包六缺原件保持，SYSTEM99继续open。
