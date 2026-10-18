# TERMS-CLASS-27 independent result review

Verdict: **usable-with-scope**. This is an independent agent review, not a native ReviewSession receipt or host supervisory attestation.

Reviewed AGENTS.md, decision review and project document instructions, the stable task Plan, production diff, benchmark code, test code, and all producer JSON files and raw sample records. Existing producer evidence was located before reproduction; explicit independent reproduction remained required.

The baseline is the actual git revision a5a13c2aea4165d0d3aebcd6c99ca0135a6efdbb (also checkout HEAD), loaded into separate module globals. Baseline indexed search explicitly binds the baseline tokenizer. Shared unchanged helpers do not substitute the candidate search or tokenizer. Candidate changes preserve normalization and token classes; query classes are determined after normalization. Projection removes only tokens incapable of intersecting the query.

Both measurements use the same frozen 238 corpus files and SQLite index, complete hot-store calls, alternating AB/BA order, two warmup pairs and eleven measured pairs per case. Construction/loading is outside timing; output comparison is outside timing. No timing wrappers artificially slow the baseline. The 20 cases are exactly the frozen backend/query/limit matrix. Independently recomputed every median, ratio, per-case gate, geometric mean and six memory gates from raw samples; checked recorded code, corpus and stable Plan hashes against current bytes.

| Round | Geometric ratio | Per-case gates | Maximum ratio | Memory gates |
|---|---:|---:|---:|---:|
| Producer | 0.7078171837307474 | 20/20 | 1.0703391257545778 | 6/6 |
| Independent | 0.7224149000975887 | 20/20 | 1.0066784879407362 | 6/6 |

Independent invocation: `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python scripts/benchmark_term_classes.py --out agent_doc/results/terms-class27/independent`. Exit 0. Main controller was notified to avoid simultaneous performance work until this completed. Host exclusivity is not guaranteed and is correctly reported false.

Full JSON equality held on every benchmark invocation; all twenty saved producer outputs equal independent outputs. Separate reviewer-authored checks added 208 full JSON comparisons spanning 13 fullwidth/Unicode/mixed queries, four filter modes (unfiltered, existing domain, existing structure, missing domain+structure), limits 1/20 and both backends. These passed. Additional 1000 seeded Unicode strings matched the authentic baseline default tokenizer and all 4000 class projections passed. SQLite hash remained unchanged through extra searches. See review_checks.py and the public per-case complete-output SHA256 manifest extended-output-hashes.json. Full raw outputs are preserved at .agent-runs/terms-class27/independent-extended-outputs.json; the check script regenerates that raw file and its manifest.

Scope limits: observed approximately 27.76% lower equal-case geometric latency ratio on this fixed hot-search benchmark; no assertion of end-to-end task, network or LLM quality gains. The mixed-query cases have no class omission and need not accelerate. Memory bounds cover two specified long strings and three class selections using tracemalloc Python allocation peaks, not total RSS. The normalization allocation remains present; this is no universal memory improvement claim. Full repository/Reader regression and publication verification remain the main controller's responsibility.

Raw SHA256: producer 9c792906f38adeb13e14b1d7fa2d1f85959c7025cc00ef2a0a9738fe1a56e99b; independent 498c4d5fd33963be3f3919c6ffeae8f455caf68916aefe66a24ab6c8af976303. Machine summary and artifact hashes: review.json.
