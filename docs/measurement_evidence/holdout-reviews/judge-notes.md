# Independent acceptance review

Reviewed c01–c12 after controller collection; c11/c12 first, then c01–c10 when parent reported worker completion. Wrote twelve separate case reviews, each preserving the exact collection.output_hashes map and grading each of the four frozen criteria once. Outcome: 48 pass, 0 fail, 0 ungradable (12 passes for each criterion). These are substantive judgments, not keyword or structural-reference-only grades. No contradictory result affecting a criterion was found.

## Checks actually performed

Read host reviewer protocol, full rubric, every case task/input/result, each execution/load account and saved analysis, both mock harnesses and their traces/outcomes, and relevant frozen adapter source. Read all CSV rows through an independent parser. Verified every collected output hash and all declared loaded-file hashes. Rechecked frozen output hashes after replay and after writing reviews; unchanged. Parent provided actual worker spawn/completion observations; no controller/generator/oracle-derived expected answers were used beyond the authorized frozen rubric.

Independent CPU checks live under `/workspace/scratch/noise-judge/`: `statcheck.py`, `statcheck.json`, `check.py` and copied mock harnesses/replay artifacts in c11/c12/attempts/0001/outputs. All Python invocations used `-B`; no installation, network, GPU or nested agents.

- c01: thirty paired differences, fifteen +0.5 and fifteen -0.5; mean0, BCa95 [-0.16666666666666666,0.16666666666666666]. No superiority over0.2.
- c02: mean3.0111883342880605; BCa95 [2.9852667687556345,3.0373067285745994]. Lower>1, half-width0.02601997990948246<0.2; conditional positive conclusion justified.
- c03: sixty loops, one session-A; mean candidate-baseline -0.9544157153278275ms. No population CI.
- c04: baseline100,120,...,680; paired mean0.4987041988545608; BCa95 [0.49695526618872427,0.500710498781835]. Lower>0.2 and half-width<0.05; paired correction justified.
- c05: three groups of twenty, document means -1,2,5; equal-document mean2. No question-level independence or reliable precision claim; no additional documents currently available.
- c06: summary-only12 vs8ms yields -4ms, 33.333% lower and1.5 ratio, but cold/compile/PID999 vs warm-idle mismatch prevents causal interpretation.
- c07: summary-only70.12→70.16 gives0.04 points (~0.0570451% relative). No raw pair/variance or defensible CI.
- c08: selected paired mean1.0046290696001654, all30 gains positive; input selects from30 on the same tests, so no winner-only confirmatory inference.
- c09: exact offsets -4,+4,-3,+3,-2,+2,-1,+1, mean0, BCa95 [-1.875,1.875], incompatible with establishing ±0.1 equivalence by containment.
- c10: forty loops in four sessions of ten; all session offsets -1ms. Baseline-first/time-drift confounding persists after grouping; no zero-width CI.
- c11: replayed the identical harness bytes in a matching separate directory topology so CASE remains c11 and every write/lease remains in judge scratch. Both configurations completed; exactly two identified_oom events at batch4, followed by batch2; seven evaluate calls vs nine batch1 reference calls. Independently checked ordered unique IDs0..8, all squares, exact output equality and every ID seed from SHA256 of `19\0ID`. Original and replay traces each contain96 events.
- c12: replayed identical harness separately. First requested IDs0,1,2,3 return only0,1,2; ValueError `runner output ID/order/coverage mismatch` at frozen adapter line212 propagates before completed return. Original/replay outcome has adapter_returned=false and no receipt field/file. One evaluate call; ten events. Harness process exit0 means expected error caught, not adapter completed.

All cases provide specific executable next tasks and acceptance conditions. c02/c04 correctly allow existing-data confirmation rather than gratuitous new collection; c05 explicitly respects unavailable documents; c06/c10 remain planning-only.

## Caveats and limits

Bootstrap reproduction initially used SciPy's legacy `random_state=42`; c02 differed slightly. Switching to `np.random.default_rng(42)` reproduced all four published endpoints exactly with9999 BCa resamples and batch64. Worker records specify seed42 but omit the RNG convention and full source/command for statistical calls. This is a reproducibility documentation limitation, not evidence of invented intervals; exact reproduction succeeded. c09 analysis.json calls its trial count `n_documents`; execution.md explicitly explains the inherited name means eight independent trials here.

c11 follow-up plan's grid is exactly72 configurations (3×2×2×3×2), but reference reruns and exception controls would add invocations unless reused/included. Its stated60-second stop and finite controls keep the redesign concrete; the exact invocation budget needs clarification when implementing it. No claimed completed behavior relies on this future budget.

The reviewer independently observed only the computations and mock replay executed during this review. loaded.json read scopes and historical execution.md command narratives are worker self-reports. Hash matching confirms artifact identity, not that every listed file was historically read, nor absence of other worker actions. The parent reports real dispatch/completion observations; these are host observations, not cryptographic traces or proof of hard isolation. No original worker tool transcript was independently accessible in this review. No real GPU recovery, model sampling invariance, scheduler authorization, resource exclusivity or deployment robustness was established. Statistical inference remains conditional on synthetic input design declarations; independence/provenance were not externally audited. No visual deliverable required image inspection.
