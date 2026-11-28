# Adaptive Harness
基线 c1409215。用户授权普通研发按 adaptive/v1 推进；历史合同及其证据保留。主 Agent 维护策略、宿主集成与预算，隔离 Worker feature/adaptive-admission 交付 6f13f884 的 Engine 修改。

已验证受管 Store 并发、串行恢复、独立任务和作用域冲突。CLI 0.172.0 在 workspace-write 下启动线程，但本机 bwrap 挂载拒绝；任务回执退出 0，实际无交付。保留事件于 ~/v5-adaptive-diagnostic/adaptive-analysis/codex-events.jsonl。已增加宿主产物验收。后续对照需使用同一任务集，分别绑定质量、调用与费用证据。正式科研结论仍待最终验收。

本机核验包位于 /tmp/agent-system99/adaptive-v1/。V5 频谱复算及其源数据哈希在 ~/agent_doc/forge-universal/results/v5-er-tail-scale/summary.json，动态训练记录在相邻 v5-harness/live.json。
