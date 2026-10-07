# CAR-LoRA：量化迁移结果与训练预算混杂

## 问题触发

adapter portability；compression-aware LoRA；CAR-LoRA；量化迁移

## 精确结论与证据身份

ICLR 2026 的实验支持有限量化方案下的 adapter 迁移候选；训练轮数不同且 layer skipping 退化，不能据此承诺任意未来模型可用。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- models: Llama-3.1-8B Mistral-7B Gemma-2-9B
- compression: INT8 FP4 NF4 structured pruning layer skipping
- metric: reasoning benchmark accuracy

## Observation / 实验 / 源码定位

- §4.1 基线训练 5 epochs、CAR-LoRA 20 epochs，不是等训练预算比较。
- §4.2 Table 1：Llama-3.1 GSM8K 的 BF16 LoRA 38.9%，CAR-LoRA NF4 38.1%、layer skipping 31.1%。

## 可算例子与任务映射

同样 5 vs 20 epochs 是 4 倍训练轮数；不测每步成本时也不能声称恰好 4 倍 GPU 时间。

## 失败情形与不可推广范围

- 模拟 continued pretraining 不等于任意厂商未来版本；需结构兼容与迁移质量验收。
- 存在训练预算混杂，不能把全部收益归因于压缩感知机制。

## 最小迁移验证

- 对目标基座/量化做小 held-out 测试。
- 若声称方法优越，补等训练预算对照；只做迁移决策时先不重做全论文。

## 来源定位与尚未验证项

- [§4.1; §4.2 Table 1; §4.3 Table 2; temporal evolution experiments](https://proceedings.iclr.cc/paper_files/paper/2026/file/72491c8fd75d85b4b5adf561a15bcd2c-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
