# 作图材料、模式与可选输入模板

与 [共享约定](figure_shared.md) 配合使用。不是必填问卷；已有材料够用就直接推进。

## 3. 从现有材料选择起点

用户不必先整理成固定目录，也不必填写全部模板。给出论文、Idea、数据、旧图或文件夹中的任意一种，Agent 先盘点，再决定哪些阶段可以执行。已有项目结构优先，不为适配本文而移动原始文件。

### 3.1 任务模式

| 当前材料 / 需求 | 运行模式 | 可以直接完成 | 暂不具备条件时如何处理 |
| --- | --- | --- | --- |
| 只有 Idea 或研究计划 | `concept` | 问题示意、概念框架、拟议方法、研究流程、待验证实验的图规格 | 标注 proposed；不生成虚构结果图 |
| 有方法、公式或代码，没有实验结果 | `method` | 方法流程、系统结构、算法步骤、理论关系、实验设计示意 | 代码与文字冲突先记录，不自行判定哪版正确 |
| 有原始或整理后的数据 | `results` | 数据审计、合适的数据图、caption、复现脚本 | 未知字段/单位只阻塞依赖它的 panel |
| 已有论文全文和数据 | `full-paper` | 对照论证结构规划必要图、补齐图文关系、统一全篇风格 | 保留已有编号；新增和重排说明对应关系 |
| 已有图和绘图源码 | `polish` | 直接渲染现状、按最终尺寸精修、比较前后效果 | 不无故重做研究叙事、图型和统计分析 |
| 只有截图、PNG 或 PDF 图，没有源码 | `reconstruct` | 检查可读性；按可确认内容重建结构，或恢复可提取的矢量元素 | 不把估读曲线当原始数据；精确结果重绘需数据 |
| 一批风格不一致的图 | `harmonize` | 统一尺寸、字体、图例、颜色语义、panel 标签 | 对不可编辑的图说明可修改边界 |
| 投稿修改或新增实验 | `revision` | 建立意见—图—数据依赖映射，修改受影响内容 | 不重新生成无关图；旧结果不自动代表新方法 |
| 单张图或某个 panel | `single-figure` | 走所需最短路径，完成该图及最小复现记录 | 不创建无关的整篇论文文档体系 |

支持组合模式，例如 `full-paper + polish`。`auto` 表示 Agent 根据当前材料选择模式并说明理由。

### 3.2 论文类型与表达对象

“通用”体现在统一规划与验收，同时允许不同论文走不同绘制路线。下列类型可以同时出现，不强制归类为一种。

| 论文内容 | 常见表达对象 | 首选路线 | 不能默认的内容 |
| --- | --- | --- | --- |
| 算法、机器学习、软件与系统 | 方法、结构、流程、性能、误差分析 | SVG/TikZ + 数据绘图 | 所有论文都有 baseline、消融或速度指标 |
| 理论、数学与形式化方法 | 定义关系、几何构造、证明结构、函数性质 | TikZ/SVG；必要时公式计算与绘图 | 数值示例等于理论证明 |
| 实验科学、工程、材料等 | 装置、样品、过程、响应、测量结果 | SVG 示意 + 数据图 + 原始图像 panel | 每个测量点都是独立重复 |
| 仿真、数值计算、计算科学 | 边界条件、场分布、轨迹、参数扫描 | 已有领域渲染器导出 + 通用排版 | 仿真输出是实测数据，网格单元是独立实验 |
| 观察、调查与社会科学研究 | 样本构成、变量关系、效应与不确定性 | 数据图 + 研究设计图 | 相关关系表示因果，重复观测相互独立 |
| 综述、文献计量与证据综合 | 分类体系、证据分布、时间趋势、检索筛选过程 | SVG/TikZ + 来源明确的统计图 | 检索计数、分类和效应量可以凭文献摘要补齐 |
| 定性研究、案例研究、人文研究 | 概念、主题、过程、论据与案例关系 | SVG/TikZ + 可追溯的文字/表格 panel | 主题可以随意量化，视觉连线自动构成因果 |
| 图像、地理空间、结构或三维对象为核心 | 样本图、地图、结构、场景、局部放大 | 原有专业工具导出 + 注释与拼版 | 通用 Skill 能替代专业几何、测量或领域模型 |

化学结构、分子、解剖、地图投影、复杂三维场等内容，优先保留经验证的领域工具和源文件。通用 Agent 负责输入盘点、版式、标注、组合和 QA；需要新的领域工具时先查官方文档，不能编造其命令或宣称通用 Skill 原生支持。

## 4. 准备输入：最简说明和完整模板

### 4.1 最少只需要这一段

```text
请按对应专业工作流和 figure_shared.md 处理我的论文作图任务。
材料位置：[论文/Idea/数据/已有图/代码的路径，或“本次上传的文件”]
本次范围：[单图 / 指定几张图 / 全篇配图 / 仅精修已有图]
目标用途：[会议或期刊与年份；未定可写“通用投稿草稿”]
我最希望读者理解：[一句话；不确定时请你结合材料提出]
必须保留：[已有图号、配色、术语或布局；没有就写“无”]
请先识别任务模式与材料缺口，再完成所有具备条件的图。
```

