# 投机解码：接受率不能单独决定速度

## 问题触发

投机解码；draft acceptance；speculative decoding；proposal cost

## 精确结论与证据身份

ICML 2023 中较小 draft 在接受率略低时仍可更快；需要同时考虑 draft 成本、接受率和验证并行度。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- hardware: single TPU-v4
- target: T5-XXL 11B
- batch: 1
- tasks: WMT EnDe and CNN/DailyMail

## Observation / 实验 / 源码定位

- §4.1 Table 2：EnDe temp=0、γ=7，T5-small α=0.75、3.4×；T5-large α=0.82、1.7×。
- 相同 small draft 在 EnDe temp=1 报告 2.6×，CNN/DM temp=1、γ=5 报告 2.3×。

## 可算例子与任务映射

α=0.8、γ=4 时理想连续接受收益为 1+α+α²+α³+α⁴=3.3616 个 token；还须除以 draft+verification 成本，不能称 3.36× 实际加速。

## 失败情形与不可推广范围

- 精确采样算法保留目标分布，不保证不同实现相同随机种子的逐 token 一致。
- 不能由 batch=1 推断高并发吞吐；拒绝修正、tokenizer 和 sampling 处理必须正确。

## 最小迁移验证

- 先验证拒绝采样/目标分布，核对 tokenizer 和解码参数。
- 只用少量目标输入测 α、draft 时间、验证时间，避免盲扫 draft 大小。

## 来源定位与尚未验证项

- [§3.3–3.4; §4.1 Table 2; Appendix A.3](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
