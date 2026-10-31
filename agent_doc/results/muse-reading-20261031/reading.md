# MUSE 正文精读：条件化经验、选择注入与未验证的持续累积

2610.38332v1，*MUSE: Multi-Level Memory with Selective Runtime Injection for Scientific Coding Agents*，Haoran Jin / Defu Lian / Xiting Wang / Hong Xie，arXiv版本日期2026-10-28；HTML固定 https://arxiv.org/html/2610.38332v1 。第三方更新时间不证明v2。实际读取本地精确HTML/text正文，不以abstract或旧读记抵数。

正文63045 Unicode字符已连续阅读：[0,6500)、[6500,14500)、[14500,22500)、[22500,30500)、[30500,38500)、[38500,46500)、[46500,54500)、[54500,63045)。最初试图输出0:13000被宿主截断，不计；之后明确从0重新读取上述段。覆盖主文1–5及所有子节、Limitations、全部References、Appendix A.1–A.3/B.1–B.6、Tables1–6、Eq1–6、Figures1–8图注和全部六prompt/schema。未查看PDF像素/图中额外曲线，不运行作者代码/模型/工具、无实验复现。public旧6500字符检查点只是过去partial0credit，不追改成当时全文。

## 方法及关键机制（§§3.1–3.4、Appendix B）

每源尝试冻结task、可见trajectory、最终逐字submission与evaluation。提取L1实际总体route与L2重要implementation decisions，区分observed、derived_from_contract、proposed_unverified；失败位置不直接等同root cause，正确但未加速不当成正确性失败，失败修法不当成已验证成功。源材料b_i含problem/submission/feedback，与检索lesson一起供检查，而非只给总结。

L0 GlobalMemBank由提取内容和原始证据逐源add/replace/retire，再全库audit；保留条件/公式/操作/理由，不因为缩短删除必要细节。unchanged由程序原字节保留，操作有内部source_refs/basis/stable ID。Appendix B.2只给advisory 80000 model tokens“matching comparison knowledge budget”，没有证明实际各方法输入/全费用相等。完整L0给每个目标，不是按需L0，也不是额外共享聊天池；L1/L2在L0整合时不改，评测前所有bank/index冻结。

初始化完整L0+问题相似Top5 L1，每项附源记录；qkey去公共环境指令，embedding单位向量cosine（Eq2）。初始5个source ID在runtime所有索引预排除，避免与已给reference重复。

工具如Write/Bash返回后取assistant body / tool args / tool output四路Top1：body→L2；args→historical submission和L2；output→historical errors。L2 key只含decision与choice/rationale。相同source合并，只有submission/error hit时可无L2 lesson；随后排除以前已runtime注入source，**不补检索**，最多四个候选（Eq3）。不是任意topk新记忆保证、不是给主agent全部候选。未选source仍可之后被取到，已注入source永久在本trajectory排除；冻结库试验没有处理其更新后的更正传播。

无工具gate看task summary、之前public trajectory、当前interaction与候选，选0或1个source并写具体review note（Eq4–5）。指出当前operation/assumption/result和该查什么；直接可见缺陷与待查风险分开，提过/写过不等于验证过，也不授予任务禁止的工具权限。无可操作提醒则空selection/空note，空选择不改context。note最多100words且1200chars，JSON maxItems1；选中的整个候选记录与note一起注入，source加入去重集。note界限不是整个注入/整回合输入/调用次数上限；gate逐次看public history的开销未报告。

## 实验、指标与主要结果（§4.1–4.2、Tables2–3、Eq6、A）

约30%随机任务做memory source，每个仅一次无memory rollout，所有方法共用这些trajectory，bank冻住再测其余任务：PDE194/451、KBX53/122、KGB63/140、SWE Science35/84（extraction/test）。独立任务切分不保证跨任务无近重复，也未提供该重复审计；不能据随机split称无一切污染。

共同ZCode/GLM-5.3-flash high reasoning同时用于solving/construction/gate，10baselines+MUSE共享source/tool permissions。PDE允许Bash/local probes，kernel禁candidate自测，software依benchmark frozen workflow；hidden评估事后，不返agent。模型卡320Btotal/18Bactive是作者引provider，不是我们核验。Qwen3-Embedding-8B/4096float32cosine，无client instruction prefix/不chunk/truncate runtime query；不表示embedding服务无限输入。max_tokens128000为task/gate每响应，非总输入/总tokens；wall limits2hPDE/4hkernel/3hsoftware。

Correct=sum(correct)/所有测试任务。Accel=sum(correct * valid_timing * [reference/candidate>=1.01])/所有测试任务，非仅正确任务的速度平均。reference/candidate同GPU/同lock，失败timeout按失败；阈值只减轻近1.0timing波动，不是统计显著性保证。双EPYC7742共128物理cores、8×A100-SXM4-40GB，单kernel评估占一GPU，推理hosted API。约$1500包括preliminary/construction/evaluation，未分method/role/成功任务、无tokens/latency分布，不能据此计算MUSE相对全费用。

