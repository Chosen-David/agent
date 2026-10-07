# RL 熵坍缩：先核查 log-prob 精度、离策略更新与探索需求

## 问题触发

RLVR 熵坍缩；entropy collapse；BF16 log-prob clipping；inference training discrepancy；连续任务再训练探索。

## 结论与来源观察

ICLR 2026 的 Qwen3/AppWorld 与 AIME 实验发现，输出降精度可改变 clipping 与熵轨迹；保熵方法的收益依赖探索需求，不能只看最终熵。

§4/附录B：FSDP2 输出 casting 使 log-prob 比率产生有效 clipping 不对称；Qwen3-8B 的 FP16 与保留全精度输出联合消融将 DAPO 熵坍缩变为增长（Fig.3/8，三种子均值）。

§6/附录C：REPO-R、ADAPO 相对各自离策略基线保留探索并改善测试表现；AppWorld 效应较强。Fig.7 的 AIME↔AppWorld 顺序训练保留了再学习能力。

## 前提

- model：Qwen3-8B/32B; LoRA rank 16 alpha 32
- data：AppWorld train 90; NuminaMath AMC/AIME filtered 563
- stack：custom FSDP2, vLLM, Cut Cross-Entropy; typically 3 x 8 H100
- metric：AppWorld TGC; AIME24/25 pass@1 with 4096-token budget

## 推导范围与算例

推导示例：log 比率差为0.01时 exp(0.01)≈1.01005；先将两项 log-prob 分别舍入可能抹掉差值。这仅说明检查敏感性，不是论文的 bias 定理证明或本地训练结果。

来源核对不等于完整证明审查；理论只按原文前提引用，未做形式化证明或本机论文复现。

## 反例与限制

AIME 每年仅30题，附录C.3按 AIME24/25 测试均分选择 checkpoint，存在选择偏差；AppWorld 使用 dev 选点。

附录B.1对严格 on-policy RLOO 未观察到相同 casting 影响；FP16 需要 loss/gradient scaling。保熵不等于任意提高熵，DAPO 也有熵失控增长。

累计熵与性能相关不证明普适因果；当前 PyTorch/Accelerate 版本是否仍有原默认行为须另查。

## 任务映射与最小检查

- 核对 rollout 与训练 log-prob 的实际 dtype、casting、概率比与上下 clip 命中率，记录软件版本。
- 在目标任务以同一预算检查奖励/成功率与熵轨迹；明确 on-policy 或复用数据的 epochs，保留最小精度对照。

用于实验前筛选、识别无效重复探索和制定最小迁移检查。用户指定实验、显式复现、新环境性能与正确性验收仍需执行；文献值不得记为本机实测。

## 来源定位与未验证项

[ICLR 2026 正式论文](https://proceedings.iclr.cc/paper_files/paper/2026/file/124dde499d62b58e97e42a45b26d7369-Paper-Conference.pdf)：§4–6; Figures 1–8; Appendix B.1–B.3, C.1–C.3 (PDF pp.5–10,23–26)。2026-10-07核查相关正文、设置、图表与附录。完整PDF字节SHA256：`1c371101bed7c0d035292e34626d209ed57fbf92ca0859b15e6f1914fdfec310`；30页。

`local_reproduction=not-run`；作者实现未固定源码commit或本地执行，本卡不提供可直接复用且已验收的代码。
