# 复用 PEFT 的 LoRA / DoRA 实现

## 问题触发

PEFT adapter implementation；LoraConfig use_dora；LoRA merge

## 精确结论与证据身份

已有 PyTorch 模型的 adapter 需求优先评估 PEFT 已核查实现；不从零重写 LoRA/DoRA 的 merge 和范数路径。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: LoRA or DoRA adapter training
- framework: PyTorch with PEFT
- backbone: supported model modules

## Observation / 实验 / 源码定位

- layer.py 包含 adapter layer 与 merge 逻辑；dora.py 包含幅值/方向实现。

## 可算例子与任务映射

将 attention 的 q_proj/v_proj 名字硬套到没有这些模块的模型会失败；先 inspect 模型模块。

## 失败情形与不可推广范围

- 示例 target_modules 占位必须按模型替换；quantized merge 和 dropout 路径需单独核查。
- 未安装/训练目标模型，不能声明质量或速度已验证。

## 最小迁移验证

- 核对冻结参数、target_modules、训练/推理输出与 merge 前后数值。
- 保存 adapter 配置、基座版本与加载测试；量化迁移需新质量检查。

## 固定实现与许可证

`huggingface/peft@e13de7e469d37e3163d93f2356ec013c7a7e1f0a`，许可证 Apache-2.0。入口：`LoraConfig(r=8,lora_alpha=16,target_modules=[...],use_dora=True)`。

- `src/peft/tuners/lora/layer.py`
- `src/peft/tuners/lora/dora.py`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/LICENSE)；查阅 2026-10-06。
- [src/peft/tuners/lora/layer.py](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/src/peft/tuners/lora/layer.py)；查阅 2026-10-06。
- [src/peft/tuners/lora/dora.py](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/src/peft/tuners/lora/dora.py)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
