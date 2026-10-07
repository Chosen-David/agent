# DoRA：幅值/方向观察与额外训练成本

## 问题触发

DoRA magnitude direction；LoRA capacity；权重方向；weight decomposition

## 精确结论与证据身份

ICML 2024 的权重分析与任务实验支持把幅值和方向分开适配；分析里的相关趋势不能证明因果或普遍最优。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- method: magnitude plus low-rank directional updates
- models: LLaMA LLaVA VL-BART in paper
- metric: downstream task quality

## Observation / 实验 / 源码定位

- §3 Figure 2 比较 FT/LoRA 的幅值与方向变化；§5 表格比较下游结果。
- §4 的归一化方向和可学习幅值能够合并推理权重，但训练计算/内存须单独考量。

## 可算例子与任务映射

一个方向向量归一化后再乘独立幅值，可保持方向不变而调整幅值；这说明表达形式，不证明任务收益。

## 失败情形与不可推广范围

- 不能由几层权重趋势推出所有模型 LoRA 失败机制。
- 同 rank 不一定同训练成本；应同时比较参数/显存/耗时和质量。

## 最小迁移验证

- 核对列/行方向、范数梯度与 merge 结果。
- 做一个固定预算 LoRA/DoRA 对照；不重复论文全部权重趋势实验。

## 来源定位与尚未验证项

- [§3 Figure 2; §4; §5 task tables](https://raw.githubusercontent.com/mlresearch/v235/main/assets/liu24bn/liu24bn.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
