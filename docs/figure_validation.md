# 作图职责拆分：实现与验证

日期：2026-10-03 UTC。实现基线：`db19c5f117070d1451e65a089f2f4d768362ac62`。保留并发的旅行契约与主调度反思增强。本文描述仓库工作流/技能交付，不声称宿主已安装或后台多 Agent 服务已运行。

## 1. 对齐范围与实现

status=aligned。范围是将论文数据可视化与流程/架构示意分为两个专业入口，保留旧 `research-figures` 兼容路由和混合图负责人，共用证据、主动美学设计、最终尺寸 QA 与交付契约。数据图须美观，架构图须精美；科学忠实不能被审美替代。不新增模型服务，不修改用户账户权限，不安装外部作图软件。

- [数据可视化](../workflows/data_visualization_workflow.md)：数据审计、图型/编码选择、审美设计、数值保真、复现与精修。
- [流程架构图](../workflows/diagram_workflow.md)：节点/边/边界语义、层级构图、连接线路由、精美设计与语义保真。
- [兼容入口](../workflows/figure_workflow.md)：按证据/表达目的路由，混合 panel 交接、指定整图 owner 并重新验收。
- [共享核心](../workflows/figure_shared.md)：来源、状态、Figure Spec、设计系统、分项 QA、领域素材和交付。
- 原流程的工具选型/安装后备与跨学科输入/模式模板分别保留在 [figure_tools.md](../workflows/figure_tools.md) 和 [figure_inputs.md](../workflows/figure_inputs.md)，按需读取，不在轻量入口重复全部正文。

研究插件升级 1.2.0，现有 11 个技能。三个作图技能和科研总入口携带包内完整后备；独立安装专业技能不用依赖仓库外路径或联网读取兄弟技能。规范主源是 `workflows/`；包内副本逐字同步，由测试检查，不手工维护分歧版本。普通文件链接已覆盖包内闭合。

## 2. 外部原始 Skill 核查

本次实际阅读以下原始入口，未安装/运行其代码。记录当次默认分支提交用于溯源，不宣称推荐这些 commit 永远最好；运行时仍应按任务选型和锁定。

| 来源 | 核查结论与本仓库处理 |
| --- | --- |
| [scientific-svg-figures](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/scientific-svg-figures/SKILL.md) | 明确图类别、画布/分区、文字与连线、实际尺寸及 SVG marker 检查；用于示意职责后备，小修无需完整重设计 |
| [scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill/blob/43098ddb9e6a6d142218540c114f9ed38922fc42/SKILL.md) | 明确只做数据图、不做架构示意；包含剖析、图型选择和视觉闭环。其固定期刊参数/一刀切图型规则不直接当科学标准 |
| [matplotlib](https://github.com/tvhahn/matplotlib-skill/blob/ec4a4b470aa7c83b6379e2fc9d9bf612ccb24072/skills/matplotlib/SKILL.md) | 当前默认分支 master，个人风格与样例绘制/QA 并存；只按任务借鉴，不强制固定字体/主题或必加结论注释 |
| [beautify-chart](https://github.com/preordinary/science-plot-formatter/blob/750c6c1834c833c2607e5913daea76497433dc6e/.claude/skills/beautify-chart/SKILL.md) | 既有 Matplotlib 脚本的前后渲染与尺寸精修；明确保留数据、颜色、线型、轴限和既定构图，不把它当重新设计所有科学编码的工具 |

本仓库采用的是职责和验收边界，不复制外部 Skill 全文。第三方宣传、条款和审美预设不作为经实测的质量结论；不能把读了入口说成工具集成已经成功。

## 3. 测试与 taskset 的意义

`tests/test_figure_contract.py` 检查：规范/包内快照一致、独立技能链接闭合、新角色与兼容入口路由/元数据、关键证据与视觉门槛。

`tests/fixtures/figure_tasks.json` 包含 20 个规范情境，覆盖真实数据/不确定性边界、理论曲线/示意曲线、实测热图/张量示意/歧义输入、节点/箭头语义、混合图、真实专业图像、辅助插画边界、截图重建、精修与越界修改。每例写明预期角色、交付、不得做的动作和审阅依据；这是人工/模型评测待用 taskset，不是自动生产路由器。

少量可执行 fixture 检查验证“指定的不变量可以发现人为注入的错误”：独立运行均值与单位保留、理论公式值、样式改变不改变数值/语义投影，节点/边、颜色身份、单位/变换等修改可被样例 oracle 拒绝。这些不是任意绘图脚本验证器，也不能证明模型不会犯错。

美学 rubric 覆盖 final_size、palette、typography、whitespace、accessibility、evidence_preservation；真实任务必须提供渲染和具体观察，未看图就 unverified。测试检查 rubric 的存在与明确要求，不自动判图是否漂亮。

## 4. 执行结果与未验证项

执行命令：

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python -m compileall -q tests
git diff --check
```

Python 3.12 环境本轮实际运行：根目录 38 项通过（含新增图表 14 项），阅读器应用 3 项通过；compileall 与 git diff --check 通过。Skill Creator quick_validate 对两个新专业技能和旧兼容入口均通过（只验证格式，不证明行为质量）。未进行宿主技能安装、付费模型端到端出图、真实论文数值/视觉评估或外部工具集成。没有受控相同任务、模型、预算的前后对照，不声称拆分后质量/成本/速度已经提升。

后续真实验证：从 taskset 选数据、架构、混合与边界案例，在同一输入/模型/预算下执行旧版与新版；审阅源数据/拓扑、实际尺寸渲染、可复现性、角色交接和具体美学维度，记录失败/未完成项。严格分开确定性回归、单次成图观察与模型质量评估，不以多数模型同意替代证据。