Table3按PDE Pass、KBX Correct/Accel、KGB Correct/Accel、SWE Pass：Vanilla44.8/57.4/31.1/44.3/8.6/29.8；MUSE92.2/79.5/44.3/66.4/24.3/40.5。各metric最强baseline依次Evo87.8、ACE66.4/36.9、RAG57.9、ReMe20.0/35.7；MUSE相对各最强+4.4/+13.1/+7.4/+8.5/+4.3/+4.8pp。主表显示六项最大点估计；论文没有这些差异的CI/paired significance、重复seed均值或全费用匹配，不能说所有差异显著或得到普遍可靠性保证。科学memory baseline是共享agent中模块移植，不代表原完整系统比较。

## 消融、负边界与案例（§§4.3–4.5、Tables4–6）

PDE累计L0=82.7、L0+L1=89.4、full92.2，相邻+6.7/+2.8pp；L0低于Evo87.8，L0+L1才超过。累计不是全factorial，不能唯一分离L1/L2单独效果/相互作用。§4.3文字把451 PDE的表号写Table5，实为Table4，保留原文交叉引用错位而不把KGB140说成451。

No-gate仍三层/四路/source排除，但每trigger直接注入相似度最高eligible source，去掉gate**选择与review note组合**；full vs no-gate PDE92.2vs90.7、KBX79.5vs66.4/44.3vs37.7、KGB66.4vs62.1/24.3vs20.0、SWE40.5vs32.1。不能把收益只归因“允许skip”、只归因note或同等调用预算；未见gate-only/no-note、固定次数随机选择、等费用控制和注入频次/skip率。

KBX→KGB相同140targets：Vanilla44.3/8.6，L0transfer53.6/15.7，L0+L1 54.3/23.6，full62.1/25.0；in-domain KGBfull66.4/24.3。迁移full相对in-domain正确−4.3pp、Accel+0.7pp，不能笼统全面同好或证明统计等价。L1对Accel增幅较大、L2对Correct较大只是此累计对照。ACEtransfer50.0/22.1 vs其in-domain50.7/17.9；跨域方向仅KBX→KGB，同kernel领域，不外推其他领域/大规模持续更新。

三选例：L0半精度先upcast使logaddexp2编译通过1.048×；L1首位FP8 source中有用E4M3编码route与其失败native cast不同，target 1.0→0x38而Vanilla0x01，32test全过1.380×vs0；L2 variance两pass source初始问题rank13不在Top5，写代码后检索/复核使target改为平方偏差，source1.818×、target1.884×。这是作者挑选轨迹的机制解释，不是独立局部消融、通用数值稳定性证明或本库kernel收益。

## 局限及本库关系

作者Limitations承认单backbone/interface，4bench、单迁移方向，**不测continual memory updates**；conflict resolution/retirement随环境变化是future work。全库audit提示词不等于运行时证明，80k advisory与“fullL0每task”可能带来很高上下文/缓存/构造/gate成本，需要实际provider usage。无连续纠错、并发ownership、任务依赖闭包或reader遗漏检测证据；论文不提供满足本库这些合同的替代。

本库静态对应固定4468f3f4（源模块与f88相同）：`MemoryLedger.correct/_revise`保留superseded历史并将descendants stale，document-bound correction要新snapshot；`_context_closure/check`做依赖/文档门禁。`MemoryLedger.index`全选定snapshot hash/分页cursor只导航，明确仍全DB read，不能以省wire说省读取或有效性。`task_context.task_view`保留所有非任务行/全局约束，显式SHA/未知ID拒绝；`advice_context`按真实H2导航/原SHA，选段保留leading text/超限拒绝，不证明全局closure。不能用MUSE source去重替换这些更正和依赖门禁，更不能建新root TASK/shared pool。

adopt评价问题：每次建议必须关联具体当前操作与适用条件，区分实测/语义推导/未验证修法，允许无信息增量时不追加advice。已有合同具有相应边界，当前无确认缺陷，不追加重复长prompt/机械删注释。defer L0全量加载、四路embedding、新LLMgate/自动退休及架构迁移；缺真实宿主provider全输入/全角色cost与同条件最终质量，不实施或称提速。之后若提出改造，复用唯一TASK/MemoryLedger/定向交接，做完整读取对照任务包/活跃view的更正/异议/依赖遗漏和实际quality/uncached/cache/调用/构造恢复费用；先对齐版本方案，不能凭此论文静默迁移。

prior查询377扫描、partial=true/25errors，六词法candidate含combined-corpus-delta、math-risk、memory-pack及advice-context/link，均未在本次核验成等环境实证，不复用其收益，也不称穷尽无旧结果。无生产/test/workflow修改、作者实验/模型复现或性能结论。全文已读，独立复核尚待；不计完成阅读，旧历史65不被本记录重新认证，SYSTEM99继续open。

作者GitHub补充只读：hr-jin/MUSE固定524ddcd70fa5412e24601fa69d367fab2838170c之完整README已读，返回字节重算Git blob 4efc5826051b906c876c54dea9e4d8310f45f91a与该commit tree一致。README明确release提供construction/retrieval/gate prompts/schema，benchmark/verifier/agent runtime从upstream另装，输入trajectories由用户提供，synthetic/fake-model tests不调模型/benchmark。runtime可处理既有interactions保存delivered.json，也提供live callback，但不是本库已接入；默认Top5至少5sources、额外embedding/chat endpoints未知可用。未执行安装/测试/API、不据README宣称paper-v1全部实验可回放；commit日期早于paper提交且release与paper实验精确对应未另核。
