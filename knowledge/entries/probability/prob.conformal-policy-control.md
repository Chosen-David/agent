# Conformal Policy Control：非单调风险校准与近似权重的保证边界

## 问题触发

非单调风险校准；conformal policy control；safe policy importance weighting；反馈协变量偏移；expected risk stability。

## 结论与来源观察

ICML 2026 将校准作用于策略偏离程度；风险保证是带稳定性余项的边际期望界，精确多轮权重与实用近似须区分。

Theorem 4.2：交换的非单调 K-Lipschitz 损失与ε replace-one稳定性给出 E L≤α+Kε。Theorem 4.6：CPC 的精确多轮校准给出 E Lt≤α+max(α,B−α)ε¹。

策略为 min(πt,βπ0) 再归一化；§4.2 的置换权重通常不可计算，算法采用历史策略混合与经验最大权重近似，不自动继承精确界。

§5/Fig.4–6：MedLFQA gCRC 控制FDR/保留true-claim recall；三回归数据集主动学习以α=0.2约束违规率；Pythia14M/Ehrlich 序列实验中中等风险限制有时提高目标值。

## 前提

- loss：bounded loss in [0,B]; known acceptable-risk reference policy
- policy：mutually absolutely continuous policies; computable likelihoods; stable context distribution
- calibration：gCRC exchangeability plus Lipschitz/replace-one stability; CPC exact weighted calibration plus relative replace-one stability
- guarantee：marginal expected risk, not per-context or high-probability safety

## 推导范围与算例

定理代入示例：B=1、α=0.2、ε¹=0.01 且精确CPC前提成立时，期望界是0.208，不是0.2。这是条件代数，不是实测违规率。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

医学QA是数据集上的方法实验，不是临床可靠性认证；序列实验是合成 Ehrlich 函数，不是湿实验生物结论。

有限样本并不消除稳定性余项；未知K/ε、近似密度比、分布漂移或不可行校准均须额外核验。

CPC多轮结果使用加权非交换性框架，不能把gCRC的普通交换性直接当作反馈策略已满足。

## 任务映射与最小检查

- 核实安全参考、支持集重叠、loss上界、目标分布和稳定性条件，明确α是期望而非逐次保证。
- 验证权重/归一化/采样实现、近似误差和校准失败回退；漂移后重校准。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[ICML 2026 正式论文](https://raw.githubusercontent.com/mlresearch/v306/main/assets/prinster26a/prinster26a.pdf)：§4.1/Theorem 4.2; §4.2/Theorem 4.6; §5–6, Figures 4–6; Appendix C/D (PDF pp.5–9)。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`754fe349ce8894181b7b19f69d47e834bbb05d86d784224db4071336d636b0f5`；53页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
