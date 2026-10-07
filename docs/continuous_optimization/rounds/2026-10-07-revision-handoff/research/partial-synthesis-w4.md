# In-progress shared mechanism table — 2/10, not completed synthesis

| Paper | Prerequisites / mechanism | Evidence / cost | Failure / relationship | Decision and repo mapping |
|---|---|---|---|---|
| AgentDropout v1 | Train round-specific participation/edges | Tables 1–7; training/sample cost | Strong pruning can harm; repair edges need independent coverage | Learned pruning rejected here; required-edge controls pending in communication eval |
| Optima v1 | Weight training; quality/token/readability objectives | Tables 1–3, C, E; training overhead | Short unreadable messages impede correction; no durable/tool recovery test | Training rejected; compact sufficient evidence vs omission control pending in existing pipeline |

Complementary inference: route only necessary participants while retaining repair
evidence. Neither demonstrates local transactional recovery or justifies removing
mandatory independent acceptance. Eight more complementary papers required; do
not extrapolate their benchmark gains into repository results. Full notes record
actual reading and limits.

| AgentSpec | Explicit observable action predicates | Tables4/6 tradeoffs; §6.3 no long-horizon prediction | Hook and predicate maintenance; reflection/human latency extra | Missed contexts/overblocking; no crash atomicity | Complements retained-evidence rules; does not replace retry intent | Test scoped existing adapter preconditions; reject importing DSL/runtime |

| SagaLLM | Compensable domain actions and durable state | Four selected planning cases; qualitative Table10, no cost/ablation proof here | Coordinator and domain compensation code | Unverified compensation/ownership; cannot undo every external effect | Supports history preservation alongside preconditions; conflicts with duplicating Engine state | Pending dependent-only actual repair/recheck; reject runtime import |
