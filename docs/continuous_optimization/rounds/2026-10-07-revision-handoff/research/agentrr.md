# Get Experience from Practice: LLM Agents with Record & Replay

arXiv:2505.17716v1, 2025-05-23; Erhu Feng, Wenbo Zhou, Zibin Liu, Le Chen,
Yunpeng Dong, Cheng Zhang, Yisheng Zhao, Dong Du, Zhichao Hua, Yubin Xia, Haibo Chen.
Original: https://arxiv.org/html/2505.17716v1
Read main §§1–7, Tables1–2, state-transition definitions, modules, case and
limitations; actually viewed Figure4. Other figures/bibliography unchecked; no appendix.

Question: reuse experience without unconstrained model replanning.
Mechanism: generalized high/low-level trajectories plus audited check functions,
selecting precise scripts when prerequisites match and higher-level adaptation
otherwise (§§3–4). §5 presents form-filling illustration with two demonstrations;
CUA comparison lacks matched repeated trials.
No benchmark ablation or measured cost;
Table2 qualitative labels are not effect estimates. §6 notes incomplete summaries,
UI drift, human audit burden and conservative repetitive-task applicability.

Repo comparison: parameterized scripts and versioned memory already provide pieces. Pending candidate: store reusable protocol recipe
with exact invocation inputs and applicability checks in existing communication
workflow; heldout changed-input/ordering tests distinguish unsafe trace replay.
Reject new runtime/store and private reasoning capture. Unlike ACRFence's exact irreversible replay, adaptation belongs
only in authorized reversible scope; an old successful trace cannot validate a
new manuscript. No repository speed/quality benefit demonstrated.
