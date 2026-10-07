# AgentDebug — original v1

Original: https://arxiv.org/html/2509.25370v1 (2025-09-29).
Read main §§1–7, Algorithm1/Table1, AppendixA.1–A.2 and A.5 prompts;
selected A.3/A.4/A.6 examples. Visually viewed PDF pp7–8/Figures5–7 and
p19 detector prompt. Other figure interiors/reference audit/code unverified.

Question: localize critical failure rather than repair every symptom.
Mechanism: modular taxonomy, earliest critical error, bounded targeted re-rollouts.
Evidence (§4): 200 annotated trajectories across ALFWorld/WebShop/GAIA;
GPT4.1 detection, up to five re-rollouts, token-matched baselines claimed.
Table1 strict localization remains24.3%; Figure7 varies attempts/detector/rollout.
No complete monetary/latency accounting shown. AppendixA.1 limits domain/scale.

Cautions: §3.2 describes actual counterfactual tests, while Algorithm1 explicitly
uses LLM detection without counterfactual rollouts. Reported findings box and
Table1 disagree; improvements mix relative/absolute language. PDF p24 forces a
plausible answer despite incomplete evidence: incompatible with repository boundaries.

One pending candidate: retain precise failure location/evidence and revalidate only
affected artifacts in existing eval pipeline. Small fixture cost; minimum test
must distinguish hypothesized cause from executed intervention and original finding
closure. Reject automatic causal labels or forced answers. No repository gain proven.
