# 科研图共享约定：证据、设计与验收

适用于数据可视化、流程/架构示意及混合图。专业任务只读本文件和对应工作流；工具选型时读 [工具后备](figure_tools.md)，需要模式/完整模板时读 [输入说明](figure_inputs.md)。这些是任务规范，不是程序已执行的 schema 或自动路由器。

## 1. 共同底线与最短路径

- 以读者问题、用户约束和现有材料确定范围；不预设学科、固定 Figure 1–5、baseline 或主张方向。单图不扩为整篇重做，不要求先搬动项目目录或填表。
- 科学忠实是硬门槛，美观与精美是独立交付要求。不得为好看改数据、删不利结果、补误差/显著性、虚构节点/边或证据。装饰不能掩盖未知。
- 区分 conceptual / measured / simulated / theoretical / literature / qualitative；拟议方案标 proposed，非量化示意标 schematic，教学/工具测试合成值标 synthetic 并隔离，不能混入论文结果。
- 保留原始数据/素材只读和已有图版本；追踪来源、版本/哈希、处理、主源、实际生成产物。关键未知只阻塞依赖它的 panel，继续独立部分。
- 既有分析方案与用户指定语义优先。不自动做新实验、大规模仿真、统计模型、外传私密研究材料、安装新权限或发布；发现必要变化先按主调度决策门禁对齐。
- 同一项目沿用已验证 Skill 和风格锁；新项目先检查可用能力，再按需求有限选型。实际读取候选 SKILL.md、依赖、样例，不凭名字推断能力；离线可用已有代码并标 offline_fallback，不假装调用未安装工具。
- 第三方审美预设不是科学规则；其强制字体、固定期刊尺寸、必加结论注释、必找一个问题或固定 legend 位置与任务冲突时不照搬。只报告实际观察的问题，原图已合格可保留。

项目新指令先按 [既有结果检索与复用](result_reuse_workflow.md) 查 `agent_doc/results/` 的相关数据及当前独立验证；来源/条件不匹配时不拼接旧结果或悄悄补造实验。

对当前项目测试/实验产生的数据，先按 [结果验证闭环](result_validation_workflow.md) 消费带 `required_result_refs` 的 usable-with-scope 结果；pending、invalid 或代码/数据版本过期时不生成依赖结论图。数据格式检查、重新绘图或视觉 QA 不替代实际代码与数据的独立验收。文献原图/纯概念示意按其来源说明，不伪造本地实验验证。

## 2. 图与 panel 的交接契约

沿用已有 FIG / FIG-T ID 和 run ID；专业拆分不重编号历史结果。最小单图记录可合并进 figure_notes.md，多图才分开计划、style、manifest 和 QA。字段只填适用项，不造未知值。

```yaml
id: fig_unique_id
asset_id: null                 # 保留旧 FIG ID；区分同一内容的论文图/幻灯片等资产
usage: null                    # paper / slide / teaching / other
review_binding: {}             # 主源、导出、预览及承载文件路径/sha256，承载页码
role: auto                     # concept / method / design / result / analysis / synthesis
route: null                    # data_visualization / diagram / mixed / asset_only / clarify
reader_question: null
takeaway_or_purpose: null       # 解释目的或有证据的结论，不预写“优于”
evidence_type: null             # conceptual / measured / simulated / theoretical / literature / qualitative
source_refs: []                 # 输入路径、版本/哈希和页/字段/代码位置
evidence_status: unresolved     # verified / unresolved
owner: null                    # 整图唯一整合负责人
panels: []                     # 每项含 id、route、owner、source_refs、evidence_type、status
data_transforms: []             # 如适用，记录筛选、聚合、归一化等
analysis_definition: null
semantic_contract: {}          # 如适用，节点/边/方向/边界/符号及依据
visual_encoding: {}             # 变量/对象 → 颜色、位置、形状、线型
dimensions: {}                  # 最终物理尺寸、panel 尺寸、嵌入比例、规格来源
readability_profile: {}         # 用途阈值及依据，有效字号/上下标字号/线宽；未知标 provisional
style_ref: null                 # 共享字体、层级、色板、留白、图例、panel 标号
primary_skill: null
editable_source: null           # 每 panel 一个主源；整图另有拼版源
build_command_or_steps: null
outputs: []
caption_points: []
missing_inputs: []
qa:                            # 每项记录状态 + 证据/检查产物；not_applicable 需理由
  scientific: pending
  numerical: pending
  semantic: pending
  visual: pending
  technical: pending
  final_carrier: pending        # 正确资产在实际承载页/显示环境中的检查
  reproducibility: pending
  submission: unverified
status: draft                  # draft / ready-for-review / submission-spec-verified
```

