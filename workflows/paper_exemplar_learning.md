# 写作前范文学习 v1

完整新稿或全稿重写，在动笔前执行。先读本角色真实 SKILL、execution、论文交付契约；这一阶段辅助写作，不替代本稿的研究证据、科学审稿或最终 PDF 全页检查。局部修字不追溯强制重学；本次用户明确要求的 10 篇是硬条件，不能静默减少。

## 1. 确认投稿情境与能力

先确认用户指定模板、venue/year/track、语言、研究类型与篇幅；用户具体模板优先，核查对应官方作者指南的来源/日期/模式并记录差异。没指定时选择与题材匹配的高水平会议及公开模板，写明选择依据，不暗示用户已承诺投稿。规则尚未发布时明确 provisional；不能拿往年模板冒充当年确认。模板未核验可继续搜集/阅读，但不得宣称前置完成或开始本轮全稿写作。

复用已锁定且适合的 writing/reading skills，必要时查实际 SKILL.md、references 和许可证，记录 URL、commit/hash、适用与不适用部分。已有 research-write、paper-reading-companion、research-read-pdf 可分别提供论证组织、原页定位、图表阅读方法；伴读页面生成或 PDF 文本抽取本身不等于读完。外部 systems-paper-writing 等是候选辅助，不是本稿科学证据；不能照搬其固定页数、段落数或未经核实的例文细节。

## 2. 选定 10 篇不同的已发表相关论文

记录每篇规范身份（DOI/出版机构标识，合并预印本与出版版）、题目、真实 venue/year、出版证明 URL、全文来源、选择理由与质量依据。选择以目标 venue 同题材/同类论证为主，兼顾不同写法、图表任务与代表性强基线；不是只挑支持己方结论的作品。高引用、获奖、venue 声誉只能辅助，不代替技术与写作质量检查。

未来会议尚无 proceedings（如以 DAC2027 为目标的早期准备）时用已发表的往年 DAC 同题材论文并标真实年份；可适量纳入方法/评测可比的相关系统顶会，逐篇说明可迁移性与限制，不能假称来自未来届次。不能用 10 个 URL、同文不同版本或只有摘要的条目凑数。

候选全文无法合法获取时标 access_blocked、寻找作者公开版或替换候选；access_blocked 不计入已完成 10 篇。记录版本差异，不绕过访问限制。默认只在私密项目区保存合法获取的原文与笔记，不将第三方全文/图或用户材料推到公开 agent 仓库。

## 3. 实际读全文与图表，逐篇形成可核验分析

冻结原文 PDF hash、物理页数，阅读全文（包括引用、附录及选定版本所有页）；保存逐页实际观察、工具阅读回执与覆盖状态。正文可用文本辅助，但所有图/表及图注必须打开原页阅读，记录图表完整 inventory 和逐项覆盖；没有图表时明确全页检查后的 absence_reason。截屏/渲染成功或总结流畅不等于阅读发生。无法阅读任何页/图表时保留缺口，不算 read_complete。

每篇至少分析以下五个维度，以 section/page/figure 等位置支撑，写自己的观察、效果与可迁移/不适用原因，不抄长句：

- organization：摘要、引言、背景、方法、评估、相关工作、结论的顺序与篇幅如何服务读者问题；不限固定章节。
- claim_evidence：问题→洞见/贡献→机制→证据→限定如何连接，什么实验/证明排除什么替代解释。
- figures：每个图表的论证任务、视觉编码/轴/单位、对照、caption、出现位置与正文呼应；区分装饰和证据。
- rhetoric：术语定义、段落主题句、因果/转折、贡献措辞、结果强度与限定语；归纳句子功能并原创表达，避免拼接他人句式。
- content：背景深度、设计取舍、实验设置和结果的分配，以及限制/负结果/复现细节放置的理由。

把文体学习 ID（EX01…EX10）与本稿科学 claim/evidence ID 分开。范文结果不是本稿结果；需要作为 related work 科学来源时另建引用核验与精确支持关系，不能凭文体阅读自动认证。

## 4. 跨文归纳 → 本稿蓝图 → 实施

完成 10 篇后比较共同模式、分歧、例外及各自适用条件，保存 synthesis；不能由单篇复制出通用模板。生成私密 writing_blueprint：本稿主线、章节/段落的读者问题与证据安排、图表任务/图注计划、措辞与术语策略、篇幅依据。每个学习决定记录来源 ID+锚点、采取/改造/不采用及理由、本稿目标位置、本稿独立证据 ID或明确缺口。五个维度均有具体决定，不能只有“更清晰”“像顶会”等口号。

主 AI 确认前置记录后才启动本轮正文写作。保留既有草稿；之前先写后学属于前置违规，需要重新执行受影响写作与复查，不倒填时间。继续完成不依赖写作的文献/数据整理；缺项列 blocker，不伪称端到端完成。

作者在本稿中实施蓝图，保存 implementation_map（蓝图决定→新稿位置/对应变化→本稿证据或缺口）；没有旧稿时给具体实现段落即可。不机械执行不适用范式，不为“像范文”编造生产观测、实验数值、贡献或删除 limitations。不复制长句、数据、图、无许可图源；原创绘图仅使用本稿合法证据，注明必要的学术归因。

## 5. 独立验收

审稿角色核对 10 篇身份/覆盖/笔记与实际原文、跨文归纳、蓝图和稿件，评价 blueprint_application：哪些组织、claim-evidence、图表、措辞、内容安排决定实际落地，哪些被合理拒绝；逐项给稿内位置、来源锚点、具体理由和反例。不接受只有 10 个链接或通用标题的 checklist。不能以蓝图执行掩盖论文科学内容不足。

