# ACRFence

arXiv:2603.20625v1, 2026-03-21; Yusheng Zheng, Yiwei Yang, Wei Zhang, Andi Quinn.
Original: https://arxiv.org/html/2603.20625v1
Read main §§1–6, Table1, threat model, experiments, mitigation and limitations;
actually viewed PDF physical page2/Figure1. References not independently audited;
no appendix present in retrieved full text.

Question: nondeterministic restored calls evade syntactic deduplication.
Mechanism: proposed irreversible-effect log and semantic replay/fork classifier.
Evidence: §3 simulated MCP services, Claude Code/Qwen3-32B; 10 replay trials
versus 10 no-checkpoint controls; token reuse only two examples. §6 explicitly
states mitigation is not implemented/evaluated. No ablation, classifier accuracy
or overhead evidence. The universal inevitability claim exceeds these trials
(our assessment), and community issue counts are not independently reproduced.

Repo comparison: existing exact event IDs/bodies and saved intent address local
request identity; mailbox cannot reconcile arbitrary external effects. Candidate:
retain exact request on restart rather than regenerate IDs; test changed-ID
replay against existing protocol probe. Low adaptation cost, pending actual host
repair/recheck. Reject importing semantic classifier/eBPF proxy: unevaluated,
new runtime and permissions. Complements AgentSpec preconditions and SagaLLM
history; semantic equivalence alone cannot authorize a fork or close a finding.
No repository performance or safety effect established.
