# 向量自归一化：轻尾、方差自适应与序贯置信界的收益和代价

## 问题触发

vector concentration Bernstein Bennett；向量自归一化方差；anytime valid kernel bandit；轻尾非次高斯；鞅自适应停止。

## 结论与来源观察

ALT 2026 在可分Hilbert空间构造超鞅，给出 Bernstein/Bennett 和混合序贯界；低方差合成bandit受益，高方差下并不总胜次高斯界。

Assumptions 3–5/Theorem 9：若 sum σi²||Gi||²≤Cn² 为确定上界，则概率至少1−δ时，对t≤n有 ||(ρI+Vt)^−1/2 Mt||≤B log(2/δ)+Cn sqrt(2log(2/δ))。

Theorems 11/12 使用混合界适应随机停止；实用半径需数值求根且承担额外对数项，经验方差版不能任意推广到异方差。

§5.3/Fig.1：RBF长度0.01、ρ=0.05、δ=0.1、500轮合成GP-UCB；缩放Beta(5,5)/(20,20)/(50,50)低方差下混合Bennett较紧，缩放Uniform高方差下原次高斯界反而更紧。

## 前提

- process：predictable X_t; conditional mean-zero epsilon_t; fixed rho>0; separable Hilbert space
- tails：conditional Bernstein moment condition, or bounded noise and predictable variance bounds
- horizon：Theorems 9/10 deterministic horizon n and variance envelope Cn; Theorems 11/12 fully sequential mixtures
- empirical_variance：Theorem 12 requires bounded noise with constant conditional variance and a valid variance confidence sequence

## 推导范围与算例

定理代入示例：B=1、Cn=2、δ=0.05，则该固定时域半径为 log40+2sqrt(2log40)≈9.12；条件Cn必须事先有效，不是样本标准差即插即用。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

beyond sub-Gaussian仍要求轻尾矩条件，不覆盖任意重尾/无限方差。dimension-free仍通过信息增益/谱等项含有效维度。

固定n内uniform不等于无限时域；不能事后挑Cn或混合θ而沿用原δ。作者没有调优实验超参数，不是普适SOTA比较。

与COLT无正则下界并不矛盾：本卡ρ>0、尾部与半径前提不同；完整证明未独立复核。

## 任务映射与最小检查

- 核查可预测性与条件零均值，分清尾界B、方差σ²、确定Cn和经验置信序列。
- 选择固定时域或完整混合界并核对数值求根；保留ρ偏差项、有效维度及低/高方差对照。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[ALT 2026 正式论文](https://raw.githubusercontent.com/mlresearch/v313/main/assets/martinez-taboada26a/martinez-taboada26a.pdf)：Assumptions 3–5 (PDF pp.4–5); Theorems 9–12 (pp.10–11); §4.5/§5.3, Figure 1 (pp.12–16)。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`2145434a403cd01f36cfecd6b800e96fc9762d84802bfd81862c9506cf4c2399`；31页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
