# Optima — full-text reading 2/10

Title: Optima: Optimizing Effectiveness and Efficiency for LLM-Based Multi-Agent System.
Authors: Weize Chen, Jiarui Yuan, Chen Qian, Cheng Yang, Zhiyuan Liu, Maosong Sun.
Original: https://arxiv.org/html/2410.08115v1 ; version date 2024-10-10.
Publication status of this version: preprint; no final-venue claim checked here.
Read: main §§1–5, Tables 1–3; Algorithms 1–5; Appendix B, C Tables 4–5,
E.1–E.4 and Table 6; Appendix A/D explanatory prose, F prompt introduction
and first IE/math prompts. Not read: figure interiors, remaining F prompts,
detailed bibliography. No graph-based scaling claim independently verified.

Question: jointly optimize task quality and communication cost.
Mechanism: generate/rank/select/train with task, token and readability rewards
(§2, Eq.1); iterative SFT, DPO/MCTS and hybrid. Conditions: one shared Llama3
8B, two agents without tools (§3), six training iterations (E.4).
Table 1 reports task/token trade-offs, not universal dominance. Table 3 and
Appendix C show overly compressed information can impede correction. §3.2
reports difficult distant-domain transfers. E.3 restarts debate SFT from the
base model, unlike information exchange; training is not merely new prompts.
Training cost is outside a token-only inference comparison.

Repository inference: compact references must preserve discriminating evidence
and repair conditions. Candidate: existing communication eval, compare compact
payload with omitted-evidence control on identical inputs; low preparation cost,
unknown model A/B comparability. Pending, no adoption. Reject training migration:
no authorized compute/model-weight interface, and no long tool-using crash-recovery
evidence. Readability-loss proxy is not a scientific evidence validator.
