# WTB：从执行证据到持久效果的权限边界

2609.08472v4，*From Evidence to Effect: Authority Semantics and Runtime Infrastructure for Stateful Agents*；Yang Li、Zongsi Xu、Sergey Volkov、hai liu、Tuo Zhou、Xiyu Chen、Di Wan、Dian Shao、Ye Luo、Hao Sun。v1于2026-09-08 09:11:53 UTC提交，实际读v4（2026-10-19 08:35:24 UTC）。[正文](https://arxiv.org/html/2609.08472v4) · [版本历史](https://arxiv.org/abs/2609.08472)。同一SYSTEM-99 / Plan54继续未完成；本记录不是本库性能、真实宿主或整轮验收。

## 实际阅读与版本

0002检查点读正文§§1–11和附录A；0100续读B–L。合计Tables1–22、Figures1–4图注及声明范围正文/附录文本；未看PDF/渲染图、作者代码、完整实验包或逐题原始轨迹，未复现生成/统计/事务实验。精确字符范围、原始HTML/规范化文本SHA见inputs.json；参考文献和HTML页脚不算科学正文。两次读取只计一篇，独立复核和公开回读后可恢复记录31→32，不抵扣未来新批次。

## 方法、证明与前提（§§2–3，A–C）

状态S由材料/工作区W、执行证据E、作用域权限A、效果账本L构成。权限充分性要求存在规则从观察O(S)和请求a判定准入Y(S,a)，等价于Y在每个观察纤维内常量。它是指定状态/请求域上的信息条件，不保证某模型会实现该规则，也不保证未来权限。相同可见观察、相反二元准入的均衡世界对，观察型规则期望正确率为1/2；不是任意任务的成功率上限。

三个干预分开：C0→R0增加权威事实；R0→W0用相同事实的无损原始/类型化编码；W0→W1冻结意图、改变效果放行。无损编码保留信息划分，实际模型决策仍可能因呈现而变，不能将格式收益归成新增事实。

发布绑定包括贡献者的原生execution、精确attempt、actor/scope、完成receipt与权限generation，及材料/version/贡献链和approval。相同字节可属于不同准入版本，撤权再授权也不等于连续权限。成功旧attempt不能直接授权新执行。

| 路径 | 证明依赖与明确限制 |
|---|---|
| 本地效果 | 相关状态写者与check/consume/commit共用序列化事务，效果在该事务前态满足准入，唯一key与approval消费防重复。可信证据、actor归属、存储及完全中介均为前提。 |
| 外部效果 | 本地事务检查、消费approval并先持久化不可变key/payload/token/reservation；接收端原子检查其当前权限token并按key唯一插入。旧receipt返回不产生新效果。 |
| 丢响应恢复 | applied查询恢复receipt；权威absent查询后重查贡献者/材料/approval并重发相同key/payload/token；unknown保留pending，不猜失败。重试不再要求Unconsumed，因为原reservation已消费approval。迟到发送者与重试仍靠接收端去重。 |
| 两个提交点 | 接收端权限是其实际检查状态。本地预发送检查不能推出全局策略更新与远端写入的统一顺序；需要额外协调。安全允许无限pending，恢复可用性还需最终可靠lookup、稳定权限及可达sink。 |

三种完整控制共享合作接收端，服务贡献不能归给WTB独有机制。DSH SDK能做durable receipt lookup但该集成不支持checkpoint rewind；LangGraph facade的process-local provider身份不能仅凭相同checkpoint路径跨新facade恢复；Ray prototype禁用原生retry并有driver-owned dispatch fence，未验driver重启。三者持久化能力不统一。

## 实验单位、对照与消融（§§4–9，D–K）

六个研究家族不可池化成独立样本：128 authority cells、96 planning calls、32 fixed-intent replays、392 contract checks；6次原生capture复用产生960确定性cases，另有24次live interleavings；1120独立coding slots、120 prospective SWE stage slots及117条连续轨迹/468阶段结果。native assertions、模型responses、stage、trajectory、task/repository各有不同分母。

1. **事实/呈现。** R0与W0语义结果均32/32，C0/G0均0/32；首动作是各arm专属政策，不可横比。C0可安全BLOCK且保留正确字节，但common semantic要求非BLOCK的解决，因此0完成不等于32不安全。R0一次ITT失败为允许文件重读违反严格执行协议，语义仍成功；1/2二元定理不预测有abstain的完成率。另一96调用使用不同模型路由：raw→typed时DeepSeek unsafe 8/8→0/8，GPT Nano 1/8→6/8；11个typed unknown全来自DeepSeek，包括7/8未授权情境，不能声称格式普遍改善规划。
2. **固定意图放行。** 同32个W0输出不重生成，16未授权世界零非法效果，其中六个不安全publish意图被拦；12/12有效授权意图执行，另四个授权世界缺有效意图，不能写成16/16任务完成。原生gate改善效果安全，不产生缺失计划。
3. **完整能力对照。** 原Git/Auth、CONTINUITY、MasDrift分别36/56、44/56、28/56；增强后与WTB都56/56。补齐职责的能力相同，增强所需工程工时未计。后续编码差异来自供应功能、API便利和应用接线的组合，不隔离单一架构因果。
4. **职责消融。** 三runtime×两backend×20预设world×八实现为960。完整控制均120/120、60/60合法效果、零非法；去精确attempt/generation/consumption分别引入12/6/12非法效果。去monotone reconciliation同时伤安全和合法完成；去unknown recovery零非法但少六个合法完成。表中legal-correct须效果计数与状态都对，不能只用completion flag。不是960次新原生执行、生产故障频率或维护成本估计。
5. **live时序。** DSH与LangGraph各12次，两backend/三完整控制/相关或无关权限变化；12相关变化拒绝，12无关变化各保留一效果。Ray仅在确定性矩阵。更长执行、多权限写者、干预中崩溃未覆盖。
6. **独立采用。** 四source cohort×十block×四arm×七stage=1120；E0空代码，E1等从指定arm脚手架开始，每slot独立，不传前slot候选。三来源WTB176/210，publication19/30；E3/E6有对手更好。E0–E2或全阶段bundle是独立slot汇总，不是持续恢复证明。predecessor历史构造未计成本。
7. **真实库接线。** 12选中库→10通过输入/native-test资格，其中8主分析、2开发；另三库calibration有单次等预算收费continuation。空应用代码加供应native libraries和reference patch材料，C0/E2/E4累计验收5/7/11治理场景，失败代码可后续修复，因此WTB5/8core→8/8recovery→4/8handoff。任务是治理接线，不是自主解决上游issue。六比较Holm后的recovery p=.09375、handoff .375，均未达.05；不从描述性大差值宣称总体显著。
8. **连续维护。** 十二task×arm起点预先通过共同E0–E2，四stage按前一已接受候选延续，失败关闭余下阶段。117条完全可观察轨迹保留方法失败及predecessor-blocked，但未决操作中断轨迹不进入complete-case、原协议禁止选择性替换。9/10分母和E4 accepted/entered随arm变化，不得补成120条ITT或忽略选择效应。九个Holm比较均>.05，最小.28125；六个joint-success费用对只是共同成功子集。

## 费用、材料与复现限制（H–L）

收费coding每stage最多64 valid responses、64 requested actions、三次验收，DeepSeek V4 Flash/high reasoning，16384 response cap。报告费用包含供应库之上的成功/方法失败与返修response工作，不含库历史构造和人类工程。连续队列8067条completed response记录共$27.615736318，条件于117条观察轨迹；不是所有计划调用的完整总账单。

WTB在主SWE recovery的固定工作量费用较低，handoff时Git/Auth总费用更低但零handoff接受；共同成功对Tornado、calibration等对手更便宜。单位成功成本受成功率和条件选择影响；不能概括每题更省。成功应用新增约116–135行是供应库之上的条件均值，未计native库建设，不能替代实际token、总复杂度或维护性。

TeamBench/BulkPR/Terminal各只取一个固定适配task，三种two-producer分组是实验file-group改编；上游revision与冻结workload revision不同。BulkPR官方hidden verifier不可得，仅有164本地测试；预备W1零付费replays与正式矩阵分开，不能充大正式样本。source基准背景不等于benchmark-wide问题解决率。

L的compact package支持数值/图表重建，TeX可离线编译，不包含完整fresh execution stack；重执行还需SDK、native/comparator库、controller、冻结starts和容器。本文只阅读这些声明，未获取/运行其分析包，也不把build成功当模型实验复现。模型/供应商行为、prompt或contract变化均是新条件。

## 对本库的关系与决定

静态核对core/TaskSupervisor/Reporting入口及publication.py：已完成状态会重验证据与依赖；过期非幂等副作用保持ambiguous并要求明确reconcile。PublicationLedger冻结候选/任务归属、复核来源与验收，远端观察前后再过gate并要求准确branch/commit回读。它明确不stage/commit/push，须宿主串行调用与可信authorize/accept/reader；私有JSON非同权限攻击者的防篡改账本。Context.current只约束本地token/lease/cancel，不能认证第三方接收端效果。没有查证到需修的新契约缺陷，也不能据此说外部提交已具论文的原子保证。

采用为评价与设计约束：区分事实完整性、呈现、冻结意图的放行；分别报告拒绝不安全效果、合法恢复、unknown停留、重复效果和最终质量。应用论文证明前必须验证合作接收端/权限token及跨存储协调前提；现有未验条件保持unknown。暂缓另建authority ledger、runtime adapter、自动重试/默认typed视图或agent_doc迁移。恢复条件是原生宿主能力和符合现有权限/预算的独立验证方案；旧耗尽/暂停边界不因本阅读重置。

结果先查2609.08472，max_scan5000扫描326目录，无命中但25缺record错误，status=incomplete、partial=false；不证明没有旧记录，不复用实证结果。实际knowledge查询只得到segment-monoid与avian-pallium-convergence，身份词重合不满足effect权限假设，拒用、adoptedrefs=[]；query快照见inputs。

无生产修改、测试或实验模型/后端调用；独立阅读/源码复核是另一实际AI调用，全角色tokens/费用unknown，不能称零模型成本。手工复核不是受信ReviewSession或native验收，历史登记unknown/null。真实宿主、完整模型输入、任务质量、全角色费用及跨存储/并发恢复等SYSTEM-99未决继续保留。
