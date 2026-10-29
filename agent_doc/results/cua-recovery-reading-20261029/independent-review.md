# CUA-Recovery 冻结阅读结果独立静态审核

- Task: SYSTEM-99；当前稳定计划 Version56。
- 项目：`/workspace/scratch/95d615402a52/agent-run-1202`。
- 决定：**accept（仅带疑点的文献阅读与源码关系说明范围）**。
- 阻断项：**无**。下列编辑建议不阻断本次阅读接受，不要求第二次审核；主控可在后续版本作有限文字更正并保留本反馈。
- 这是一次真实分离上下文 AI 的手工静态审核，不是 ReviewSession 受信回执、完整受保护计划批准、实验复现、性能认证或 SYSTEM-99 完成。审核调用额度1/1；未重试任何旧门禁，尤其没有重试或改判 MemDerive。

## 已读覆盖与方法

实际读取 AGENTS.md、项目文档治理的相关权威/写入/交接规则、只读 guide README、空 GUIDE.md、唯一 TASK 的 SYSTEM-99 项及 SYSTEM-99 详情的目标、稳定 Plan56 和相关末尾进度；未以巨大历史全文审读冒充本次必要覆盖。确认 guide 全目录人类专用、总 TASK 由主控唯一写、本人只写本审核目录。

实际读完冻结 `reading.md`、`inputs.json`，对 inputs 的全部11项 source_refs 计算 SHA256，均匹配。正文采用不超过16000字符的切片读取，完整科学覆盖为 `[0,39470)` 与 `[50261,117016)`，具体切片为 `[0,16000)`、`[16000,32000)`、`[32000,39470)`、`[50261,66261)`、`[66261,82261)`、`[82261,98261)`、`[98261,114261)`、`[114261,117016)`。没有以摘要、关键词命中或参考文献替代正文。后一个范围末尾包含少量 HTML 页脚。覆盖 §§1–6、附录 A–G、Algorithm1、Eq1–5、Tables1–18、Listings1–6 以及图注/相关解释；未视觉检查 PDF 或图像细节，未读完整参考列表。

实际复读源码 `agent_runtime/core.py:292–375`、`project_memory.py:278–332`（另读模块头的调用者责任说明）、`handoff_basis.py:218–290`、`maintenance_gate.py:1–140`；另读 task_supervisor.py 模块头。只作文本检查，无运行测试、模型、作者程序、数据或实验。

