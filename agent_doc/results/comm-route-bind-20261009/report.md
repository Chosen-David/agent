# Route field binding — 2026-10-09

**Outcome: rejected for adoption; runtime remains exact baseline.** Both current1000-route primary gains passed, but one mandatory producer single-route guarded publish regressed. All four cohorts and every sample retained; no performance retry or threshold change. This is accepted negative evidence, not a deployed communication upgrade.

Baseline main0a532bf447936fd7c07d0d97779a600c6a764905; fresh main67f3d6cedff0537e5f2a570098e4296222515866 adds unrelated MATH64 knowledge/docs only, communication/source/harness unchanged. Those concurrent changes were preserved. Candidate binds sender/task_id/kind once per public publish, uses all3 short-circuit comparisons against current plan and preserves sorted fanout. Strong comparator reapplies oldr12 to current source; originalr12/r13 negatives/timings untouched. Ordinary loop-invariant Python optimization; no scientific novelty or AECP/HEAR/ABCAgent implementation claimed.

| Cohort | Events | Routes | Reference ms | Candidate ms | Ratio | Primary gain | All guards |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| producer_current | 100 | 1 | 1.140818 | 1.278760 | 0.892128 | not required | FAIL |
| producer_current | 20000 | 1 | 0.862374 | 0.837691 | 1.029466 | not required | pass |
| producer_current | 100 | 1000 | 1.268465 | 0.790852 | 1.603922 | pass | pass |
| producer_strong | 100 | 1 | 0.858873 | 0.856458 | 1.002820 | not required | pass |
| producer_strong | 20000 | 1 | 0.771991 | 0.843546 | 0.915174 | not required | pass |
| producer_strong | 100 | 1000 | 0.927748 | 0.880033 | 1.054220 | not required | pass |
| independent_current | 100 | 1 | 0.717659 | 0.761645 | 0.942249 | not required | pass |
| independent_current | 20000 | 1 | 0.935993 | 0.853082 | 1.097190 | not required | pass |
| independent_current | 100 | 1000 | 1.527138 | 1.031742 | 1.480155 | pass | pass |
| independent_strong | 100 | 1 | 0.790544 | 0.751652 | 1.051742 | not required | pass |
| independent_strong | 20000 | 1 | 1.343153 | 1.518135 | 0.884739 | not required | pass |
| independent_strong | 100 | 1000 | 0.924938 | 0.862083 | 1.072911 | not required | pass |

Frozen primary: current100-event/1000-route full publicpublish requires >=1.25x and >=0.05ms in BOTH producer and independent. Strong comparison is a nonregression guard. Every shape/cohort additionally guards publicpublish and fresh-write publish/ACK: candidate<=1.25*reference OR delta<0.2ms. Failing producer_current100/1route fresh-write publish:0.799387→1.153993ms (+0.354606ms,1.443597x), so keep=false even though current primary gains1.603922x and1.480155x pass. Shared-host variance is a limitation, not permission to discard this gate or rerun for a better number.

Each of4cohorts has31 alternating pairs/3warmups. Full API includes refs/connection/transaction; SQL VM/change counters and storage equal, unchangedDDL maintenance/reopen/migration diagnostic only. Profileoutside latency selected baseline routegenerator2002calls;strong/candidate0. Complete ranges/guards/diagnostics in independent_decision.json; no isolated loop timing substitutes for publicmethod latency.

Independent checks:61 public properties,218 route assertions and2 existing regressions on EACH of3sources; frozen2 route-authority tests also pass each source. All cohorts run25 communication/usage tests. Route oracle covers all3keys,partialmatch/unmatched,sorted unique fanout,liveplan changes,duplicateimmutability/refrevalidation andatomic rejection. Native6criteria proofSHA b98504a066ad63988d376f90421243a79b0a9b5fc2a8905d8c64ff0fedbb0d9e authenticated by actual /root/route_bind_verify run comm-route-bind-independent-20261009, then registered natively. Hash alone is not reviewer authentication.

Failures retained: v1 plan review revise, v2 accepted before measurements. Original profile.py launch shadowed stdlibprofile beforefixtures; identical frozen script succeeded with python -P, no source or paireddata change. Independent helper initialduplicateconstructorfixture was correctlyrejected;attempt1log retained, only helper validinitialplan corrected. No performance retries.

Negative branch: actual runtime/test suite untouched; proposed integration_tests.py stays evidence-only, no new fullsuite/integration result claimed. Preregistered integration contract remains unused by design because keep=false. Local sharedCPU/warmcache synthetic SQLite evidence does not establish network/LLM/token/quality/physicalI/O/remote deployment gains. Human guide and SGLang unchanged.

Primary research screening and subsequent reading scopes/mismatches in research.md,screening_followup.md,post_negative_screening.md. Broad continuous optimization remains active; next eligible tests need new frozen plan/budget: characterize connection lifetime and concurrency boundaries or task-grounded controller outcome/cost fixtures; untested, not completed improvements.