若缺模板核验、未读页/图、access_blocked、缺分析/蓝图、先写后学或未见实际实施，则前置/交付不通过。有限 evidence 的原创论文可以学得充分但仍为工作稿，两个状态分开；学习完成不产生 submission-ready 结论。

## 6. 私密记录接口（与 validate_paper_delivery.py 配合）

paper delivery record 增加 drafting_started（本轮正文是否已开始）、exemplar_learning；schema_version 仍为 1，历史记录缺此扩展须补录真实证据或标未执行，不能补造。

exemplar_learning.state = completed / not_run / blocked。未完成时 reason 必填，drafting_started 必须 false，保存已有稿为历史输入且不宣称本轮已写；待材料齐备后续跑。completed 时：

- template：verified=true、provisional（bool） 、venue、year、track、source_url、checked_at、evidence（path/sha256）。核验是针对实际采用模板，provisional 必须说明并阻止 submission_checks_complete 的 format pass。
- skills：selection_notes（path/sha256，含实际候选入口/版本/许可证和复用理由）。
- papers：正好 10 条，identity、title、venue、year、publication_url、selection_reason、quality_reason、published=true、access=full_text、pdf（path/sha256）、page_count、read_pages（完整物理页）、read_receipt 与 notes（path/sha256）；figure_inventory、figures_read 为图和表的唯一 ID 列表，无图表时 absence_reason；analysis 含上述五维，每项 location、observation、transfer。
- synthesis、blueprint（path/sha256）；decisions 非空，每项 dimension、source_ids、source_locations、decision（adopt/adapt/reject）、rationale、target_location、own_evidence（本稿证据 ID 或明确 missing，不允许填范文 ID 冒充）。
- completed_before_drafting=true，preflight_receipt（path/sha256，绑定学习结果、时间/事件与随后写作启动）。它是记录声明；宿主时间序列由主 AI 核验，不是布尔值能证明。

每个交付 language version 增加 implementation_map（path/sha256）和 checks.blueprint_application（verdict/location/reason/evidence）。完成态必须 pass；前置未完成的 partial 可标 unresolved 并列具体 blocker。脚本检查覆盖/哈希和声明一致性，不证明实际阅读、已发表身份或蓝图应用质量。不得将合成记录测试宣传为 10 篇真实阅读或论文改善实测。

## 7. 架构图学习与绘图角色协作（按图任务触发）

用户要求架构/流程图或本稿计划采用这类图时，architecture_requested=true，前置必须包含架构图设计学习。10 篇语料优先包含可比架构图；不强制每篇都有架构图。对选中图打开实际像素（多面板逐 panel），记录 source identity、figure ID、页码、原页 hash、打开/阅读回执；文本 caption 或自动视觉描述不能替代实际查看。学习该图为何突出核心贡献、如何区分既有/新增模块、抽象层级与读者认知负担、布局/数据流箭头、颜色语义、字体、留白和多 panel 叙事。记录取舍、误读风险及本稿为何采用/不采用；不以“简洁、专业、顶会风格”代替具体判断。

reader 把定位清楚的图像分析交给 `research-diagrams`（混合图由 `research-figures` 协调），实际启动绘图角色讨论：本稿最重要的科学问题和贡献应该怎样被看见、哪些实现细节应省略、图与正文的分工、哪些视觉方案容易误导。收到真实角色结果后选择/修订方案，不能把发消息或路由表当协作发生。没有独立角色能力可如实标 staged 并完成设计工作，但不得宣称独立协作验收完成。

产出私密 visual-design-brief：贡献焦点；信息/视觉层级；抽象层级；布局与数据流；色彩语义；字体/留白；多面板分工（单 panel 时给理由）；科学不变量（张量维度/依赖/时间顺序/符号等）；本稿真实结构来源；参考图位置；原创方案与替代方案取舍；交付与验收。具体使用何种工具由 research-diagrams 选型，避免为了像范文而改写机制。不能复制原图、图标或无许可素材。

独立审阅分别判定 diagram_scientific_accuracy（节点/箭头/边界/符号与真实方法一致）和 diagram_visual_design（贡献是否醒目、层级/对齐/阅读顺序/编码/留白是否有效），均给最终图定位与理由。美观不能补救科学错误；正确但平庸的图也不能自动通过用户的视觉目标。保存 brief→方案→最终图的 implementation map，由原页阅读者与绘图角色复查。

记录：顶层 architecture_requested 为 bool；为 true 且 exemplar_learning.state=completed 时，learning.visual_design 含 brief、reader_receipt、diagram_role_receipt、selection_evidence（path/sha256），mode（independent / staged）、reader_actor 与 diagram_actor；independent 时必须不同实际上下文，staged 时 reason 必填且只能 partial，未完成的独立协作验收列具体 blocker；source_figures 列表每项 identity、figure_id、page、pixel_read=true、receipt（path/sha256）。analysis 含 focus、hierarchy、abstraction、layout_flow、color_semantics、type_whitespace、panels，各项 source_location、observation、design_choice。每个最终 language version 的 checks 加入 diagram_scientific_accuracy 与 diagram_visual_design；完成态须 pass。不需要架构图的任务 architecture_requested=false，不能将本用户明确要求降级为 false 来跳过检查。读者/绘图回执仍需宿主核实真实性。

## 8. 数据图专属分支

包含数据图的论文还必须执行 [数据图范文学习](data_visualization_learning.md)。复用当前十篇完整语料的相关数据图，补八维观察、data-visual-design-brief、research-data-visualization 实际协作与最终数据/审美双验收；架构图分支不能代替它。
