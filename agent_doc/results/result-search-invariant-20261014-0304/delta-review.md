# Independent concurrent-main reconciliation review

Verdict: APPROVE unchanged v5 candidate on integrated main66c88cd60dc4a7bf064d835f2e3c50b822f8b2cd, pending completed new-base regression/report/inventory review.

Reviewed full9c071f7→66c88cd path delta:24 files limited to MATH113 result evidence/record/TASK detail, TASK index addition, knowledge coverage/learning_state and corresponding plugin snapshots. No agent_runtime, tests, Reader tests, AGENTS, prompts or workflows changed in this delta. Current staged TASK change appends RESULT-SEARCH-INVARIANT after existing MATH113, preserving concurrent entry and other history. Production source/helper equal frozen v5; root/independent/current module SHA identical.

Actual corpus grew143→144 records by one math-measure-diffusion-20261014/record.json. All previous143 record hashes remain identical. Both producer and independent timers freeze identical current144record corpus before/after execution, scanning224 directories with80 errors per case. Those errors, results, scanned/partial/status/metadata all remain equal between frozen baseline and native candidate for every observed call. New corpus is treated as changed inputs, not silently relabeled old143record timings.

Independently executed full measure.py with frozen raw-v5-serial.json after root timer completed and before new-base tests. Source/helper exact frozen matches,11 alternating pairs per each of6cases, entire returns compared to baseline per call. Recomputed all medians/reductions and positive finite timing checks from pairs. Producer new-base large reductions42.23%/38.69%; independent43.24%/39.39%, clearing declared10% gate. Controls all within10% nonregression gate; tiny control changes remain observations, not reliable gains. No timing overlapped another known root timer/regression run.

| Context | Independent baseline ms | Independent native ms | Reduction |
|---|---:|---:|---:|
| large-corpus | 170.844 | 96.965 | 43.24% |
| large-math | 151.709 | 91.958 | 39.39% |
| medium-batch | 94.653 | 91.061 | 3.79% |
| none | 91.177 | 89.796 | 1.51% |
| incomplete | 92.375 | 90.982 | 1.51% |
| unknown | 92.709 | 91.631 | 1.16% |

Existing source review and18 native boundary controls remain applicable because exact production source/helper and relevant runtime/tests/guidance paths are unchanged. This delta review does not certify MATH113's scientific contents or all historical experiment records; they are search inputs only. Scoped warm-cache CPU/local corpus, no concurrent caller mutation/model/token/cold-cache/end-to-end/quality benefit limitations remain unchanged.

New-base whole-suite/Reader completion, refreshed report, final explicit capture inventory and ordinary publication/readback remain pending. Prior full-suite results are preserved, not attributed to the new main before execution.

## Completed final delta gate

Final verdict: APPROVE exact unchanged v5/current144record result and authorized ordinary publication candidate. Independently inspected full-integrated-tests.log:1179run,1171pass,8skipped,OK; reader-integrated-tests.log:3pass,OK. Both working and staged git diff --check completed clean. Fresh report explicitly separates initial143record evidence from current144record final43.24%/39.39% measurements, carries all limitations/excluded-interference history, and does not certify old52paper reads,10newreads, model/token gains or deployed backends. Latest TASK keeps MATH113 and RESULT-SEARCH-INVARIANT pending ordinary publication/readback; task detail reports local acceptance and preserves unresolved larger continuous scope.

Read capture.py: explicit24 run artifact paths plus3 code/TASK paths; excludes early/interfered timers and unrelated work. Inventory hashing provides binding, not independent scientific/runtime authentication. Ordinary push/readback remains root-owned and unverified here. After final capture, any byte changes in approved inputs need targeted reconciliation; later truthful metadata closure may record actual publication SHA separately.

Latest individually inspected evidence hashes before capture:

```json
{
  "agent_runtime/result_store.py": "3f2a5639ac16bcb1e072f5ec06f9fbb3e2cc7cc33ff76f128acb362f2a421689",
  "agent_doc/task/TASK.md": "fedd3168c01190c463aa15ad2f361151979afe74b6c0f212781afa9f9557c456",
  "agent_doc/task/task_details/RESULT-SEARCH-INVARIANT.md": "d7d3889f4fc6c036ba2a6c9b576653c7c84633efb369dd41e1b3eebd868ee667",
  "agent_doc/results/result-search-invariant-20261014-0304/measure.py": "523ddcda5a1b49b2dc66beb39f3c83d87760f0cb71addc11f3345192ac1ddbb7",
  "agent_doc/results/result-search-invariant-20261014-0304/capture.py": "406b4d334cb21a9e0bb93b55694985ae1a22fcfbbac72d327301eb28c1183b7d",
  "agent_doc/results/result-search-invariant-20261014-0304/report.md": "8a83c1540474b7cbb19acfa6c0ce55e9b6ead662a51645eb6b729645b568e8c1",
  "agent_doc/results/result-search-invariant-20261014-0304/native-integrated-66c.json": "4b75777a5aa4e747dee54c160c45101e13bd7ff6b9e9561015775a9d5a6a3f4a",
  "agent_doc/results/result-search-invariant-20261014-0304/independent-integrated-66c.json": "4d615687196435aacab7403d3252a619de185a3790f0c4ee9d77b6cf1d7e12e5",
  "agent_doc/results/result-search-invariant-20261014-0304/full-integrated-tests.log": "4ad9accda4896b0ec940c1eaafc1fe5ec9e29ad55ef1c2b1a236879425f0ffc2",
  "agent_doc/results/result-search-invariant-20261014-0304/reader-integrated-tests.log": "00c343765bdbf273817bed76adb4d2096dfb0ac6fa6c9c783e0dcc403eba560f"
}
```
