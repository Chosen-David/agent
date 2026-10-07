# FlashInfer：不规则 KV 与负载平衡

## 问题触发

ragged KV cache；负载平衡；decode plan run；FlashInfer

## 精确结论与证据身份

MLSys 2025 以可组合 KV 格式、JIT 与调度支持不同推理形状；库选择必须匹配 KV 布局、decode/prefill 和计划成本。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- hardware: A100 40GB SXM or H100 80GB SXM
- workload: ragged/batched LLM inference
- metric: attention latency and end-to-end serving

## Observation / 实验 / 源码定位

- §3 描述动态调度、plan/run 分离与 CUDA Graph 兼容；§4 分别测 kernel 和端到端。
- 论文摘要的 ITL 降低 29–69% 属于所测服务栈；长上下文与并行生成是另外实验。

## 可算例子与任务映射

KV 长度 128 与 8192 的请求差 64 倍；按请求等分的工作分配并不意味着等工作量。

## 失败情形与不可推广范围

- 计划、JIT、graph 建立成本不应被遗漏；冷启动不等于稳态。
- 论文服务实验含 SGLang，但本仓库明确不修改 SGLang；仅复用独立算子知识。

## 最小迁移验证

- 核对 paged/ragged 格式、heads/dtype、stream 与 plan 生命周期。
- 在目标 workload 单独记录 plan、run、冷启动和稳态。

## 来源定位与尚未验证项

- [§3.2–3.4; §4; Figures 7–11](https://proceedings.mlsys.org/paper_files/paper/2025/file/dbf02b21d77409a2db30e56866a8ab3a-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
