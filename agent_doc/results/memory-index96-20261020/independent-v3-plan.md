# Independent native-v3 protocol reconciliation

Reviewer `/root/memory_index_verifier`; manual native host context; producer `/root`.

Approve the scoped native-v3 repair/measurement protocol in `validation_plan-native-v3.json` (SHA256 `00ce24b9874b4dfc180c0906b87fa6a8bd7e2f4fb1a7613bb4e69fdcd7259ce4`). It preserves the six original fixture workloads and restrictions, adds the previously agreed local tokenizer observation, and fixes the independently observed Windows newline mismatch. No model request, GPU, paid inference, background service, new persistence/cache architecture or total-token claim is authorized by this approval.

The initial LF-only byte/token measurements remain historical and superseded for the exact native-wire claim. `independent-pipe-v1.json` demonstrates the former hard-cap defect (810 requested characters, 811 actually emitted with CRLF); the corrected index reserves `len(os.linesep)`. Actual binary subprocess capture with explicit UTF-8, complete native terminators, full pages and necessary body replies is the appropriate acceptance target. All source and artifact bindings require revalidation against the v3 manifests.

The v3 tokenizer identity includes exact version, encoding, mergeable-rank digest, pattern, special tokens, package files and cache data hashes. These enable reproducible local text token counts; they do not identify an unqueried serving-model accounting protocol. Full/short-body controls remain valid negative results, and token-success counters must not be promoted from this experiment.

Storage is accepted only as read-only SQL/business-state observation: live WAL readers can change SHM reader marks, independently observed in the boundary records. Physical file immutability, compaction and deletion are outside the claim.

The reviewer checker itself initially omitted commits around direct-SQL fixture mutations, causing a false refusal expectation failure. This was a harness defect, corrected with explicit transaction contexts. `independent-boundary-v1.json` and `independent-boundary-v1-harness-fix.json` retain those failed observations; they must not be presented as additional implementation defects. Corrected final properties appear in `independent-boundary-v3-pre-freeze.json`, bound to the final implementation hash.

No final experiment acceptance is implied by this plan reconciliation; independent code/data checks and applicable final regression remain required.