asset_id 与 usage 绑定主源、最终导出、预览及承载文件的路径/sha256、页码、物理尺寸和嵌入比例；无分页载体时记录实际显示环境。最小单图可在 figure_notes.md 记录，不强制另建文件。换图、改版本、尺寸或嵌入比例后，受影响的 QA 失效并复验；同主题的不同用途资产不能互相代验。

主源、数据快照与 caption 对应同一版本。caption 说明目的、panel、符号与来源；样本量、独立重复单位、误差定义、尺度、参数和文献编码只在适用时交代。概念图不强塞统计信息，理论数值例子不替代证明。

## 3. 设计系统：美观需要主动设计

1. 先定用途与最终物理尺寸。读取用户模板或目标 venue/year 官方规格；不照抄第三方固定值。未定时记录 provisional 宽度/字体，继续草稿，但不声称投稿合规。嵌入后有缩放则按实际比例复核字号和线宽。
2. 写简短设计说明：主要阅读顺序、重点、布局、字体层级、颜色语义、图例位置、留白分配。记录可审阅选择，不输出私密思维链。复杂总览可比较两种低细节布局；小修无需生成多个方案。
3. typography：统一字体族与数学符号风格，少量明确字号/字重层级，核对中文、负号、上下标和字体嵌入。图注已有标题时勿让图内大标题压过数据；不能靠不断缩小字体解决拥挤。
4. palette：有限且有语义的配色。类别用离散色；单向量值用顺序色；围绕真实中点的偏差才用发散色。同一对象跨 panel 保持身份，保持前景/背景可辨；不用无意义彩虹或装饰性渐变暗示量值。
5. accessibility：颜色配合线型、marker、形状或文字，避免只靠红绿区分。实际看灰度预览；能做色觉模拟时补做并记录，灰度可辨不等于已经通过色觉模拟。
6. layout：有意识地控制网格对齐、间距节奏、视觉层次、边距与留白。为图例/注释预留空间，不遮重要数据或连线。保留有意义的比例，删掉不帮助理解的边框、阴影、3D 和装饰。
7. 参考图只借鉴设计，不借其数据、结论或未核实结构。根据任务适配，不把某一外部 Skill 的个人风格统一强加给所有论文。

## 4. 实际渲染与视觉质量 rubric

执行 渲染 → 实际读图 → 记录具体问题 → 修改 → 重渲。已有图先看 before 再编辑，交付前看 after。通常最多三轮，通过即停；若仍有问题保留 draft，明确剩余项，不以迭代次数代替通过。

每一轮按 review_binding 核对实际打开的资产，再记录预览路径、最终尺寸/嵌入比例、检查者/工具、具体观察和修正。屏幕放大看细节后，还要按用途在最终实际尺寸与承载环境中检查；paper 需整页嵌入预览；文件声明 300 DPI 不能证明清晰，程序无错不能证明美观。

