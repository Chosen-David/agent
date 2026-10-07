# AgentDropout — new full-text reading 1/10

Original: https://arxiv.org/html/2503.18891v1 (2025-03-24).
Authors: Zhexuan Wang, Yutong Wang, Xuebo Liu, Liang Ding, Miao Zhang,
Jie Liu, Min Zhang. DOI: https://doi.org/10.18653/v1/2025.acl-long.1170.
Publication metadata checked: https://aclanthology.org/2025.acl-long.1170/.
Read version is v1; the ACL final PDF was not read or compared this wake.

Actual reading: main §§1–6, Limitations, Tables 1–7, Algorithm 1,
Appendix A.1–A.4 including textual case study. Figures' captions read;
image interiors and bibliography details not independently inspected.

Research question: reduce redundant participation and communication.
Mechanism: learn per-round graph weights, prune nodes, retrain then prune edges
(§§3.2–3.3, Algorithm 1). Conditions: 40 training examples, three specified
models, temperature 1, two reasoning/four code rounds (§4.1). Tables 1–2 report
accuracy and token comparisons; Tables 4–5 show aggressive dropout and random
replacement can hurt. Table 6 tests transfer between math datasets, not long
research projects. Limitations explicitly restrict tasks and predefined roles.
Training cost is required; token savings are not measured wall-clock savings.

Repository inference: protect rare repair/recheck edges before cost pruning.
Do not deploy learned pruning: no matching budget, training or long-task evidence.
Candidate: `communication.py`/existing pipeline, test lost repair plus unrelated
delivery controls; adaptation low for diagnostics, undecided for API. Status:
pending comparison, not adopted. No scientific completion or crash recovery
guarantee follows from this paper. Equation 4/Algorithm line 6 name inter-round
weights despite intra-round prose: do not silently resolve this implementation
ambiguity without source review.
