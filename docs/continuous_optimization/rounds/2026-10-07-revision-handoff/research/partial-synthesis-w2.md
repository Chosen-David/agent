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