| 检查维度 | 应有证据与通过条件 |
| --- | --- |
| 科学/数值/语义硬门槛 `evidence_preservation` | 对照源数据、公式或结构逐项核验；不遗漏、反转、虚构；数值与处理可复算 |
| 层级与阅读顺序 | 重点清楚，正文/辅助标注权重有区分，读者知道从哪里看起 |
| 字体与最终尺寸 `final_size` / `typography` | 实际尺寸能读，无缺字、拥挤、遮挡或裁切；不只看编辑器放大图 |
| 配色与可访问性 `palette` / `accessibility` | 颜色有含义，对比清楚，冗余编码和灰度仍可识别对象 |
| 布局与留白 `whitespace` | 对齐、间距与 panel 比例有意图；画面平衡，不松散也不挤满 |
| 图例与注释 | 位置贴合对象，说明必要信息，不压数据、不混淆箭头，不重复堆砌 |
| 完整性与技术 | 检查真实最终导出格式、字体、外链资源、有效分辨率、SVG ID/marker/clipPath、比例 |
| 最终载体 `final_carrier` | 实际尺寸单图、整页嵌入及灰度预览对应同一资产版本；非论文用途按真实显示环境检查，记录适用性 |
| 复现 | 输入定位、版本、主源、重绘/拼版步骤齐全；手工步骤如实记录 |

有效字号与线宽按嵌入比例核对，单独检查上下标及辅助标签。readability_profile 的阈值来自任务用途、用户模板或已核实规格；无依据时标 provisional 并实际读图，不硬设“顶会统一规范”。满足数字阈值仍须人工/实际视觉审阅，不能保证可读。

科学语义、几何技术、阅读美学与最终载体分别给出结论，不可相互抵消。关键词/节点存在不等于关系正确；XML、嵌字、出界或脚本检查通过不能自动授予视觉通过。下列负例必须退回相应检查：

| 情境 | 判定与恢复条件 |
| --- | --- |
| paper 任务只查看 slide 或放大的 PNG | final_carrier=needs_revision；打开绑定的论文页和实际尺寸图复验 |
| 文件哈希、页码或嵌入比例与审阅记录不符 | 受影响 QA=needs_revision；更新绑定并检查当前产物 |
| 节点/关键词齐全但箭头起止关系错误 | semantic=needs_revision；修正关系并复核真实端点 |
| 语义正确、无乱码，但核心机制只靠长段文字解释 | visual=needs_revision；以可见结构/编码表达机制并重新读图 |
| 仅累计审读次数、模板化赞同或技术 pass | visual=needs_revision；补实际图的定位观察与判断 |

美感维度逐项记 pass / needs_revision / unverified，并给具体观察，不计算伪精确“审美总分”。数值或语义失败不能靠审美补分；视觉未实际检查不能为 pass。未满足项不自动退化为“仅能打开就交付”。无法实际查看图片时报告“视觉检查未完成”。已到验收阶段仍未完成的适用项记 needs_revision，整体保留 draft；unverified 用于明确记录尚未验证，不能放行。

ready-for-review 需适用的科学、数值/语义、视觉、技术、最终载体、复现项通过；submission-spec-verified 还需核对真实投稿规范，两者均不是外部学术认可。未知规范可留 submission=unverified 而完成通用图草稿。

## 5. 拼版、专业素材与交付

纯数据多 panel 优先同一个绘图工程；混合素材由指定整图 owner 统一拼版。先约定各 panel 尺寸、共享 style 与 caption，再交付带来源的真实素材。缺素材用明确 draft 占位，不能把占位图当完成结果。

整合后重新渲染验收：字体缩放、相对尺度、色标可比性、图例与编号、SVG ID/marker/clipPath 及资源路径。不可将整张矢量数据图截图拼版；保留各 panel 主源、拼版源。转文字路径仅用于兼容发布副本，另留可编辑文本主源。

图像/空间/领域对象优先保留经验证的原工具与专业源文件。记录裁剪、旋转、对比度、色标、投影、视角等适用处理；对照保持可比，尺度条来自真实校准。未知尺度不估造，不用生成图替代显微/照片证据，不把插值说成恢复细节。专业工具不足时只做可完成的标注/版式，明确缺口。

交付实际主源、目标格式、PNG 预览、caption、简短设计/证据/QA 记录、可复现命令或手工步骤及未解决项。保留实际工具版本；不为单图生成空文档。新数据或审稿意见只更新依赖的 panel/caption，方法变化时核查旧结果仍适用。
