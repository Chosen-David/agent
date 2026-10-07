# 高维自归一化：无正则、双重统一界的维度障碍与平滑条件

## 问题触发

self normalized martingale dimension barrier；高维无正则反例；doubly uniform regret；自适应协变量平滑密度比；sequential linear regression。

## 结论与来源观察

COLT 2026 区分一维对数界与d≥2全对抗线性下界；受固定基准测度密度比约束的平滑协变量可恢复次线性界，不能无条件删除正则。

Theorem 4/5：一维 dyadic 自归一化指数矩界对应 O(log T) 控制；有界响应的在线回归可确定性达到 O(m² log T) 双重统一 regret。

Theorem 7：d≥2 时存在自适应 dyadic 构造，使 E||ST||²_(VT†)≥(1−ε²)T；尺度齐次后协变量也可有界。

Assumption 8/Theorems 9/11：固定基准测度的平滑条件给出含 sqrt(d Ccov T log(T/δ)) 的无正则界；Theorem 11还要求条件次高斯噪声。正文为理论研究，没有报告新数值实验。

## 前提

- setting：online squared-loss linear regression; unrestricted comparator norm and covariate scale
- noise：dyadic Rademacher martingale for lower bound; conditional sigma-sub-Gaussian for Theorem 11
- smoothness：conditional covariate law relative to partial covariate history dominated by fixed mu with density ratio <= Ccov
- response：Theorem 9 responses in [-1,1]; dimension-one theorem uses |y|<=m

## 推导范围与算例

来源下界代入：T=100、ε=0.1时，存在d≥2构造满足期望自归一化平方量≥99；不是所有二维数据都等于99。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

下界针对双重统一、无正则及全对抗范围，不否定带特征/比较器限制、正则或随机设计的标准线性bandit结果。

固定有限时域T的概率界不能不加代价直接作所有t的置信序列。平滑密度比条件比口头“数据有噪声”强。

O/隐常数界不是可直接部署的置信半径；未独立逐行复核全部证明或运行形式化工具。

## 任务映射与最小检查

- 明确是否真的要求同时与covariate尺度和comparator范数无关；核查维度、正则和噪声量词。
- 验证固定μ支配条件与Ccov来源，避免将输出噪声当作协变量平滑；奇异VT用伪逆并检查range条件。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[COLT 2026 正式论文](https://raw.githubusercontent.com/mlresearch/v336/main/assets/chen26f/chen26f.pdf)：§3/Theorems 4–7 (PDF pp.8–10); Assumption 8, Theorems 9/11 (PDF pp.10–12); Appendices B–D。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`a1e1d9101d2fe271c714d9a5e589a1e1e1669fee2801f85df52c008f18dceb3f`；29页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
