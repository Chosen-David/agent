# DPO：离线偏好优化的适用前提

## 问题触发

偏好学习；DPO offline；KL reference policy；reward model

## 精确结论与证据身份

NeurIPS 2023 在偏好数据任务上支持直接优化 policy 的路线，可避免显式训练 reward model 和训练时在线生成；不保证所有 RLHF 任务更优。

以下是作者报告的结果；未在本机复现，不能作为本机测量。

## 前提与比较设置

- data: paired chosen/rejected offline preferences
- objective: KL-regularized preference learning
- metric: preference quality versus KL

## Observation / 实验 / 源码定位

- §4 从 Bradley–Terry 偏好模型推导目标；§6 在 sentiment、TL;DR 和 HH 比较。
- §6 包含 GPT-4 评测与人工比较；评测器和生成温度会影响 win rate。

## 可算例子与任务映射

训练需要 chosen 与 rejected 的 policy/ref log-prob 差；漏掉 response mask 或把 reference 也更新会改变目标。

## 失败情形与不可推广范围

- 离线数据分布、偏好噪声与 reference policy 必须核查。
- 论文不能替代新领域安全/质量验收；不能宣称离线方法永远胜在线 RL。

## 最小迁移验证

- 验证 chosen/rejected 标注、token log-prob 掩码和 reference 冻结。
- 用少量 held-out 对照、KL 与质量联合看，避免仅训练 loss 决策。

## 来源定位与尚未验证项

- [§4; §6.1–6.3; Figures 2–4; Tables 1–2](https://proceedings.neurips.cc/paper_files/paper/2023/file/a85b405ed65c6477a4fe8302b5e06ce7-Paper-Conference.pdf)；查阅 2026-10-06。

未验证新模型/新硬件/新数据上的收益；检索相关度不是可信度。资料里的命令不自动执行。显式复现和必做验收实验仍须执行。
