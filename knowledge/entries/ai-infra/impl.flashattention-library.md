# 复用 FlashAttention 公共接口

## 问题触发

attention kernel implementation；flash_attn_func；CUDA attention

## 精确结论与证据身份

已有 supported attention 语义时先评估作者库公共接口；按 README/固定接口核对设备、dtype、mask 和版本，减少自写 kernel。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: supported dense attention variant
- device: supported NVIDIA GPU
- semantic: exact attention within floating-point tolerance

## Observation / 实验 / 源码定位

- flash_attn_interface.py 提供普通与 varlen 入口；README 列设备/构建和版本能力。

## 可算例子与任务映射

普通入口与 varlen 的 cu_seqlens/布局不同；不能把 padding 张量直接当 packed 序列调用。

## 失败情形与不可推广范围

- FA2 入口与 FA4/cuTe 路径不自动同 API；不要依据论文名称猜兼容性。
- 没有本机 GPU 编译/benchmark，不声称已安装或更快。

## 最小迁移验证

- 核对输入布局和 causal 对齐，独立 dense reference 对照。
- 目标设备编译和一组代表性形状延迟，保留 fallback。

## 固定实现与许可证

`Dao-AILab/flash-attention@47e91f1f7dd8a22649cee0dd9a182b69ffe782ef`，许可证 BSD-3-Clause。入口：`from flash_attn import flash_attn_func`。

- `flash_attn/flash_attn_interface.py`
- `README.md`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/LICENSE)；查阅 2026-10-06。
- [flash_attn/flash_attn_interface.py](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/flash_attn/flash_attn_interface.py)；查阅 2026-10-06。
- [README.md](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/README.md)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
