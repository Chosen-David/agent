# PagedAttention：KV 分页与服务吞吐

## 问题触发

KV cache 碎片；请求调度；paged memory；PagedAttention

## 精确结论与证据身份

SOSP 2023 的 vLLM 实验支持用按需分页和共享 KV 减少服务内存浪费；收益来自内存管理与调度的组合。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- hardware: A100
- models: OPT and LLaMA-13B
- workload: ShareGPT/Alpaca length traces with Poisson arrivals
- metric: normalized end-to-end latency versus request rate

## Observation / 实验 / 源码定位

- §6.1 用长度合成请求和 Poisson 到达；Orca 是作者重实现，Oracle 预知输出长度，是不可部署上界。
- §6.2 ShareGPT 中相近延迟下可承受请求率相对 Orca Oracle 提高 1.7–2.7×；Alpaca 的 OPT-175B 余量更大时差距缩小。

## 可算例子与任务映射

若 KV block 容量 16 token、请求长 33 token，则需 3 block，末 block 空 15 token；分页仍有尾块浪费。

## 失败情形与不可推广范围

- 不是单个 attention kernel 加速，不能替代 TTFT/ITL/SLO 的本机验证。
- 2023 系统基线不是 2026 最新服务栈；跨工作负载倍数不可直接迁移。

## 最小迁移验证

- 核对长度分布、到达率、KV 占用和延迟 SLO。
- 先在一个负载点检查分配浪费/队列/吞吐，保留现有强库基线。

## 来源定位与尚未验证项

- [§6.1–6.6; Figures 12–18](https://arxiv.org/pdf/2309.06180)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
