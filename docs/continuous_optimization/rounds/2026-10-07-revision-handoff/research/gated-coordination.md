# Gated Coordination — original v1

Original: https://arxiv.org/html/2604.18975v1 (2026-04-21).
Read main §§1–5, Tables1–4, AppendixA.1–A.6/Algorithm1/Tables5–10;
actually viewed PDF p8 Figure4. References and code not audited.

Question: when does a local failure justify public coordination?
Mechanism (§3): verified private state, structured issue detection, deterministic
score, bounded gray-zone judgment, explicit failure cooldown/local fallback.
Evidence (§4): Minecraft baselines and resource-partitioned scenarios; 200 custom
MindCraft episodes. Table4 separates partition/gate components. AppendixA.6 uses
template-disjoint calibration and exposes under-escalation from excessive history
penalties. TSR is block-level construction quality, not binary task completion.
Table7 costs have unequal event denominators; Table9 reports episode cost.

Limits/inference: no scientific review, durable ACK/crash test, uncertainty bars or
general permission model demonstrated. Construction LOCAL_SKIP cannot waive
mandatory evidence or acceptance. Narrow gray-zone cost tradeoff is domain-specific.

One pending candidate: explicit actionable failure routing in existing communication
workflow, preserving required corrections. Cost: small protocol/fixture maintenance.
Minimal test: same blocked finding, local retry versus owner request; independently
check closure, stale reuse and actual cost. Reject imported weights/learned gate
without local calibration. No repository effect established.
