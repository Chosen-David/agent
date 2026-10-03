# Observable tool proxy for process-sensitive tasks

Use this supplement when the host cannot export worker tool events and a required
criterion concerns an action during execution (for example, checking a handoff
hash before writing, opening each PDF page, or analyzing code without running it).
An executor's `execution.md` alone cannot establish such a process condition.

1. Start a fresh numbered attempt through the unchanged pipeline. Give the worker
   its actual attempt path; `host_worker.md` uses `0001` only for the first attempt.
   Retain any earlier ungradable attempt and explain why it needs recovery.
2. The worker reads its pinned role and asks the controller for specific tool
   operations on its own inputs. Requests must precede the work they support.
   Keep task execution requests separate from reviewer checks and rubric content.
3. The controller inspects the requested operation, invokes the real tool, and
   saves the exact request plus available raw result, exit status and artifact
   hashes under `RUN/host/`. For visual work, actually open the rendered images;
   retain page identity, image hashes and concrete observations. Do not fabricate
   omitted events or label a later replay as the original execution.
4. Return that result to the requesting worker, with read access to its own proxy
   record. The worker checks the result and completes the task. It references the
   actual received evidence and reports any missing capability. For read-only
   code analysis, route all target-source access through the observed read-only
   commands; do not import or execute the target.
5. An independent reviewer compares the proxy record, inputs and delivered
   artifacts against the original frozen criteria. Keep earlier verdicts intact.
   This may turn a later attempt into a pass; it must not increase first-pass
   counts. Missing evidence still prevents a pass.

The proxy is a trusted-host observation mechanism, not cryptographic attestation
or an OS sandbox. A worker and reviewer still share a filesystem. Do not claim
that these records prove no unobserved action was technically possible. If a task
requires that stronger property, it needs separately validated isolation.
