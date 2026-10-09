# Task-local inbox observations

When the trusted host dispatches a local task to a recipient that also handles other tasks, it can select that exact task before pagination:

```python
messages = mailbox.inbox("writer", task_id="FIG-1", limit=20)
```

```powershell
python -m agent_runtime.communication --root ABSOLUTE_PROJECT_ROOT --db messages.sqlite --plan plan.json inbox writer --task-id FIG-1
```

The selected task must be explicitly routed to that recipient. All message kinds, fields and references are preserved. Scope selection performs no ACK, semantic validation or task completion. Other tasks remain pending. The default unscoped interface is unchanged. Both interfaces are paginated; an empty or partial scoped list cannot establish global clearance or completed work. Main coordination must check the full inbox/status and actual cross-task dependencies. Shared blockers must reach the true affected tasks or coordinator; producers do not choose a narrower consumer scope.

This reduces unrelated observation acquisition before a local model turn. It is distinct from claim-key encoding, validation receipts, instruction deduplication and tool catalogue exposure. Existing prepare_context/consume reference and independent result gates remain necessary.

Primary research: [OpenCodeReview, arXiv 2608.09290v1](https://arxiv.org/html/2608.09290v1), methods 3.2–3.3, describes deterministic dispatch and bounded review tools. Its file exclusions and model/benchmark results are not adopted here. Our explicit task filter is a library change, not a reproduction of that whole review system.

One short synthetic FIG-1 handling pair used actual default/scoped CLI observations and real gpt-6.1-sol/high provider accounting: total input+output 20,148 → 19,709 (−439; inputs −417, outputs −22), pair spend 39,857, cached input 0. Both retained the exact unresolved blocker and correction actions. Actual non-task instruction plaintext and zero external tool catalogs match. Four scope and 16 existing communication tests passed independently. Additional WSL regression passed all 42 scoped/basic/adaptive/batch/usage/generated-reference tests; the older suite's 15 Windows file-cleanup errors also reproduce with unchanged main source, and no test was weakened. [Result bundle](../../agent_doc/results/token-005-inbox-20261010/) preserves frozen sources, raw logs, plan and verification. Long-document quality, full communication graph cost, population averages, prices, and this chat/development cost are unmeasured. An adapter must explicitly opt into task selection; installation alone does not prove every model host uses it.
