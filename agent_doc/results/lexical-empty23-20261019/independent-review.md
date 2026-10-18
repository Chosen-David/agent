# LEXICAL-EMPTY-23 independent result review

Verdict: usable-with-scope. Independent delegated reviewer: /root/lexical23_review. Manual review, not native ReviewSession certification.

Scope: already-loaded file-backed KnowledgeStore.search on the fixed 115-record corpus and nine specified queries. No CLI-startup, model-inference, or real-task quality claim.

## Six checks

- implementation: pass. Actual three-line fast path follows unchanged query/limit validation and NFKC tokenization. Empty-set intersection cannot score any row. Exact response envelope preserved. Nonempty path unchanged; plugin mirror byte-identical.
- reference_boundary: pass. Read baseline directly from Git 33ff30a0e068c4ad6e17cb6bf18a79b041fdef11; independently instantiated old and current stores match. 144 normal/invalid query/options cases matched whole output or exception type/message. Replayed baseline test module against entire old module: six expected failures (661/691 tokenizations versus one); candidate three tests pass.
- data_integrity: pass. Both rounds contain metadata plus all nine ordered unique queries, seven alternating AB/BA pairs each. Independently checked source/input/snapshot hashes, baseline outputs, and output hashes. No samples dropped.
- numerical_sanity: pass. All timing values finite and positive. Recomputed every median, reduction, threshold and pass result. Both rounds satisfy all frozen thresholds.
- measurement_validity: pass with scope. Inspected complete runner: load excluded; full search calls; one warmup pair then seven paired rounds; five calls per sample divided by 5e6 to ms/call. Same list allocation/retention overhead for both variants, equality checks outside timer. Recorded raw samples are five-call means; individual-call and warmup durations are not stored.
- reproducibility: pass. Independently executed PYTHONHASHSEED=0 python scripts/benchmark_knowledge_empty_query.py > agent_doc/results/lexical-empty23-20261019/independent.jsonl; exit 0. All thresholds passed without rerunning/selecting timing rounds.

## Limitations and documentation reconciliation

Primary producer disclosed one concurrent 0.16-second read-only result-store retrieval. Raw outliers retained. Independent timing completed before main agent started full tests; external host contention is not ruled out. Microsecond fast-path observations contain Python loop/list overhead and are not universal stable latency predictions. Non-regression covers tested queries and tolerances. Full repository regression/publication remain main-agent responsibilities.

Task-ID/Date metadata were added to the detail and TASK line endings repaired after original plan review. Re-read corrected identity; technical Plan and thresholds remain unchanged. Earlier plan-review hashes are historical, not hashes of the revised document. Current evidence hashes below bind this review. Initial reviewer baseline-test replay patched only the search method, leaving exception-module identities mismatched; that harness assertion failed. Corrected by binding the test module to the complete Git baseline module, yielding the intended six failures and no errors; no product changes or timing reruns followed.

## Median milliseconds per call

| Round | Query | Baseline | Candidate |
|---|---|---:|---:|
| raw.jsonl | !!! | 60.327336000 | 0.003188200 |
| raw.jsonl | 🙂 | 56.631497000 | 0.003458800 |
| raw.jsonl | Ω | 54.825490400 | 0.003295200 |
| raw.jsonl | memory retrieval | 55.398461600 | 55.837179800 |
| raw.jsonl | low rank | 56.566260800 | 55.961503400 |
| raw.jsonl | 量纲 | 76.514441200 | 74.903525600 |
| raw.jsonl | topk | 88.180532800 | 81.805056800 |
| raw.jsonl | zzqxnonexistent | 74.128743200 | 71.821253600 |
| raw.jsonl | ＡＢＣ | 66.561052400 | 63.755654400 |
| independent.jsonl | !!! | 59.499916000 | 0.003158600 |
| independent.jsonl | 🙂 | 65.215644000 | 0.003672000 |
| independent.jsonl | Ω | 63.324634200 | 0.003371800 |
| independent.jsonl | memory retrieval | 73.774672000 | 65.554518600 |
| independent.jsonl | low rank | 58.877726000 | 61.271860800 |
| independent.jsonl | 量纲 | 59.204359200 | 55.896227600 |
| independent.jsonl | topk | 50.985752200 | 52.518209800 |
| independent.jsonl | zzqxnonexistent | 52.197066000 | 52.616461200 |
| independent.jsonl | ＡＢＣ | 52.040901800 | 54.265327000 |

## Evidence SHA256

- Git baseline source: `0f83bb00568a0e26eaf0b49d73dab1d6f958acebd1e95d749c6bb8cc9a1014b7`
- `agent_runtime/knowledge.py`: `2ac2a75bd06f3b420e937e9185b0f5ad70592205a91d7fd231fab4fdb2d89391`
- `plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge.py`: `2ac2a75bd06f3b420e937e9185b0f5ad70592205a91d7fd231fab4fdb2d89391`
- `scripts/benchmark_knowledge_empty_query.py`: `5364a4253b2a851bc65a6de809d2eb54fa2e42c78a97700e358349ea2e1eb8a5`
- `tests/test_knowledge_empty_query.py`: `3ede7e879836453e658131e60b6e8b94ec8d029398292104505115fbea838ec8`
- `agent_doc/task/TASK.md`: `5ac8418799d0d71707aee392c235ba3326f3d526dd52ccbebc3563543f83c0e2`
- `agent_doc/task/task_details/LEXICAL-EMPTY-23.md`: `b45105f0a739368f60df393fb5aaa9d52da5afcaf40c1ff1de239e27fcd4ac40`
- `agent_doc/results/lexical-empty23-20261019/raw.jsonl`: `98efbf01f221513a3eced2db212dc02c94f31305329d3198f76a6f40c589e3e4`
- `agent_doc/results/lexical-empty23-20261019/independent.jsonl`: `02df1228bcb093c8ddbbb6e96375161b197c3b1c62469f5cf056d3c2ef704fa2`
- `.agent-runs/lexical-empty23/before.log`: `80216ea3ebc6708dded26f774f7baacfbee0d37b7fc298810c5fd8fec096f6c0`
- `.agent-runs/lexical-empty23/after.log`: `9c2dcdbed803180dd4999ac35e5b9b9f6dc50e14da044d05f59dac4152878a7a`

## Independent targeted test replay

Baseline:
```
FFFFFF..
======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='!!!', options={})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 661 != 1

======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='!!!', options={'limit': 20, 'include_unpublished': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 691 != 1

======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='🙂', options={})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 661 != 1

======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='🙂', options={'limit': 20, 'include_unpublished': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 691 != 1

======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='Ω', options={})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 661 != 1

======================================================================
FAIL: test_empty_terms_skip_document_tokenization (test.EmptyQueryTests.test_empty_terms_skip_document_tokenization) (query='Ω', options={'limit': 20, 'include_unpublished': True})
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/workspace/scratch/88c3234ecfbc/agent-memory/tests/test_knowledge_empty_query.py", line 27, in test_empty_terms_skip_document_tokenization
    self.assertEqual(tokenize.call_count, 1)
AssertionError: 691 != 1

----------------------------------------------------------------------
Ran 3 tests in 0.749s

FAILED (failures=6)
```

Candidate:
```
...
----------------------------------------------------------------------
Ran 3 tests in 0.160s

OK
```
