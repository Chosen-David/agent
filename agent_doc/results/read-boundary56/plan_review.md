# READ-BOUNDARY-56 independent plan review

Date: 2026-10-19

Decision: **approve** for the frozen v1 bounded implementation and validation plan. This is the independent reviewer output for the explicitly documented local workflow. It is not a fabricated ReviewSession authentication receipt, managed Engine authorization, running supervisor, result acceptance, or publication approval.

## Reviewed identity

- Project: `/workspace/scratch/5d3e4236a5b4/agent-audit-56`.
- Reviewer context: `/root/read56_plan_review`; planner context: `/root`. Actual invocation authentication, if required by a host integration, remains host-owned.
- Baseline HEAD independently read: `ffd9abfeb2264a21e46322e4bedf310947229b2b`.
- Full plan: `agent_doc/task/task_details/READ-BOUNDARY-56.md`, SHA-256 `033d1269b04e031d078d9740f5d3134341aeece72fb25f98562866b82495cbbc`.
- Plan prefix before `## Progress`, SHA-256 `5bd53f1f009b6fb77b5ff58df80315fccbccf6035a74d422d9573b60a88d2eef`.
- TASK index, SHA-256 `e18eed5dc0f8d175697dcd5065e7486a727e28a0798b07ec104bda13b8eefb23`; new unchecked READ-BOUNDARY-56 entry and detail link independently located.
- Prior query: `agent_doc/results/read-boundary56/prior-search.json`, SHA-256 `b4394ce9395bce2b6316ff7d870c1ce5cd856cf2a89e80dfeacb1f588f8d0084`.

## Full review

The prior blocking absence of a concrete stable plan is resolved. The v1 document now gives the full local A→B→C→D→E→F→G dependency chain, two five-paper branches joined at F, baseline, implementation boundaries, deterministic failure reproduction, acceptance matrix, local resource scope and publication/readback steps. The proposed small repair matches the stated user authorization. It does not substitute a different optimization project or claim to complete other open requirements.

Actual source inspection confirms both KnowledgeStore._read and ingest's input reader currently perform stat-size checking followed by unbounded UTF-8 read_text. A shared binary read(limit+1), length check before decoding, then CRLF/CR normalization directly addresses the proposed defect. Retaining existing path and stat prechecks preserves ordinary fast rejection. The plan correctly avoids claims about hostile directory replacement, atomic snapshots, physical I/O read-ahead, overall memory caps, model quality or end-to-end speed.

The acceptance matrix is sufficiently specific: store metadata/body and ingest metadata/body, each growing by +1 and +4096 after stat and before open; legal JSON whitespace/body-newline growth; actual Python read request and returned-byte tracking; exact-limit ASCII and multibyte data; CRLF, CR and non-CR Unicode separators; invalid UTF-8 and oversized invalid UTF-8; original diagnostic distinctions. The distinction between early bounded rejection and eventual downstream rejection prevents a misleading all-rejected metric. Public parsing/body validation should continue to reject empty inputs where it did before; the helper's empty-input compatibility case is not permission to accept empty corpus metadata or body.

Canonical corpus bytes and directories must remain unchanged on rejected ingest, before staging begins. Successful ingest must preserve normalized body and provenance hash semantics. Complete corpus snapshot/content/hash comparison, existing knowledge/index tests, repository/reader regressions, generated checks, byte-exact plugin sync and copied-skill python -I ingest cover the principal compatibility risks. Actual code and raw failures/results remain for independent review at F; no tests or speed benefits have been claimed at this planning stage.

The historical query is incomplete (236 scanned, partial=true, missing records), which the plan reports. Its five returned summaries concern corpus integration or a mathematical projection result, not this read boundary; none supplies current equivalent code/data acceptance. New reproduction is therefore justified without claiming all history was exhausted. One minor descriptive correction is recorded below; it does not change this no-reuse decision.

Resources are credible for this local bounded task: Python/CPU, one test process at a time, at most three independent review contexts and an estimated 30-minute duration. An estimate is not a verified hard runtime guarantee. There is no GPU/service/billing requirement. The plan explicitly retains pending status if required reading or validation is incomplete and does not pretend tmux or a trusted managed backend exists. Lock ownership and any later git/network authorization remain planner/host responsibilities, not independently authenticated by this review.

