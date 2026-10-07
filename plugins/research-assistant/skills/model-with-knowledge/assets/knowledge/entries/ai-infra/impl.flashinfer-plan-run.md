# 复用 FlashInfer plan/run 接口

## 问题触发

paged decode implementation；flashinfer plan run；BatchDecodeWithPagedKVCacheWrapper

## 精确结论与证据身份

服务推理需要分页/不规则 KV 时先复用 FlashInfer wrapper；workspace、layout 与 plan 生命周期是接口契约的一部分。

以下是已核查源码的实现入口；固定 commit，不代表已安装或已测性能。

## 前提与比较设置

- operation: paged or ragged attention inference
- device: supported NVIDIA GPU
- lifecycle: explicit plan then run

## Observation / 实验 / 源码定位

- decode.py / prefill.py 包含不同场景 wrappers，plan 准备元数据后 run 执行。

## 可算例子与任务映射

同一个 page_size 下改变请求长度会改变 last_page_len；旧 plan 不能默认持续有效。

## 失败情形与不可推广范围

- 不自动安装依赖，不修改 SGLang。
- plan 元数据过期、workspace 复用和 stream 错误会破坏结果。

## 最小迁移验证

- 核对 indptr/indices/last_page_len、heads、workspace 大小。
- 先 correctness reference，再独立计入 plan/run 延迟。

## 固定实现与许可证

`flashinfer-ai/flashinfer@ea8135c0bdf641f54214e9ae777d5b75b5133079`，许可证 Apache-2.0。入口：`flashinfer.BatchDecodeWithPagedKVCacheWrapper(workspace_buffer,kv_layout="NHD")`。

- `flashinfer/decode.py`
- `flashinfer/prefill.py`

## 来源定位与尚未验证项

- [LICENSE](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/LICENSE)；查阅 2026-10-06。
- [flashinfer/decode.py](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/flashinfer/decode.py)；查阅 2026-10-06。
- [flashinfer/prefill.py](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/flashinfer/prefill.py)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
