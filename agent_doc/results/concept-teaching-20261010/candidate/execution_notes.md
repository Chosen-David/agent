# 执行与检查记录

- Owner：candidate_explainer；日期：2026-10-10；目标：固定的三题中文概念试讲。全部写入仅位于本目录。
- 输入：上一级 `prompts.md`；输入 SHA-256 见 `arithmetic_checks.json`（生成时读取）。没有论文输入，未声称原文锚点或论文特定指标。
- 实际读取：指定 explain-research-concepts 的 SKILL.md，以及其 `execution.md`、`workflow.md`、`knowledge_access_workflow.md`、`project_document_workflow.md`、`result_reuse_workflow.md`、`result_validation_workflow.md`、`explanation_patterns.md`、`visual_explanation_workflow.md`。第一次合并读取部分输出截断，随后完整重读 project_document、result_reuse 和 result_validation 三个文件。
- 主控随后通知 execution.md 的链接导航发生可移植性修改，不改变教学指令。本次首次读取发生在该通知之前；未在首次读取时取得文件哈希，因此不声称末尾哈希代表初读版本。
- 按派发的盲测限制，没有读取其他仓库内容、结果、指南、任务清单或公共知识库。未执行旧结果复用查询；原因是本次明确限制跨结果读取。未更改 Skill 或其他路径。
- `knowledge_refs: []`；未查询知识库，状态为未接入（本次授权输入不包含语料），不假称无命中。三题基于给定数据、定义和直接代数推导；没有依赖外部时效事实，未联网。第2题明确要求不用外部资料，照办。
- `sequential_fallback`：主控明确要求无需子 Agent，本 owner 顺序完成图解 brief、绘图、数值复算和图片阅读；没有声称调用独立作图角色。

## 图解 brief 与对应

| ID | 步骤 / 面板 | 读图目标 | 数据和边界 |
|---|---|---|---|
| EXPL-001 | S1 → P1 | 从完整概率条中找出 token 0、2，并把其长度相加为0.65 | 给定完整分布，固定目标层/query/head；教学数据，无单位；不是模型测量 |
| EXPL-003 | S1 → P1；S2 → P2 | 比较相同组合系数在基向量变化前后的结果 | 给定精确整数矩阵，等比例坐标；理论几何图，无模型测量 |

完整 caption、alt text 和颜色/箭头说明在 `answers.md`。图采用英文短标签与数学符号，正文中文解释对应含义；系统 `fc-list :lang=zh family file` 返回空，因此未使用缺失的中文字体。

## 实际执行

1. Python 检查确认 NumPy/Matplotlib 可用，`fc-list` 可用；无安装新依赖。
2. 用 apply_patch 写入 `render_figures.py`；执行 `python /workspace/scratch/a2f250bdd851/agent/agent_doc/results/concept-teaching-20261010/candidate/render_figures.py`，退出0，生成 SVG、PNG、720px 预览和算术记录。
3. 用图片工具实际打开 `attention_mass_720.png` 和 `linear_map_720.png`，完成下述视觉检查。
4. 删除图源中未执行的条件表达式后，再执行同一脚本，stdout 保存为 `render_stdout.log`，退出0；图的有效绘制参数未改变。
5. 用 apply_patch 写入全文和记录，并修正 aligned 公式的显示数学定界符；无第2题独立用户交付文件，答案中该题保持两句、无图。

## 已执行检查及范围

- 数值：代码实际验证完整权重和为1、选中和为0.65、top-2和为0.75、相对比值0.8666666667、Ae1=(1,0)、Ae2=(1,1)、Ax=(3,2)，以及基向量展开等式，断言全部通过。精确输出和软件版本见 JSON/log。
- 一般性：softmax 恒等式使用共同因子消去；线性变换的解释以线性性和基展开证明一般关系，未用单个数值例子代替证明。非线性反例 F(s,t)=(s+t+st,t) 的基向量输出相同，F(1,2)=(5,2)，手算复核。
- 视觉：实际查看720px预览；概率条四段长度与值匹配，完整总体保留，token 0/2蓝色并有in S文字冗余；两幅几何图轴尺度相同，蓝/橙基向量与虚线副本、深色结果箭头一致，标签可读且无裁切。线性图下方轴名与图例较近，但没有遮挡。
- 这是生产者自检，不是独立审查，不标 independent pass 或 usable-with-scope。没有实验、性能、精度或真实学习收益结论；固定教学数值复算不是模型实测。若主控将这些试讲样例用于技能优劣结论，须由独立审查者验收。
- PNG/SVG 已渲染且预览已实际读取；当前为仓库验证归档，未向最终网页用户发送独立图片附件，不声称用户已经看到。

## 交付与复现

完整答复：`answers.md`；图源：`render_figures.py`、`attention_mass.svg`、`linear_map.svg`；渲染：同名 PNG（1440×608、1600×848）及720px预览（720×304、720×382）；复算：`arithmetic_checks.json`、`render_stdout.log`。

复现命令：在本目录运行 `python render_figures.py`；脚本读取固定上一级 prompts.md 以记录其实际哈希。
