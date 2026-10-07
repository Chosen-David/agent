# RS-GRPO：多次采样成功率、单次成功率与风险偏好需联合决策

## 问题触发

pass@k diversity；pass@1 pass@32 权衡；强化学习难题探索；risk seeking exponential utility；多次采样成功率。

## 结论与来源观察

ICLR 2026 用指数效用改变 advantage、增加难题探索；数学实验的平均 pass@32 改善伴随部分 pass@1 或单数据集退化，β 也非越大越好。

§2/§3：J=(1/β)log E exp(βr)，β>0偏向高奖励；有限臂单步分析表明足够大β可增大最优臂概率，但继续增大β会减慢该改善，非 LLM 全局收敛保证。

Table 2：Qwen2.5-Math-1.5B/deepmath103k 六基准均值 pass@1 21.4→21.3，pass@32 37.5→42.0；MATH500 pass@1 80.2→78.1，pass@32 94.0→95.6（均为%）。

§4.2：Qwen2.5-7B 与 Llama3.1-8B-Instruct 在高k仍可能落后原 base；§4.3/附录F区分 Fig.4 beta=8 与 Table 2 beta=2，不合并为同设置。

## 前提

- model：five evaluated LLMs: Qwen2.5-Math-1.5B/7B, Qwen2.5-7B, Qwen3-4B-Base, Llama3.1-8B-Instruct
- data：deepmath103k, dapo17k, math12k; six math evaluation benchmarks
- stack：VeRL, vLLM 0.8.5, Math-Verify; N=16 responses/prompt; KL=0
- evaluation：temperature 1.0 top-p 0.7; 1024 samples except MATH500 32; Table 2 beta=2

## 推导范围与算例

来源核算：表2上述设置 pass@32 均值提高4.5个百分点，pass@1 均值降低0.1个百分点；单次与多次指标不可互代。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

“保持或改善”不能解释为所有单元格单调提升；Qwen2.5-Math-7B/deepmath103k 的 MATH500 pass@32 96.0→95.8。

论文§4.1写six但只列五模型；图4/表2实际五模型。曲线 pass@32 均值排除 MATH500，表2均值含六项，不混用。

有限组估计指数归一化可能有偏；高β与稀有成功样本、奖励噪声的迁移表现未知。

## 任务映射与最小检查

- 按目标采样预算同时设定 pass@1 与 pass@k 验收，锁定温度、top-p、长度和 verifier。
- 核查 advantage 的指数稳定性、全0/全1过滤、训练熵/解覆盖率；用有界β对照检查收益与退化。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[ICLR 2026 正式论文](https://proceedings.iclr.cc/paper_files/paper/2026/file/4e6d14709eae0cbc49a1d19d87fb8b21-Paper-Conference.pdf)：§2–4.5; Figures 3–7; Table 2 (PDF p.9); Appendix F/Table 5 (PDF p.24)。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`d592772d0c8efa6782f1e312a176ab814ad8f817e6abb9412810542b9d8ca7fd`；25页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