The ten-paper reading requirement is represented by separate R1/R2 predecessors of F, five actual full texts each, with failed sources not counted. Their eventual records must identify sources and concrete methods/evidence/applicability; abstracts or failed fetches cannot satisfy those nodes. Paper evidence cannot replace local acceptance of this repair. Publication remains downstream of all required independent acceptance and latest-main reconciliation.

## Nonblocking findings

1. Target: Plan historical-query paragraph. It says all five candidates have stored validation pending. The actual fifth candidate, `math-convex-projection-20261009`, has `stored_validation=usable-with-scope`, while applicability remains unchecked; the first four are pending. Requested correction in the next report/reconciled plan: state four pending and one historical usable-with-scope, all inapplicable to this repair. Acceptance check: compare the sentence against the frozen query. This does not authorize reuse or affect the implementation/acceptance decision.
2. Target: Plan evidence-path notation. `results/read-boundary56/prior-search.json` is shorthand; the actual project-relative path is `agent_doc/results/read-boundary56/prior-search.json`, fixed above. Use the latter in downstream evidence links. No source or acceptance change is needed.

There are no unresolved blocking findings. Material changes to scope, acceptance, budget, dependencies or baseline after concurrent integration require a reconciled plan and appropriate re-review; routine Progress additions retain their ordinary meaning.

## Compact verdict

```json
{
  "decision": "approve",
  "summary": "Approve the frozen v1 local bounded-read repair plan; independent executed-code/data acceptance and publication gates remain pending.",
  "checks": {
    "intent": {"status": "pass", "reason": "Authorized Agent-only local correctness repair; ten-paper baseline retained as separate required branches."},
    "guide": {"status": "pass", "reason": "GUIDE.md is empty; complete guide README read and read-only ownership preserved."},
    "assumptions": {"status": "pass", "reason": "Actual stat/read_text sites inspected; byte count, decoding order and newline compatibility are explicit; hostile replacement and physical I/O guarantees excluded."},
    "prior_results": {"status": "pass", "reason": "Actual partial prior-query evidence read; no returned candidate applies to this defect; minor fifth-candidate status correction does not affect no-reuse decision."},
    "acceptance": {"status": "pass", "reason": "Four entrances times two growth amounts, Python read bounds, encoding/newlines, unchanged corpus, isolated plugin ingest and full regression join at independent F."},
    "risk": {"status": "pass", "reason": "Localized reversible change with specific compatibility tests, accurate claim boundaries and independent validation before publication."},
    "resources": {"status": "pass", "reason": "Local CPU/Python, serialized tests and three bounded review contexts are feasible; runtime estimate and unavailable supervisor are honestly qualified."}
  },
  "findings": [
    {"blocking": false, "target": "Plan historical-query paragraph", "feedback": "Four candidates are pending; the fifth has historical usable-with-scope, not pending.", "requested_change": "Correct the descriptive count in subsequent reporting/reconciliation while retaining all five as inapplicable.", "acceptance_check": "Compare against prior-search.json stored_validation fields."},
    {"blocking": false, "target": "Plan prior-search path", "feedback": "Use the complete agent_doc/results project-relative path.", "requested_change": "Use agent_doc/results/read-boundary56/prior-search.json in evidence links.", "acceptance_check": "Resolve the link from the project root."}
  ]
}
```

## Actual reading and actions

Read AGENTS.md, prompts/decision_review.md, prompts/review_main.md, workflows/project_document_workflow.md, workflows/dual_main_workflow.md, workflows/knowledge_access_workflow.md and workflows/result_reuse_workflow.md. Inspected guide directory, empty GUIDE.md and complete README.md; the TASK tail followed by the precise new entry and diff; complete READ-BOUNDARY-56 v1 and prior-search.json.

Read knowledge.py lines 1–170 and complete knowledge_ingest.py; inspected returned sections of tests/test_knowledge.py lines 1–195 and tests/test_knowledge_index.py lines 1–255. One initial combined output was truncated, so unseen material is not claimed as read. Inspected sync_plugin_references.py lines 150–180 and relevant call-site searches. Queried task/results text for prior read-boundary evidence. Ran the read-only knowledge query `file read byte budget TOCTOU race bounded UTF8`; three lexical probability/RL matches were inapplicable and not adopted. Read git HEAD/status/diff and computed document hashes. No producer tests, source edits, guide writes, index edits, git publication, or supervisor startup were performed. The only reviewer-written artifact is this file.
