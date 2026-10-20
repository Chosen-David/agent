# Diagnostic harness attempt 1

The first baseline diagnostic stopped before tests because the producer receipt's `/tmp/agent-memory-index96-final-h77donpw` snapshot no longer contained `agent_runtime/result_store.py`. No test conclusion was produced. The harness now compares extracted Git baseline against the current working checkout and records the actual cwd plus per-file hashes; it does not claim to replay the missing temporary snapshot.
