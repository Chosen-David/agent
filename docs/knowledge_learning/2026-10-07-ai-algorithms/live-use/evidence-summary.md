发布说明：本页为实际角色原报告的路径规范化副本。初次失败、已使用源子集及关键工具结果保留于此目录；不相关search/context包未发布，原始完整输出保留私有。原查询和工具调用完整列于knowledge-use.json，回归20,000字符预算与此次26,000字符实际调用分别记录。

# 实际使用与检查摘要

- 任务：exercise_algorithm_knowledge；输入：question-v1；归属 AIK-02。
- 答案：response.md。精确小例脚本：verify_examples.py；结果 evidence/example-checks.json，58/58 项通过。
- 核心结果：几何条件成立时 E[L]=6.12579511；每 token draft 成本 0.2T 得 1.093891984×，整批成本 0.2T 得 1.458522645×。每轮至多 9 token 的上界已排除四倍。随机目标的 argmax 反例和正确残差采样均用有理数核对。
- 实际执行 search、别名 search、context、show、snapshot、check-refs；原始 JSON 返回保存在 evidence/。检索相关度不作为科学适用性证明。
- 首次两张新卡是 candidate；默认 search 未返回，显式 --include-unpublished 才发现，show 返回拒绝。保留 evidence/show-ai.speculative-*.json 以及 evidence/initial-candidate-snapshot/，未覆盖为成功。
- 2026-10-07 01:38:17 UTC 只读观察到并发发布后的卡片；本 worker 未编辑仓库。随后重读 show/context，重新固定引用与源子集。后续 context 为 ready，三项命中，无 skipped。
- 初始完整库 snapshot：618f9175ae32a023e9cb467c0eec45e87fe2c9f87e96cb680de8ef5642bbb722。
- 最终完整库 snapshot：820007a073af71c4479f04cc28f3c3708b3cca5d0c97dac80612bd6701e5ad8f。
- 三项依赖闭包的固定子集 snapshot：6c0d4eee16889969c3de4da9651e220e2f8d34ecc43f037f75f17770e3c527d6。
- evidence/check-refs-current.json 与 evidence/check-refs-pinned.json 均 valid=true。校验范围只有身份/已发布前提；数学适用性另见 knowledge-use.json。
- 外部原始来源实际通过 web.open/find 读取：Leviathan ICML 2023 正式 PDF §2.2–2.3/Algorithm 1/§3.1–3.5/Appendix A.1、A.3；Chen arXiv 2302.01318v1 Modified Rejection Sampling/Theorem 1。论文性能数字未转作本机实测，未借 EAGLE 等无关实验外推。
- 没有读取 docs/knowledge_learning 或其他验证目录内容；知识卡中指向这些位置的字符串未被跟随。没有 GPU、模型推理、安装、仓库编辑或发布。

## 使用的知识引用

1. ai.speculative-sampling-residual-exactness，v1，3014215db96bf6ed7a00d522bf68663e58c4d1e98bdc2b88efe85ccd1a012331
2. ai.speculative-decoding-cost-bound，v1，b292c27e53687be2f8f04ad8e19be77db1eb4a286b3218df6621fc97cd861c5f；强依赖为第 1 项
3. infra.speculative-acceptance，v1，d713b2280b1b43dc109b635df3a522f92a5f3fc657dc719137402f8877c05b6a

## 复核入口

从仓库根运行：

    ROUND=docs/knowledge_learning/2026-10-07-ai-algorithms/live-use
    PYTHONDONTWRITEBYTECODE=1 python "$ROUND/verify_examples.py"
    PYTHONDONTWRITEBYTECODE=1 python -m agent_runtime.knowledge --root "$ROUND/evidence/source-snapshot" check-refs "$ROUND/knowledge-use.json"

这只复核静态引用及有理数构造，不是端到端采样器认证。实际性能与实现正确性仍待在用户目标负载/实现中获得新授权后测量。
