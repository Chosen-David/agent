# MEMORY-RECONCILE-COUNT-01

SYSTEM-99 Plan50 checkpoint; baseline139ae9e1, candidate project_memory SHA1f0fe4edc8abf2371972817083c2c12cc33dbb07640ed57dffc2d8a744b35e41. In-place temporal-sibling statistics now reuse a sorted distinct-ID union for repeated scope signatures; one-use signatures retain direct counting. No legacy production copy, persistent cache, memory policy/schema change or automatic correction. Original row/scope order, strict timestamps, custom duplicate-ID self exclusion and overlapping-scope deduplication remain intact.

## Actual acceptance

Baseline, fixed and independent each passed36methods/no skips. This is an efficiency baseline, not a pre-fix correctness failure. Exact tests/benchmark/input versions and full raw5samples/layout are retained. New portable CLI assertions execute actual reconcile body and budget refusal under cp936/ascii; four native CI matrix results remain pending at publication. No old full-suite/probe/host budget was reopened.

Full SQLite reconcile API medians (seconds),1600entries per layout, five sequential observations per condition:

| Layout | Baseline | Fixed | Independent | Fixed/baseline |
| --- | ---: | ---: | ---: | ---: |
| One shared signature | .395823 | .028245 | .029204 | .07136 |
| 32 overlapping signatures | .450454 | .036075 | .038906 | .08009 |
| 1600 unique+common signatures | .453601 | .368197 | .330255 | .81172 |

The repeated-signature cases observed about92–93% lower median time on this synthetic ledger. Independent medians also meet all frozen guards. The unique-signature negative control passes its <=1.25 ratio guard; its apparent improvement is not attributed to the optimization. All fixture/schema/normalized ordered output identities match; database bytes remain unchanged. See summary.json and independent result-review.md for exact ratios/checks.

## Validity and remaining scope

Shared CPU, sequential phases, no affinity change, no warmup/randomization, five observations and uncontrolled load/cache/frequency do not establish significance or general speedups. Slow baseline observations remain in raw data. Timing includes hydration and JSON-budget construction; excludes fixture setup, hashes and oracle checks. Three all-common synthetic layouts have no dependency edges. New correctness controls include corrections/status/snapshots/contradictions, but real model task quality, delivered context, tokens, billing, host installation and other distributions remain unknown. No memory-usage improvement is measured.

The first plan review required the formal experiment contract and schema evidence; its full revise response and Version1 remain preserved. Final approval precedes baseline. Producer→verify_experiment_result→publication bindings and six criteria are frozen. Actual separate-context delegated source/raw-data review accepted this finite scope; it is not authenticated runtime ReviewSession proof. Registration without a trusted provider remains pending and cannot authorize cross-task numerical reuse.

Related working-memory literature informs separation of management cost from delivery/outcomes, not this algorithm or local speed ratios. Standard precomputed-key bisection is an engineering optimization, not a claimed novel research method. No fresh paper credit (recoverable19 unchanged). System batch remains unfinished; no competing TASK/guide edits, architecture migration or old budget reset. Runner/benchmark text archives preserve actual source bytes at original private execution paths; they are not new production implementations or automatically authorized replays.
