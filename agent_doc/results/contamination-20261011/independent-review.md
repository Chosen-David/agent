# Independent review record

Reviewer: actual fresh collaboration context `/root/review` in this execution session. Main AI transcribed the returned findings below; this is not a fabricated `ReviewSession` receipt and does not claim a deployed dual-main runtime adapter.

Initial finding (blocking): evidence archival occurred before stop, so an archival OSError escaped and left the confirmed bad job running. Reviewer reproduced by patching atomic_write only for `/evidence/`. Fixed by stopping before archival. Initial revocation persistence failure now attempts exact stop and returns `durable=false`, blocked, without cleanup/restart. Both paths have executable regression tests.

Final reviewer result: approved affected code scope, no remaining blocking finding; independently ran contamination tests 17/17 and result-related tests 79/79. Actual pidfd stop and unrelated-process survival, repaired CPU execution, persisted revocation gates, cached acceptance refusal and replacement deduplication were covered. Tests before/after had matching SHA256:

```
ac9eb1d05cc69c4e3f054c8aeff76c4b1d353138feae93232f88f662e92fa82a  agent_runtime/contamination.py
a6e9b855d5284ca91c311223b7e45523ed4062ff155848662c0697a1b82f0126  agent_runtime/result_store.py
0c583d8fab12fcfaa4c7482ac4b696da687f5c9b1733459eb32dd2a6413610f4  agent_runtime/result_validation.py
2c11be3ae8a0699a27751e11d70d46bda368baea084f84ae41f76f8416a6729f  tests/test_contamination.py
```

Limits: POSIX file locks; external scheduler/multirank stop/fencing, actual ownership and complete reference closure remain trusted host responsibilities. Shared leaderboard transactional invalidation needs the original system. No model/GPU runs or external adapter deployment was performed. Process-restart recovery is tested; power-loss multi-file transaction guarantees are not claimed. This review does not waive full-repository checks or CI.
