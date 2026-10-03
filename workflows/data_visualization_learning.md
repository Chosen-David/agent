# 数据图范文学习与设计前置 v1

由现有 `research-data-visualization` 执行，不新建重复角色。先读本角色 workflow 与 figure_shared；为论文制作/重设计数据图时，在写绘图代码前学习同类已发表图的实际视觉组织。当前用户论文任务继承已要求的十篇范文语料：阅读全文、全部图表的记录来自 paper_exemplar_learning，不另凑十篇，也不能只读摘要/链接。其他独立 plot 任务按用户要求、venue、图型和风险确定最小合适范例范围；局部标签/颜色修正可沿用已验证 brief，不强制任何 plot 都读十篇。

## 1. 从真实图与比较问题学习

确认目标模板/实际印刷尺寸、读者要完成的比较、数据性质与图型。优先同 venue/近年相关顶会的可比数据图；相关性与信息表达质量优先于名气。原文无法访问不算已读；替换候选或标具体 blocker，不用模型记忆重构。

实际打开图所在页/裁剪的像素，连同 caption 与上下文读，绑定 PDF hash、物理页、图号/panel 与阅读回执。学习覆盖来自当前语料所有相关数据图；建 inventory，每张已读/无此图/阻塞都记录，不能只挑漂亮图而漏掉反例。文字提取、图注摘要、网页缩略图或 palette 标签不是视觉阅读。

逐图给位置、观察、作用、误读风险及迁移决定，跨图比较以下八组维度（不适用须说明）：

1. comparison_chart：比较/趋势/分布/关系/组成/权衡任务与图型，为什么用点区间而不是柱图、什么时候不应连线。
2. axes_baselines：线性/log/归一化尺度、基线、单位、零点与范围、可比面板是否同尺度；科学理由不能由审美代替。
3. uncertainty：误差棒/带表示 SD/SE/CI/范围中的什么，n 与独立研究单位；没有报告就记 unknown，不推断。
4. encoding_accessibility：位置、颜色、线型、marker、hatch 如何冗余编码；灰度、对比、色觉差异和最终尺寸是否仍可读。
5. palette_legend：类别/顺序/发散色语义、图例排序/位置、直接标签、跨图同变量是否一致，不能固定突出“ours”来诱导读者。
6. typography：字体、大小、数字精度、单位、上下标、中文/英文标签的层级与可读性。
7. layout_density：留白、对齐、宽高比、数据与辅助网格权重、注释密度、遮挡与极值/负结果是否被掩盖。
8. panels：多 panel 的科学分工、阅读顺序、共享轴/legend/色标、密度与 caption 组织；单图说明为何无需分面。

## 2. 技能选型 → data-visual-design-brief → 实际协作

在已有工具上选择最小补充；读取实际候选 SKILL、相关代码/样式/许可证，记录 commit/hash、适用与拒绝项。可评估 K-Dense scientific-visualization 的语义编码、区间定义、导出/配色筛查，以及 tvhahn matplotlib 的图型/多面板和真实渲染复查。外部样式只是起点，不自动采用固定尺寸、dropna、top-N 截取、平滑/回归、假误差或强制“发现”注释。不得把 palette audit 通过当完整 accessibility 或审美通过。

先形成 data-visual-design-brief：每张目标图的读者问题与本稿 claim ID、真实数据来源/类型、图型与替代方案、变换/单位/轴/基线、误差与缺口、八维具体决定、最终尺寸、EN/ZH 图内翻译方案、多 panel 草图与 caption。每项决定对应范文位置和本稿位置；保留合理不采用的理由，不能只写“高端、清爽、蓝橙色”。范文数据/图像不成为本稿证据，不复制图、图标或无许可素材。

reader 把真实图像观察交给 research-data-visualization；实际执行该角色并获得方案/结果回执，再由主 AI/作者选择方案，记录选择证据。无独立能力可 staged 并说明，但不冒称独立协作。设计批准后绘制并核对 brief→绘图实现→最终尺寸渲染；图内中文翻译保持单位/数值/系列身份与英文版一致。

## 3. 数据科学保真与视觉审美分开验收

冻结源数据/公式/可追溯报告、绘图数组、变换脚本和最终图 hash。区分 measured、simulated、theoretical、reported、synthetic、placeholder：引用报告数值不是本轮实测；公式趋势不是实验；placeholder 不能进入完成态的结果图。caption 必须披露性质及适用范围。

未提供真实不确定性信息时不造 error bars；可追溯汇总报告已给 SD/CI/n 时可忠实绘制并标来源，不要求凭空补原始样本。误差类型、n、独立单位与计算方法不能猜。没有原始分布不能用均值造 violin/boxplot。缺证据列 blocker，按已有真实数值作诚实工作图。

