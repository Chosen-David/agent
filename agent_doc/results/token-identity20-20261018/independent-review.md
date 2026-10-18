# Independent bounded result review

Reviewer: host collaboration context `/root/usage_identity_review`, distinct from implementation producer. Manual source/test review; not native ReviewSession authentication or automatic result-validation backend.

Verdict: **usable-with-scope** for rejecting empty/non-string requested thread/turn identities before events iteration in both accounting entrypoints, preserving inspected valid accounting behavior. No blocking findings.

Read AGENTS.md, decision review, dual-main and result-validation instructions, current tests, prior TOKEN-TOTAL-18 record and current source diff. Prior strict-counter results do not validate the new identity domain, so fresh targeted checks were necessary. The patch adds only identical two-line entry guards in both functions; downstream accounting remains unchanged. No normalization or nonempty opaque-ID restrictions are introduced. The existing JSONL helper uses the same nonempty-string convention.

Baseline reference: git HEAD `22053c039fe0a71a6cfb28a5ecbbb7d2449bed18`, loaded with `git show` into separate namespaces without changing production files. Independent reproduction distinguishes the producer's initial four-method suite (26 failing subtests, no errors) from the final five-method suite (27 failures, no errors). The added pre-iteration method contributes one failure because its first parser raises AssertionError and aborts the method. These are expected baseline failures, not candidate defects. Candidate final five methods pass.

Independent ordinary and Python -O targeted runs each pass all 21 methods in tests.test_usage_identity, tests.test_prompt_context and tests.test_turn_usage. Additional independent 62 checks pass: valid requested IDs with each event identity location missing; both invalid identity axes rejected before calling __iter__; full baseline/candidate output equality and unchanged input for opaque/whitespace IDs and zero/large valid counters; inherited totals accepted by current-turn accounting with exact output parity and rejected by fresh-turn accounting.

Offline archived native trace replay also passes four complete-output comparisons (two parsers times baseline.rpc.jsonl and candidate.rpc.jsonl from token-fifty-06-20261012). Identities were extracted from actual turn/started events. Returned totals remain 15996 and 15164 respectively. These are historical trace compatibility observations, not fresh inference results or token-savings measurements.

Evidence: independent_check.py; independent-check.json (actual source/test SHA256 bindings); baseline-initial-independent.log; baseline-final-independent.log; candidate-final-independent.log; independent-targeted.log; independent-targeted-O.log; independent_archived.py; independent-archived.json (archived trace SHA256 bindings). All reside in this directory.

Validation dimensions: implementation PASS (actual guards and unchanged downstream code); reference/boundary PASS (baseline differential, explicit identities, preserved accounting); data integrity PASS (initial/final cases distinguished, actual raw logs inspected, code/trace hashes captured); numerical sanity PASS (exact integer output comparison, zero/inherited controls); measurement validity N/A (no performance measurement or claim); reproducibility PASS (independent baseline, candidate and optimized-mode execution).

Limitations: finite local tests and two archived traces do not establish universal transport validity, production deployment, historical contamination, model quality, token/cash savings or performance improvement. No live model/API call. Full-repository regression and remote publication readback remain the parent owner's separate acceptance steps. No production or task-index files were edited by this reviewer.
