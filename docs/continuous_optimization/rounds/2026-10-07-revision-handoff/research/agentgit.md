# AgentGit

Yang Li, Siqi Ping, Xiyu Chen, Xiaojian Qi, Zigan Wang, Ye Luo, Xiaowei Zhang.
arXiv:2511.00628v1; 2025-11-01.
Original: https://arxiv.org/html/2511.00628v1
PDF: https://arxiv.org/pdf/2511.00628v1

Read complete §§1–5 and references (16 physical pages); visually checked Figures1–3,5–8. Figure4 caption/text only; cited works and implementation unchecked. No appendix or tables.

§3 checkpoints session/tool state, branches alternatives, and counts reused tree prefixes; its asymptotic gain assumes exhaustive exploration and branching factor above one, excluding storage/restore costs. §4 compares one abstract-report prompt sweep: GPT-4o-mini, temperature0, LangGraph0.6.6 plus AgentGit0.0.1 versus LangGraph/AutoGen/Agno. Figures6–8 show shorter runtime, tokens near LangGraph, broadly comparable G-Eval quality. No crash recovery, ACK-order experiment, component ablation, trial-count/significance disclosure, or dollar/storage cost measurement; graph error bars are unexplained. Reliability claims exceed measured efficiency evidence.

Bounded communication/pipeline candidate: reuse an unchanged saved prefix when retrying publication. Pending: existing exact-intent/publish-first controls already cover this; no demonstrated improvement. Smallest test: interrupt before publication and verify retry preserves request and publishes once. Engine migration rejected: checkpointing alone cannot make external ACK/publication atomic. No runtime or installation justified.