禁止误导性截断长度编码柱图、选择性删除不利点/基线/负结果、未披露缺失/排除/平滑/归一化、把理想或假设数据冒充实测。密度太高优先分面/附图，top-N 或聚合必须符合已确认科学问题并披露全范围，不能为美观挑结果。点/线的非零轴可合理使用，但要上下文与显著披露；log 的零/负值处理明确。

微小差异可能来自运行噪声、测量误差或样本波动；不能用缩窄轴范围/不同面板尺度制造显著优势。没有可核验的不确定性与适用统计分析，不从微小均值差、排序或视觉间隔推断优越；缺 raw/重复试验不能制造 CI/误差棒。将疑点以稳定 finding ID 交 research-review：主张与图位置、delta/单位、数据版本、独立研究单位、重复次数/缺口、噪声来源、需要排除的替代解释、最小重测/配对设计建议与验收条件。审稿角色核验并交实验角色重新设计/执行；图角色不擅自开展实验、补数据或宣称统计检验完成。已有区间也不自动证明 superiority，必须解释区间和比较方法适用性。

独立对最终渲染分别给 data_scientific_fidelity（绘图值、数据性质、尺度、变换、区间/样本、caption、跨语言一致）与 data_visual_design（比较任务是否轻松、八维决定是否改善理解、最终尺寸/灰度/整页嵌入）。各项有图位置、依据、失败/未核项与最小修复；正确但难读不自动视觉 pass，漂亮但数据不诚实必须 fidelity fail。保留可编辑脚本、数据来源、brief、实现映射、before/after 和复现命令，不能只交 PNG 或成功声明。

## 4. 与论文记录接口衔接

paper delivery 顶层 data_visualization_requested 为 bool，由实际请求/图计划决定，不能改 false 绕过本任务。true 时，exemplar_learning.data_visual_design 包含：mode（independent / staged，staged reason 必填且只支持 partial）、reader_actor、visualization_actor、brief、reader_receipt、visualization_role_receipt、selection_evidence、skill_selection（后三类及 brief/回执均 path/sha256）。source_figures 每项 identity、figure_id、page、pixel_read=true、receipt，必须指向十篇已读语料内已覆盖的图；相关图完整清单/未选理由存在 brief，主 AI 核查，脚本不推断原文有哪些数据图。

analysis 为上述八组键，每项 source_location、observation、design_choice；图像来源与观察必须支持迁移判断。charts 非空，每张含 id、comparison_claim（descriptive / superiority）、source_kind、presented_as（须与 source_kind 一致）、source（path/sha256）、chart_type、scale、baseline、exclusions（path/sha256）、uncertainty（available bool、shown bool、definition；shown=true 时还需 evidence path/sha256、sample_size、sampling_unit）。bar 图 baseline 必须 zero；如需展示非零局部比较，选诚实点/线或明确变更图型。sample_size 记录实际 n/范围，不支持时不展示区间。superiority 需 statistical_review（path/sha256）；经验数据还需 available=true 的 uncertainty.evidence。此文件要包含 reviewer 的适用比较/噪声核查，不以一张图或自报 true 替代。脚本只检查声明一致性，不证明输入是真的。

每个 language version 含 data_implementation_map（path/sha256），checks 含 data_scientific_fidelity、data_visual_design。完成态两项 pass，绑定现有 reviewer_snapshot_sha256 与最终稿；partial 可 unresolved 并列 blocker。独立 plot 任务按本流程人工/角色执行记录验收，不为了复用此论文 CLI 强迫生成十论文记录。原有 paper CLI 仍只面向完整投稿交付。

## 5. 已核查候选（2026-10-03；使用时复核实际锁版本）

| 能力 | 实际入口 | 采用与限制 |
| --- | --- | --- |
| 科学数据图与导出/配色筛查 | [K-Dense scientific-visualization](https://github.com/K-Dense-AI/claude-scientific-skills/tree/main/skills/scientific-visualization) | 已读 SKILL、palette_audit.py 和 publication.mplstyle，MIT；采用诚实编码、区间与冗余编码原则，配色筛查只是辅助，不认证审美/可访问性或会议合规 |
| Matplotlib 图型/多 panel 制作 | [tvhahn matplotlib](https://github.com/tvhahn/matplotlib-skill/tree/main/skills/matplotlib) | 已读 SKILL 与 P8-multi-panel 实现，MIT；借鉴最终渲染逐项检查，不采用默认 dropna/top-N、禁止单列、固定间距与强制洞见注释 |

不复制外部代码或主题进本库，不自动安装外部 runtime。具体来源 commit/hash、许可证与测试边界见仓库 docs/data_visualization_sources.lock.json 和 docs/data_visualization_validation.md；离线插件可按此能力表使用现有本地工具，不把外网访问当启动前置。
