# QLoRA：存储 dtype 与计算 dtype 分离

## 问题触发

4bit finetuning；NF4 double quantization；QLoRA memory；paged optimizer

## 精确结论与证据身份

NeurIPS 2023 报告 65B 模型单 48GB GPU 微调可行；依赖量化冻结骨干、LoRA 和具体训练设置，不是任意 65B 训练均可放下。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- method: NF4 frozen backbone plus LoRA
- model: 65B model in paper
- metric: finetuning memory and task quality

## Observation / 实验 / 源码定位

- §3 区分 4-bit 存储和 BF16 计算，double quantization 减少量化常数，paged optimizer 应对峰值。
- §4 的消融考察 NF4、double quantization 和 LoRA 配置；对 chatbot 的评级存在评测器局限。

## 可算例子与任务映射

65B×4 bit≈32.5 GB 十进制裸权重；实际还要量化常数、adapter、激活和运行时内存，不能按该数值承诺 32.5GB 足够。

## 失败情形与不可推广范围

- 不代表全参优化；activation、optimizer、KV/序列长度仍可 OOM。
- 不把 Vicuna 自动评分比例当通用 ChatGPT 能力等价。

## 最小迁移验证

- 核对量化格式、计算 dtype、target modules、梯度检查点与序列长度。
- 测一小批显存峰值和 held-out 质量即可先评估可行性。

## 来源定位与尚未验证项

- [§3–4; quantization and adapter ablations; Appendix](https://papers.neurips.cc/paper_files/paper/2023/file/1feb87871436031bdc0f2beaa62a049b-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