没有目标 venue 时继续做通用草稿；没有数据不妨碍概念图；没有参考图不妨碍原创设计。只有影响科学含义且无法从材料判断的缺口才需要提问。

### 4.2 推荐目录，不强制迁移

| 路径 | 用途 | 什么时候需要 |
| --- | --- | --- |
| `inputs/research_brief.md` | 问题、研究对象、方法、结论边界、图需求 | 没有完整论文时尤其有用 |
| `inputs/manuscript/` | PDF、LaTeX、Word 或已有正文 | 全篇规划或图文一致性检查 |
| `inputs/figure_brief.yaml` | 任务模式、尺寸、风格、产物配置 | 多图项目或固定出图流程 |
| `inputs/references/` | 风格参考及来源 | 可选 |
| `inputs/source_assets/` | 原始照片、实验图像、领域工具导出等 | 需要图像或专业图形时 |
| `data/raw/` | 不改写的源数据 | 有定量图时 |
| `data/processed/` | 由可追溯转换产生的数据 | 需要转换时 |
| `figures/src/` | 可编辑图源、绘图脚本、拼版脚本 | 正式产出时 |
| `figures/drafts/` | 初稿、布局比较、未完成 panel | 尚未通过检查时 |
| `figures/final/` | 检查完成的输出候选 | 检查通过时 |
| `figures/qa/` | 最终尺寸、灰度及局部预览 | 视觉检查时 |
| `docs/` | 规划、数据来源、风格、caption、QA 与复现说明 | 按任务复杂度合并或拆分 |

单图任务可将计划、来源、caption 和 QA 合并为一个 `figure_notes.md`。完整论文再采用详细的多个记录文件，不为流程本身生成空文档。

### 4.3 `research_brief.md`

```markdown
# 研究与作图说明

## 研究问题和研究对象
[这项工作研究什么？读者需要什么背景？]

## 论文类型与研究阶段
[理论 / 方法 / 实验 / 仿真 / 观察 / 综述 / 定性 / 混合；计划或已完成。]

## 方法、框架或研究设计
[实际步骤、对象关系、条件、输入输出；不适用的项略去。]

## 希望回答的问题
- Q1: [...]
- Q2: [...]

## 已有证据和对应位置
[数据、公式、证明、文献、代码、图像或案例路径。]

## 已支持的结论与待验证假设
[分别列出；没有结果可以明确写“尚未验证”。]

## 本次图的范围
[解释概念 / 展示方法 / 呈现结果 / 分析机制 / 综述归纳 / 精修现有图。]

## 目标读者、投稿位置与限制
[领域、venue、版面、语言、需要保留的术语、编号和样式。]
```

### 4.4 `figure_brief.yaml`

```yaml
project: my-research-paper
task_mode: auto                 # 支持 auto 或第 3 节中的模式
scope: requested_figures        # single_figure / requested_figures / full_paper
paper_types: []                 # 由材料确定，可多选
research_stage: auto
venue: null                     # venue 名称与年份；未定保持 null
figure_language: auto           # 按用户、正文或 venue 确定
notes_language: zh

inputs:
  research_brief: null          # 填真实路径；不要强制改名
  manuscript: []
  data: []
  code: []
  assets: []
  existing_figures: []
  references: []

intent:
  reader: null
  questions: []
  required_figures: []          # 不预设每篇论文都要 Figure 1–5
  preserve: []

design:
  diagram_backend: auto         # svg / tikz / existing / auto
  data_backend: existing_or_python
  layout: auto                  # 不假定所有期刊都是双栏
  width_source: provisional
  target_width_mm: null         # 优先从模板或用户要求获取
  font_family: auto
  base_font_pt: null
  palette: auto
  semantic_colors: {}           # 按实际对象填写，非固定 method/ours 配色
  panel_label_style: auto

evidence:
  allow_synthetic_results: false
  allow_labeled_schematic: true
  analysis_plan: null           # 已有分析方案的路径，如适用
  source_data_read_only: true

skills:
  discovery: at_project_start  # 新项目或显式更新时重新检索
  prefer_locked_for_continuation: true
  fallback_catalog_date: 2026-10-01
  require_verified_replacement: true
  registry: docs/skill_registry.yaml

execution:
  allow_new_experiments: false
  allow_new_simulations: false
  allow_external_material_upload: false
  allow_network_for_discovery_and_guidelines: true
  visual_revision_limit: 3

outputs:
  editable_source: true
  publication_format: auto      # 依 venue 与图的类型决定
  preview_format: png
  preview_dpi: 300              # 预览默认值，不等于所有投稿图的要求
  captions: true
  reproducible_build: true
```

这些是 Agent 的任务配置字段，不是第三方 Skill 的官方 API。未填写项允许合理推断并记录；不推断不存在的实验结果、统计方法或结构细节。

### 4.5 数据与证据说明

每张图只填写适用项：来源路径与版本、变量定义与单位、研究对象、分组/条件、采样或测量方法、时间点、独立实验单位、重复/配对/嵌套关系、排除规则、转换与聚合、分析方案、缺失与不确定性。

来源不仅是 CSV。公式对应假设与定义；综述图对应检索记录和文献编码；定性图对应主题定义和支持材料；图像对应样本、采集条件和尺度；仿真图对应模型、初边值与参数。没有定量数据的论文不应被强制套入数据分析步骤。

