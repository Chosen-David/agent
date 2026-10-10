# Baseline 试讲执行与检查

- 执行日期：2026-10-10；owner：baseline_explainer。
- 输入：上级明确指定的 `prompts.md` 中三个独立中文请求；输出限定在本目录。第 2 题的 `answer-2.txt` 仅为测试留档，不作为该用户请求的文件交付。
- 使用技能：`baseline/explain-research-concepts/SKILL.md`；实际阅读其 execution、workflow、visual_explanation_workflow、knowledge_access_workflow、project_document_workflow、result_validation_workflow、result_reuse_workflow、dual_main_workflow 八份直接参考。第一次批量读取输出被截断，随后补读受影响参考的完整内容。
- 读取边界：未读任何其他仓库内容，未修改技能、任务总表、人类指南或其他目录。按上级明确范围，不进行跨仓库历史结果检索、知识库查询或项目治理文件扩读；没有把“未检索”写成“无历史结果”。
- 知识接入：`knowledge_refs=[]`；本次为给定数值与数学恒等式的直接推导。没有必要的外部事实、论文原文或当前技术主张，因此未联网；第 2 题遵守明确的“不查外部资料”。知识库入口未在本次限定材料中提供，未声称调用。
- 作图方式：`sequential_fallback`，由同一 owner 依教学 brief 顺序完成讲解、精确代码绘图和检查。上级明确无须子 Agent，并限制读取为本技能和参考；未另调用 research-figures 技能或宣称独立作图角色。
- 数据性质：题目给定教学权重和矩阵的精确派生；无模型、性能或统计实验。这里的数值复算属于教学算术检查，不是模型实验结果验收；未冒称独立 reviewer 或 `usable-with-scope` 回执。

## 最小教学 brief 与对应关系

| 解释 ID | 步骤 → 面板 | 要解除的误解 / 必须保留的关系 | 类型 |
|---|---|---|---|
| EXPL-001 | S1 → P1 | 同一目标层、query/head 的四个权重；只高亮索引 0、2 | synthetic：给定教学数据 |
| EXPL-001 | S2 → P2 | 相加得 0.65；完整总和 1；余量 0.35 | 精确数值图 |
| EXPL-003 | S1 → P1 | x=e1+2e2；首尾相接 | theoretical：精确几何 |
| EXPL-003 | S2 → P2 | Ae1=(1,0)、Ae2=(1,1)；系数不变，终点 (3,2) | 精确几何图 |

图中文字采用短英文和数学符号，中文解释、caption/alt 在答案中；环境未发现中文字体（matplotlib CJK 字体查询和 `fc-list :lang=zh` 均为空），不冒险产生缺字。

## 实际执行

1. 检查 numpy、matplotlib、PIL 均可导入；运行环境版本写入 `numeric_checks.json`。
2. 执行：`python /workspace/scratch/a2f250bdd851/agent/agent_doc/results/concept-teaching-20261010/baseline/render_figures.py`，stdout/stderr 分别保存到 `render_stdout.log`、`render_stderr.log`；退出码 0，stderr 为空。
3. 脚本中五条断言通过：权重和为 1；候选 mass 为 0.65；目标 top-2 mass 为 0.75；Ax=(3,2)；按两列组合与矩阵乘法相同。精确值见 JSON；softmax 以答案中的代数消去作一般证明，未用一个数值样例替代证明。日志中的断言条数曾写为六，核对代码后更正为五并重跑，计算与图形未改动。
4. 保存两幅 PNG、可编辑 SVG、同内容 720 px 预览以及可重跑的 Python 源。主 PNG：attention_mass 1500×690；linear_basis 1500×870。
5. 使用 `view_image` 实际打开 `attention_mass_720.png` 和 `linear_basis_720.png`：柱高与 0.50/0.25/0.15/0.10 标签一致；蓝色斜线冗余区分候选集合；合并条比例 65/35；线性图基箭头、两步虚线路径与 (1,2)/(3,2) 终点一致；标签可读，无关键文字裁切和遮挡。英文图注需中文答案配合。没有只凭生成成功声称看过图片。

## 交付与限制

- 完整回答分别在 `answer-1.md`、`answer-2.txt`、`answer-3.md`。第 1、3 题已含宿主格式的 PNG 图片链接与中文说明；是否已由最终上级回复交付给用户、用户是否看到，未在此宣称。
- 编辑源：`render_figures.py`、`attention_mass.svg`、`linear_basis.svg`。
- 语义/数值与视觉均做了本 owner 自查；独立验收由上级决定和执行，本记录不自称独立。
- 不引用不存在的论文定义。第 1 题在本题采用“所选位置占完整注意力分布的总权重”的定义；若另有自定义 top-k 比率，那是另一指标。
- SVG 为可编辑文本图形，重新渲染需要 DejaVu Sans 和 matplotlib 的数学字体；脚本使用本机现成字体，无额外字体下载。
