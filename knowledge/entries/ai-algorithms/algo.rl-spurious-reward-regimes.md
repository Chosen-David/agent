# 随机奖励与 clipping：熵下降不是推理能力提升的充分证据

## 问题触发

随机奖励；spurious reward；random reward clipping entropy；熵下降准确率不升；探索利用任务难度。

## 结论与来源观察

ICLR 2026 在随机 Bernoulli 奖励的数学训练中区分 clipping 稳定性、初始策略偏斜和任务难度；关闭 clipping 可提高熵，也可能导致梯度爆炸。

§3.2/Fig.1：Qwen2.5-Math-7B 在这组参数下 clip 激活很少（不超过0.2%）；作者结合梯度分析反对将提升直接归因于 upper-clip 产生强学习信号。

§4.2/Fig.2：去 clipping 后熵可增大；R1-Distill-Llama-8B 验证准确率先从65.6%到76.6%，约150步出现梯度爆炸、表现骤降。

§4.3/Fig.3：更难 AIME Past 上，Qwen2.5-Math-7B 的低熵模式可能错误，训练改进不稳定；强模型/较易任务的集中化效果不能外推。

## 前提

- model：Qwen2.5-Math-7B; additional QwQ-32B and R1-Distill-Llama-8B cases
- data：DeepScaleR or harder AIME Past training; MATH500 validation
- reward：iid Bernoulli(1/2), independent of correctness
- training：verl; batch 128; group 16; temperature 1.0; lr 5e-7; clip 0.2; KL 0

## 推导范围与算例

来源数值核算：76.6−65.6=11.0 个百分点的早期提升，不能抵消后续梯度爆炸。这是阅读论文数值的计算，并非本机复现。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

主实验集中 MATH500；基线先验、污染、prompt、response length 和 verifier 均可能混杂。

§4的单步理论依赖随机奖励与策略偏斜；不证明真实奖励训练应删除 clipping，也不证明随机奖励普遍有效。

## 任务映射与最小检查

- 核查 reward 是否与正确性独立、verifier/prompt、模型初始成功率和数据难度。
- 同时看准确率、梯度范数、clip 命中率及熵；保留失败时段，不能只报最佳早期 checkpoint。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[ICLR 2026 正式论文](https://proceedings.iclr.cc/paper_files/paper/2026/file/d99e8e80a6c41e148db686918dd7eab3-Paper-Conference.pdf)：§3.2, §4.1–4.3, §5; Figures 1–3; Appendix A/B (PDF pp.5–10,16–22)。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`c2e181a50c388f7806a1c6fcb91fafe196b5d5ceee2a6c3127387cfff77840ad`；35页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