按允许范围独立执行只读现有知识检索：`python -m agent_runtime.knowledge --root knowledge search recovery --limit 3`；返回 backend `files-lexical-v1`、snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`、results=[]、applicability=unchecked。因此本审核 knowledge_refs=[]，没有套用未命中的知识条目。

## 科学内容核查

1. **方法与验证边界准确。** POMDP、持久状态、根因/接管深度/显式证据延迟、金标准 lineage、grounded port compatibility、合成 DAG、冻结 non-sink expected values、保留被检查 sink 的运行时值及 mutation 判定的区分与正文相符。417候选/17857 executed mutations 的分类和327通过、R的分母及阈值均有原文。无 freezing 和 divergence 的对照是二者同时移除；reading 没有将其归因为单独 freezing，判断正确。mutation 分数不能保证真实 agent 轨迹或所有错误被发现。
2. **数据与抽样解释准确。** 135/184接受来源和49排除分型相符；477工作流、377/100 split、8577训练轨迹及2250接管状态相符。source workflow split 的边界说清：同一工作流派生数据同 split，但没有证明源任务、实体或persona隔离。后续 MyPCBench clean-start 是源环境的评价，不能升级为源任务完全未见。前缀修复和失败筛选意味着受控单根因状态；不同深度资格改变、同一失败派生多状态、602/619观测证据与17未观测的区分都正确。无法由跨深度均值识别截图窗口损失的因果效应。
3. **训练与消融解释准确。** F.4每层最多8次、3层再1次teacher、首个成功与失败丢弃、去hint和泄漏检查均有依据。称为success-selected、最多25次的生成预算符合原文，不等于实际每例花25次，也不等于一击自主恢复。F.3 token-matched success-only对照支持该控制下 recovery数据优势，未独立隔离hint、teacher、错误暴露、筛选或prefix repair。训练资源及局限未外推为当前仓库可执行资源。
4. **结果数值与重要矛盾保留恰当。** Table2/16 的self-takeover最大 EAR44.0、最大Pass@3 25.5；Qwen平均19.9→35.2、5.0→16.1和clean-start15.3/10.8百分点均相符。不同策略自身失败来自不同条件难度群体，不宜直接解释为同难度排名。共享来源状态只支持各深度内部策略对照。
5. **d25 Evo矛盾真实存在。** Table2明确 Evo self 2.3、ReRail 5.4（d20为4.6 vs3.1）；G.1却说d20与d25均lower Pass。reading正确保留表文冲突，未重复全称“后期均有害”，也未擅自替作者订正原始数据。G.1另有“all three runs”措辞，而Pass@3定义是任一成功；reading采取表定义而没有沿用该错误措辞，这一点合适。
6. **Table18疑问属于应保留的未知。** G.3是个体rollout的aware/unaware分组，macro对agent等权；不是随机意识干预。GPT两个条件值34.7/31.1均超过Table2/16所有该agent Pass@3 cell。若同一状态集、权重、缺失处理及相同成功标准，则加权个体成功率不应超过相应any-of-three成功率；本文未提供足够原始数据验证这些条件。reading明确条件和未知，未指控造假、未机械等同分母、未据此设仓库恢复验收指标。此保守结论无需先解决作者数据未知。
7. **EAR与judge agreement范围正确。** D.3允许识别任何继承问题，不要求准确命中annotated error；G.1只看前三reasoning segments。因此EAR不是修复、精准诊断或最终验收。E.1的30%双标只覆盖三种本地策略；E.3的80 tasks为43Qwen/37Evo，20人类pass/15LLM pass、5FN/0观测FP与汇总precision/recall吻合。没有独立EAR人类校准数字，也不能把所选80的零观测FP升级为六策略或普遍保证。
8. **费用与资源解释有边界。** API16493美元、GPU9322h、sandbox2050h及训练1152GPUh均可定位；takeover时间/费用存在估算，annotation未给出可直接并入的完整总额，本地模型没有API费用不等于没有资源成本。32并发×8GPU的潜在256GPU占用有原文。没有由论文估算推断本轮全角色token/费用或仓库收益。

## 源码关系核查

core的完成证据重验与声明依赖闭包、取消保护、审核后已发生效果的blocked/reconciliation边界，以及显式reconcile的授权/依赖/handler.verify条件均与笔记相符。handoff_basis检查bound知识/记忆/产物并限定declared local claim DAG；不发现未声明语义依赖，不重写旧ACK/历史。maintenance_gate仅对精确观察且handled结果ACK，pending/异常/观察变化不ACK；不是调度器或科学恢复验证器。

MemoryLedger创建不可变新revision、supersede旧项并stale声明后代，correct的source应标识真实用户语句，均有依据。**需保持调用者契约与代码认证的区别**：模块头要求调用者提供科学独立验收；accept函数本身只调用 `_revise(..., accept=True)`，检查candidate等本地条件并创建verified revision，没有自行认证trusted host、核实用户语句或开展科学验证。原笔记的“accept needs trusted host verification”适合作为外部契约提醒，不应读成该函数已经强制实施。此项作为非阻断澄清，未发现需要本轮生产修改的缺陷。

## 补充只读作者源码（冻结阅读之后新增）

主控在本次同一审核期间提供额外三份文本及来源清单，未改原inputs/reading。已完整阅读、计算并匹配该清单SHA：

- author tree（主控来源清单声明）：`80e06bcf22615bc44456753fe4387a40d17e0f89`。
- `author-metrics.txt`：`ac0472070727a23425ee7a04cc93520152b3e84e98e0c56686f4de8377ec5cfa`。
- `author-summarize.txt`：`f2043dea76d1948020413737b63b22344343ce36b8424583ffd3b2e8a115480f`。
- `author-license.txt`：`1d0dde41ece0f9620937f1a81a67e295ace0eae180c009d862006e8f3b288458`。

本审核未联网独立认证GitHub tree交付链，只核验收到的额外文本及其静态语义。metrics.pass_at_k对显式units去重，拒绝分母外runs；默认缺失计失败，可配置排除；每unit任一有效成功则solved，rho采用首个成功rho，否则有效失败中最大rho；另报missing/incomplete。summarize以manifest eligibility或task目录集合确定units，仅接受configured judge的非空结果。这提供某些分母、missing及rho处理的实现线索，但没有作者原始数据、EAR分组实现或论文生成链绑定，**不能因此宣称Table18矛盾已解决或表值复现**。

LICENSE文本确实是MIT、copyright 2026 Anonymous Authors，可由主控追加有限核查说明。冻结笔记原写“未看LICENSE/aggregation code”在其原时点成立；后续若更新，明确是新增补充的三文件静态阅读，不将其倒填为原冻结阅读已覆盖。

## 七域反馈

| 域 | 状态 | 依据与边界 |
| --- | --- | --- |
| intent | pass | 满足带疑点正文阅读/源码关系审核；不是部署、实验、新性能或整批结案。 |
| guide | pass | GUIDE为空、README限制已读；guide只读、唯一TASK和角色单写不变；无新授权推断。 |
| assumptions | pass | 条件确定性、gold与真实评估差异、选择/深度/相关样本、source split、judge范围与Table18未知均明确。 |
| prior_results | pass-with-scope | 冻结inputs保留scanned338/errors25/status incomplete/无结果/不复用；本人没有认证这些历史查询的完整性或重新搜索历史结果。无旧结果被升格为当前实测，recovery知识检索无命中。 |
| acceptance | pass-with-scope | 所声明科学范围已完整分块复核、11项SHA全匹配；只接受文献阅读，不接受未经运行的作者代码结果、系统收益或受信runtime。 |
| risk | pass | 自动重试/终态放行/写回/微调/架构迁移均defer；保留不可逆效果和独立最终验收；未开旧门禁。 |
| resources | pass-with-unknowns | 单次有界静态审核在deadline前完成；无测试/模型实验/付费新增资源；全角色input/output tokens、实际费用和精确provider计量均unknown。 |

## 非阻断编辑建议与保留未知

1. 将MemoryLedger句改为“accept的科学独立验收由调用者/可信宿主负责；该函数只检查本地修订条件，不自行认证科学验收”。避免读者误认已部署机器认证。
2. E.2句的“table heading usesPass@3”建议改成“E.2正文称Pass@3，但Table10标题说trajectory-level full completion”；实际表题并未称Pass@3。该编辑不改变已正确指出的人类agreement层级歧义。
3. 如采纳额外三文件，补写有时序的addendum：MIT LICENSE已静态看到；pass_at_k/rho/分母有部分实现依据；原始数据、EAR条件分组与论文表值关联仍未知。不抹除原被冻结的‘未查’历史。

保留但不阻断阅读：Table2/G.1 d25冲突、Table18聚合/分母不明、E.2层级表述、未审图像、作者数据与完整实现未复现、独立运行时认证和真实宿主/全输入/最终任务质量/总成本未验。它们阻断相应量化验收与收益外推，不阻断带这些限制的阅读记录。

## 冻结输入SHA256

inputs.json实际SHA256：`4ae1b7f36d28c3029bad7994a9dc61580ae9c9868c8ed9a1a94d9cc44a5510a1`。

| 输入 | 实际SHA256（均与inputs匹配） |
| --- | --- |
| AGENTS.md | 97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed |
| agent_doc/task/TASK.md | cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f |
| agent_doc/guide/GUIDE.md | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| agent_doc/guide/README.md | f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261 |
| agent_runtime/core.py | a567a48f765aa0e14f5f60c63a601f3ecdf57f9d2b09157bbde9b4660dae8712 |
| agent_runtime/project_memory.py | 1f0fe4edc8abf2371972817083c2c12cc33dbb07640ed57dffc2d8a744b35e41 |
| agent_runtime/handoff_basis.py | 20b4e127726f046b564086d2c5028ba92e986c6b796784a23cfe94971071f50a |
| agent_runtime/maintenance_gate.py | 91f40b40d92e7b8ce2f60e424033381d434c9e4b0bf405c2ca890917312d4e05 |
| source.html | 59de7d3c746fdcd9a635a146c467642b5743cfe99c48bceb6859a48aeaa739ed |
| source.txt | 8dddd7705770f41e0fb9acec169a8f26b71716424f8608a60bc5773fd3d6f99d |
| reading.md | 122d749893ddd3ad3487f5256dcde58e305e4acb1960fee5e32aed41b60e2da1 |

审核者未写TASK、guide、生产源码、producer原稿或原有历史证据；本审核报告是唯一有意新增产物。完整反馈已保留；无第二次调用、无实验或测试验收。
