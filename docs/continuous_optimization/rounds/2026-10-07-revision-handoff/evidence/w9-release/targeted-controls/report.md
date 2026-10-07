# W9 targeted local controls

Actual revalidation reused W8 consumer setup/consume/guard/LocalHandler bodies against the current local runtime. The original CLI is not parameterized: hardcoded W8 paths, old candidate identity assertions and raw capability logs made verbatim reuse unsuitable. Main explicitly authorized ephemeral relocation after this limitation was reported. Only OUT and PRIVATE assignments changed in a private temporary script; AST checks confirm all function/class bodies are identical. The checked-in adaptation.diff and identity.json bind original/adapted scripts, current runtime/core, current commit and frozen V3 workflow hashes. Existing W8 task hash remains a synthetic fixture authorization reference inside unchanged code; this is not a claim that V3 identity was checked by W8 main(), which was not called.

Actual driver procedure: compile/exec the relocated file with __name__=w9_relocated_consumer, then invoke setup('budget') and setup('conflict'). Their unchanged Engine/Context guards and real subprocess consumers ran in fresh owned directories outside the repository. Budget child exited 3; conflict child exited 4, exactly as expected. Both parent setup assertions and separate post-run state assertions passed. Raw command/Engine/lease logs remain only in mode-0700 private temporary storage. Public command records redact token/idempotency values; no lease capability is published.

| Control | Actual observation |
|---|---|
| Event budget exhausted | Outgoing publish rejected; exactly one seed event remained; original receipt null and consumer inbox still contains original; zero new ACK, zero successful outgoing publication. |
| Conflicting receipt | Preflight stopped; existing rejected receipt unchanged and distinct from saved needs_revision intent; exactly one seed event; zero new event or ACK. |
| Stale reference | Existing unittest test_reference_changed_after_delivery ran using a fresh TemporaryDirectory; consuming mutated referenced artifact raised sha256 mismatch and original remained pending. Exit 0, one test passed. |

Actual stale command: python -B -m unittest -v tests.test_communication.CommunicationTests.test_reference_changed_after_delivery, cwd repository root. Commands/stdout/stderr/exit codes and private record hashes are in scenario JSON files. Local control execution took under one second, within the two-minute CPU budget. No interruption test was needed; no model-session restart, performance gain, external exactly-once behavior, scientific closure, all-adapter migration, or representative-role rerun is claimed. No runtime or production code changed.

Initial navigation failure retained: rg --files docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/w8-candidate from workspace root reported missing directory. Repository was then located at agent/; this did not run any control or affect results.
