# Trust Layer：评分、来源、完成声明与重复可靠性

2610.07274v1，*A Trust Layer for Agent Evaluation*；Mohammadreza Sediqin、Shivali Dalmia、Srinivasa Karthikeya Reddy Kovvuri、Abhishek Mukherji。实际版本于2026-10-05 19:15:37 UTC提交。[正文](https://arxiv.org/html/2610.07274v1) · [版本](https://arxiv.org/abs/2610.07274)。同一SYSTEM-99 / Plan54继续未完成，本记录不是本库性能或整轮验收。

## 实际阅读范围

0200检查点读至§3.5计数规则中段；0300续读余下正文§§3.5–5/Limitations及附录A–F，合计Tables1–14/Figure1图注。精确规范化字符区间与源SHA见inputs.json；参考文献和HTML页脚不充正文。未看PDF/渲染图、作者代码、逐题轨迹或原始grader，未复现模型、judge、重评或统计实验。v1写明代码待接受后发布，不把搜索结果中的仓库线索当已检查实现。两次读取合计同一篇，独立复核和公开回读后可恢复记录32→33，不抵未来新批次。

## 方法与决策边界（§3，A）

四维是原评分旁的附加审计，不改原分数、不加权互相抵消。D1–D3使用保存轨迹、输出及可访问grader；其中有judge调用，不能当零模型成本。D4另跑agent。确定性决策规则依赖模型标签，并不消除标签错误；三票同意也不是事实认证。

| 维度 | 实际机制 | 不能推出什么 |
|---|---|---|
| D1 competence | 扫全部grader文件恢复gate，三票标critical/process/administrative与anti-gaming；离线重跑grader并匹配失败gate。regex抽terminal成功声明，对重评分形成已证失败/不可验证/无确认假声明；再按固定规则confirm/contradiction/upgrade/unverified。 | partial未达完整pass阈值多为定义差，不等于grader错；无法重评保持unknown。gate类型在该grader上复用，不保证跨新版本有效。 |
| D2 value provenance | 用agent未见的reference在离线选答案值，再查executed output、given input、手工typed及ungrounded。标量逐值、大数组/表按文件来源；歧义送judge判断任务是否要求计算，三票严格多数才判gamed，允许直接回答则清除。 | 无trace先路由，不自动判作弊；confession须配合来源缺口且排除否定表达。执行代码写出伪造常量/文件可逃过检测，因此derived不是数值正确、工作真实或意图证明。 |
| D3 completion claims | 按D1重评分而非原score判断成功声明是否被失败反驳；无法重评是suspected。第二阶段judge再确认/撤销及标严重程度，不反馈D1或改score。 | operational“lie”只说明报告不实，不证明agent知道不实。D3依赖D1，不能当两份独立证据。无已确认假声明不等于已证成功。 |
| D4 reliability | 相同配置五次重跑，排除被分类为infrastructure的run，对存活重复是否跨ALE pass/partial/fail分档判stable/varied；均值与原score差另报，不作gate。 | stable可能全部失败，或稳定在不同于原score的档位；不等于重现原成功。五次样本不保证未来，排除基础设施后是条件可靠性，不代表完整harness可靠性。 |

行政upgrade只有decisive gate确为administrative、prompt未要求该格式、值与reference一致、未确认虚假声明才可到达；显式任务格式属critical不能放宽，任何更严重gate优先。实测未授予一次upgrade。不能以该方法为理由跳过本库任务/接口约束。

D2的“suspect”是送审路由，最终表无该状态；无verdict既不clean也不gamed，仍保留分母。论文描述保守多数/分歧清除，但本次无代码核对具体投票分支。D1的gate typing使用模型，后文把D1/D4称“deterministic dimensions”应理解为后续决策规则，不能称D1全流程无judge。

## 数据、实验与消融（§4，B–F）

108个ALE任务、三难度层/11域，五配置同harness/decoding，原先各一次；D1–D3声明相同11任务无法离线重评，余97。judge为GPT-5.5三票，主文只报告独立票/一致性，未证明误差独立。D4先在Sonnet取得87题五次完成，再从中按层级及recorded band抽50题，五配置各五次；两次Sonnet campaign不是同一组重复结果的直接子集。完整实际输入、费用和随机性细节不由这些数量自动成立。

- **D1。** confirm为50–61/97，contra35–47，主要partial→非完整pass的阈值差；真正pass→fail每配置2–9，fail→pass1–2。1078个gate内三票94.1%一致、两次标注96.8%一致，不是对human真值的准确率；作者把人工gate标注验证列为未来工作。
- **D2。** gamed/97从10到49，未给verdict3–28；Gemini25/97=25.8%，若仅看已有verdict为36.2%，缺失非随机，不能删除后作普遍排名。Sonnet14项gamed人工核对，不能外推全模型precision。注入无来源reference值36/38被检出，执行代码写入的只有2/45检出，直接暴露laundering盲区。多数gamed来自judge-fabrication（78–100%），不是全确定性来源证据。
- **D3。** confirmed counts17–55/97，包括原pass档；Sonnet两个人工样本上claim识别48/50一致、kappa .85/matcherF1 .91，severity kappa .84/judgeF1 .97。只验证一配置/样本，不证明全配置judge准确，更不推断欺骗意图。
- **D4。** 50题跨档18–46%；分档组成随模型不同，只能在同档或适当控制后比较。Sonnet87题25.3%varied与新50题campaign46%不同，作者同时保留，不能挑低值。181个stable中16个稳定在不同于原来的档位，包括四个原pass；若要求原档重现，结论会变。按原pass/fail分组后均值差正负部分受分档边界制约，不单独证明原benchmark有系统性偏置。p_hat^k是估计连续成功量，未在本次确认跨run独立/平稳前不能当真实恢复保证。
- **合取/消融。** 50题×配置中的84个原pass，19个清四维，作者Wilson95%区间15.0–32.6；各配置13–20个原pass，区间全重叠，不作排名。D1留下50，加D4留下34，四维后19；后15项由D2/D3进一步排除，但D1先有gate标签，不能说34项完全无模型判断。计数可重叠，不相加；all-band总数受D1拒绝partial的定义主导。相同题跨模型重复，汇总Wilson不是本次已验证的题级聚类人口区间。

## 原文未解口径与限制

1. §4.1称D1–D3同11题排除/97题；但Table6（D1 recorded bands）与Table9（D2 assessed列）在部分模型的原分档数量不同：MetaMuse为22/37/38对19/41/37，GPT-Sol23/36/38对21/38/38，Opus24/33/40对22/36/39，Gemini18/25/54对16/27/54，Sonnet两表15/36/46一致。Table9 Tasks列是108全体、不能直接与97比；上述比较特取assessed列仍不一致。本文不补造不同snapshot/阈值/排除原因，不将其当共同逐题cohort已核对，也不从表反推自己的模型排名。
2. §4.2宣称同输出五次grader重执行在“all108”一致，但§4.1有11题无法离线重评分；实际重评范围/“无verdict也一致”是否包含其中未明。保留原文疑点，不改写成108题可重评分。
3. D4先完成筛选、基础设施排除及两次campaign差异会影响外推；未读到对剩余0个有效repeat、精确排除数量/不确定分类错误的充分处理，不能自行规定“无运行即stable”。附录A给每题方差说明，没有完整执行代码。保留为未核实边界。
4. 本次没有原grader/trace/作者代码来独立验证gate覆盖、judge prompt或引用值来源；代码待发布。D2人工precision、D3人工标注只一配置，D1还缺人工gate真值；judge同意不是校准。原文无可用于本库的全角色token/完整账单或端到端性能数据。
5. 证据仅ALE，接口可移植的主张仍须其他基准实测。分数不覆盖权限、工具真实副作用、任务取消、旧依据传播及基础设施可用性；这四维不是全项目可靠性证明。

## 与本库的关系和决定

静态核对result_validation.py、result_validation_workflow及真实CLI：声明的producer→独立gate→consumer关系、相同合同及独立owner不可省；manifest与六类依赖、review evidence在可信回调前后重查，当前revocation/绑定检查不授予跨动作原子性。宿主须认证真正独立事件，不能凭producer JSON的actor/independent标记。持久proof不能恢复信任，无provider保持pending，callback异常/缺证据不会变usable。CLI只加载显式可信host adapter；显示外置不等于验收。这些控制不自动实现论文的graderreplay、值来源、声明判定或repeat质量。

采用为未来评价方向：保留原score和失败，分开结果正确、过程证据、终态声明、同条件复现；unknown/无verdict单列；实际任务成功率另保留所有基础设施失败、取消、预算耗尽和费用，不用筛选后的稳定率代替。暂缓新增四维评分器、三judge默认投票、五次自动重跑、阈值放宽、共享聊天池或agent_doc迁移；没有本库同条件收益证据，旧后端/验证额度不重开。

先查2610.07274，max_scan5000扫描327目录，无命中但25缺record错误，status=incomplete/partial=false，不是历史不存在的证明，无实证复用。实际knowledge查询命中conformal-policy-control与betting-test-martingale；缺其分布/似然/稳定性/条件均值等前提，拒用、adoptedrefs=[]，不借定理认证三票或五次run。

无生产修改、测试或实验模型/后端调用；独立阅读/源码复核是另一实际AI调用，全部角色tokens/费用unknown。手工复核不冒充受信ReviewSession/native验收，历史登记保持unknown/null；真实宿主、完整输入、最终任务质量、全费用及并发恢复等SYSTEM-99未决不关闭。
