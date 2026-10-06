# Independent forward test F

Task ID: `knowledge-forward-f`. Task refs: task request, `context.json`, `context-focused.json`, `context-tiny.json`, `refs.json`, `checks.json`, and `evidence.txt` in this directory. Scope was solely the supplied skill and outputs in `/tmp/knowledge-forward-f`; no repository, tests, rubric, other-agent evidence, or network was consulted. Skill files were not changed.

## Result and model

**Yes, the selected top-k membership is guaranteed under the stated spectral error premise**, interpreting selection as the k largest raw inner-product scores, with a common finite candidate set, `1 <= k < n`, and the stated .14 as the exact original k/(k+1) boundary gap. Let K and Khat be real d-by-n matrices with aligned key columns, q the same real d-vector for both evaluations, and s=K^T q, shat=Khat^T q.

With e=s-shat, the induced Euclidean matrix norm gives

`||e||_2 <= ||(K-Khat)^T||_2 ||q||_2 <= .02 * 4 = .08`.

For any distinct coordinates i,j, Cauchy–Schwarz gives

`|e_i-e_j| <= ||u_i-u_j||_2 ||e||_2 <= sqrt(2)*.08 = .11313708498984762`.

Every originally selected i and unselected j satisfy `s_i-s_j >= .14`, so

`shat_i-shat_j >= .14-.11313708498984762 = .026862915010152394 > 0`.

All cross-boundary comparisons remain strict. This guarantees membership, not internal ordering. The generic coordinatewise route would give epsilon=.08 and demand `.14 > 2*.08=.16`, which fails; that route is inconclusive, not evidence of failure. Keeping the joint error structure resolves the question.

## Premises and applicability

| Premise | Task mapping | Status / importance |
|---|---|---|
| Real, dimension-compatible objects and column keys | K,Khat in R^(d by n), q in R^d | Given/model interpretation; makes s=K^Tq valid |
| Same candidate identities and finite top-k selection | 1<=k<n, largest raw inner products | Implicit in boundary-gap wording; conclusion is conditional on this interpretation |
| Fixed query in both evaluations | q unchanged, ||q||_2<=4 | Given; changed q needs an additional error term |
| Spectral/operator norm of full residual <=.02 | ||K-Khat||_2<=.02 | Given; yields a joint bound on all score errors |
| Original boundary gap .14 | s_(k)-s_(k+1)=.14 | Given; exceeds the sharp joint threshold strictly |
| Exact modeled scoring, or all additional errors covered | Scores are those of the matrices and fixed q | Any extra numerical or transformation errors need accounting |
| Approximation is truncated SVD or low rank | Not stated | Not needed; no SVD theorem used |

Norm labels matter: a bound on a mean sampled error is not the full spectral bound or a uniform coordinate bound. Strict gap matters; equality at the threshold can create a tie. No statistical assumptions, distributional model, SVD optimality, or speedup premise is required here.

## Mean sampled score error .005

**The same guarantee does not follow if .005 mean sampled error replaces the spectral premise.** Even if “mean error” means mean absolute error and is known over the entire population, rare boundary errors can change membership.

For n=32 and k=1, take original scores `(.14,0,-1,...,-1)` and approximate scores `(.06,.08,-1,...,-1)`. There are two absolute errors of .08 and 30 zeros, so the population mean absolute error is `.16/32=.005`, but top-1 changes from coordinate 1 to 2. A sampled mean cannot exclude these outliers; signed means are weaker still. This example is realizable with q=4 and one-row matrices equal to these score rows divided by 4. Its matrix spectral error is `.0282842712474619`, exceeding .02, so it does not contradict the first guarantee. If the spectral premise remains known and .005 is merely additional information, membership remains guaranteed from the spectral premise.

## Retrieval and selection

Built persistent SQLite index `/tmp/knowledge-forward-f/search.sqlite` from the explicit supplied corpus. Initial build indexed 10 entries. A later repeat reported all 10 unchanged, verifying reuse. Query was:

`real column key matrix approximation spectral error fixed query norm boundary gap top-k membership mean sampled score error`

The normal context call used max-entries 8 and max-chars 40000. It returned `ready`, `applicability: unchecked`, 6616 payload characters, and direct retrieved IDs `math.score-difference-bound`, `math.low-rank-svd`, and `math.topk-margin`; Cauchy–Schwarz was a prerequisite. Applicability was assessed above, independently of ranking.

A focused context call used the same index/query with `--limit 1`, max-entries 8 and max-chars 40000. It returned `ready`, 6612 payload characters, no skipped entries, with this distinction:

| Entry | Context selection_reason | Actual use |
|---|---|---|
| math.score-difference-bound | retrieved | Main joint norm argument |
| math.cauchy-schwarz | prerequisite | Strong prerequisite, read in full |
| math.topk-margin | related | Membership interpretation and conservative baseline |
| math.low-rank-svd | related | Inspected but excluded as unnecessary |

The focused call's only `retrieved_ids` entry was `math.score-difference-bound`. Related entries were not misreported as direct retrieval hits. All three used entries were also read through `show`; their returned references were deduplicated into `refs.json`, retaining the complete strong dependency closure. The unused SVD reference remains in raw context evidence but not in the actual-use refs file. `check-refs` returned valid.

## Small budget behavior and checks

Deliberately repeated normal context with max-chars 100. It returned `status: partial`, zero used payload characters, no entries, and no knowledge_refs. Every original candidate appeared under skipped with reason `complete prerequisite bundle exceeds context budget`; Cauchy–Schwarz also appeared as skipped related material. This reports missing evidence explicitly and does not silently strip a theorem's premises. The tiny result alone is insufficient evidence for the conclusion; the full ready output supplied that evidence.

Executed `checks.py` and saved `checks.json`: all assertions passed. Checks covered the .08/.113137/.026863 arithmetic, a one-row matrix example attaining the worst pairwise error with spectral norm .02 while preserving membership, the .005 mean-absolute-error failure example, context selection roles, complete prerequisites, actual-use reference set, and explicit tiny-budget incompleteness. `evidence.txt` contains actual show/index/check-refs outputs and raw context responses. No Lean/proof assistant or performance benchmark was run, and no formal-proof or speedup claim is made. Knowledge-entry metadata mentioning earlier tests is source metadata, not a claim those tests were executed here.

No unresolved blocker. Parent can incorporate these results and artifacts into its final acceptance work.
