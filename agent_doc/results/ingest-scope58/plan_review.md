# INGEST-SCOPE-58 independent plan review

## Review identity and immutable object

- Reviewer context: `/root/ingest58_review`, a separate host agent invocation from planner `/root`.
- Project: `/workspace/scratch/5d3e4236a5b4/agent-audit-58`.
- Decision: **approve** for the bounded local engineering plan described below.
- Reviewed plan: `agent_doc/results/ingest-scope58/plan_v1.md`.
- Verified SHA-256: `b9ed2eda610c8001d9b2542702ff24d295e613ebaafc5bd92b09b5d7846935f2`.
- Baseline HEAD verified: `cacbee7663282bcd17b8e08de6b4a00945a0a9fb`.
- Scope of this review: source inspection and plan evaluation only. No tests or measurements were run by this reviewer, and no implementation, task, guide, or external repository was changed.

This is an actual independent-context review document, not an authenticated `ReviewSession` receipt or proof of a deployed supervisor. The supplied host lacks the runtime authentication adapter and tmux service required for managed execution. That runtime branch remains blocked; this approval neither fabricates it nor authorizes bypassing a protected runtime gate. It evaluates the already-authorized, bounded local work. Publication remains conditional on actual implementation/result acceptance, current user authority, synchronization and remote readback.

## Full review

### 1. Intent — pass

The proposed change has a concrete producer/consumer basis, rather than an assumed performance benefit. `agent_runtime/knowledge_ingest.py` currently copies `store.root` into an isolated stage. `KnowledgeStore.__init__` reads records only from `root/entries`, and the subsequent ingestion path writes the candidate under that same subtree. Copying unrelated root siblings is therefore unnecessary for the combined-corpus validation that this temporary stage performs. Restricting only this copy boundary is smaller and more faithful to existing semantics than reconstructing the corpus from in-memory records.

The task stays within Chosen-David/agent, preserves the import API and candidate status, and excludes other repositories, SGLang, deployments, paid model calls and unrelated architecture changes. Recovering ingestion in the presence of unrelated root-local special files is a valid robustness objective even if measured timing gains are inconclusive.

### 2. Guide and document authority — pass

Read `AGENTS.md`, `prompts/decision_review.md`, `prompts/review_main.md`, and the dual-main, result-validation and project-document workflows. `agent_doc/guide/GUIDE.md` is genuinely empty (zero bytes). The existing guide README explains the human-only boundary and explicitly says it does not supply project requirements. No absent guide requirements or human approval are inferred. The whole guide directory remains read-only.

The canonical task index contains the active INGEST-SCOPE-58 entry and links to its detail. Root `TASK.md` is only migration navigation, not a competing editable checklist. The task detail currently has the same full-file hash as the frozen plan. Main-controller ownership of task/source/test/report writes and reviewer-only ownership of this review are explicit. Prior task states and historical evidence are not claimed as completed by this change.

### 3. Assumptions and interface compatibility — pass

Source inspection supports the essential assumption: the first staging copy can be limited to the full `entries` subtree while retaining relative paths and arbitrary nested layout. `KnowledgeStore` binds record paths relative to the corpus root, recursively discovers JSON/Markdown pairs, rejects symlinks inside entries and in the corpus-root ancestry, validates dependencies and derives the snapshot from record references. The stage must still contain `entries`, not move its contents up one directory.

The plan explicitly preserves all subtree files rather than filtering only JSON/Markdown. That is important because normal attachments/provenance should remain untouched, orphan Markdown must still be discovered, and unsupported subtree objects must not be silently skipped. In particular, non-record FIFO files are not rejected by `KnowledgeStore` itself, but existing `copytree` rejects their copying; keeping the entire entries copy preserves that refusal path. A FIFO used as metadata is rejected by the regular-file read check.

The three store validations, last snapshot comparison, candidate-only publication rules, provenance fields and final same-filesystem staging/rename must remain intact. The plan does not claim to fix pre-existing check/rename races or grant concurrent-writer safety; the existing single-maintainer contract remains applicable.

### 4. Prior results — pass

Inspected `prior-search.json`: query `knowledge ingest copy staging`, 237 scanned directories, `partial=true`, five candidates and explicit missing-record errors. Four candidate records report pending validation; the historical usable-with-scope communication result is unrelated to this copy boundary. None is valid evidence for the proposed import change. The plan transparently declines reuse for current acceptance instead of treating stored pass labels as proof.

The adjacent read-boundary56 report documents a distinct bounded-read defect and retained regression coverage. Its earlier code/data results cannot establish copy-scope correctness or new timing gains. Existing literature-reading records may remain background only; they are neither new reading nor local experimental evidence. A partial search cannot establish that no relevant historical result exists, but it does not block this targeted correctness investigation because no historical data are being relied on to waive required checks.

### 5. Acceptance — pass

The frozen acceptance criteria distinguish robustness, behavior equivalence and measurement. Required cases include root-local dangling symlinks/FIFO/regular files, retained refusal inside entries, invalid dependencies, repeated ID, ordinary nested attachments, no-attachment and root-attachment inputs, and a real SQLite-index fixture. Comparing records, snapshots, references and provenance excluding only timestamp is stronger than accepting exit status alone. Full tests, Reader tests and isolated plugin/mirror checks cover the second distributed implementation surface.

Logical-copy-byte accounting is expressly separated from uninstrumented full-ingest timing. The declared timing boundary includes validation, both copies, rename and cleanup, excluding input preparation. Seven alternating paired measurements after warmup, identical paired inputs and preservation of every sample are adequate for this bounded synthetic comparison, provided the implementation evidence really follows the plan. The zero-attachment case has no unsupported universal speedup threshold; absence of reliable timing benefit narrows the conclusion rather than being disguised as success.

The producer-to-independent-verifier-to-consumer order is preserved. The later verifier must inspect executed code and raw evidence across all six specified dimensions and independently reproduce a small representative subset. This plan approval is not result acceptance. Evidence must be frozen before downstream claims; implementation or protocol changes affecting the frozen scope require a new version/review, not retroactive relaxation after seeing measurements.

### 6. Risk — pass

The proposed implementation is narrowly reversible and has no external effects beyond the separately authorized eventual publication. It does not remove root-local attachments, rewrite corpus metadata, weaken entries validation or change the destination filesystem strategy. Special-file fixtures must stay in owned temporary directories, and the byte counter must not remain installed during timing. The final code review should confirm there is no added traversal of root siblings and that both source and plugin copy receive the same minimal change.

The plan's explicit publication gate is appropriate: fetch/integrate current upstream, reconsider changes overlapping the reviewed dependencies, independently accept results, then ordinary non-force publication and SHA/tree readback. A clean local test run is not a remote-publication result.

### 7. Resources — pass

The engineering plan needs local standard-library execution, bounded synthetic root-local attachments (16 MiB), seven paired repetitions and at most two active roles, with no overlapping timing jobs. Those resources are proportionate to the hypothesis. It introduces no GPU, new credential, paid service or indefinite retry demand. The absence of tmux/managed host authentication is openly scoped as a missing runtime capability, not presented as a started monitor. Costs or benefits of model execution and production hardware are outside acceptance.

## Nonblocking interpretation notes

1. **Root-local cache scope.** The documented default cache location is project `.knowledge-cache/`, outside the knowledge corpus root. The real SQLite case here is a user-configured index under the corpus root; do not report gains as applying to every default index configuration. Ordinary root documentation is also unnecessarily copied today, but the amount differs materially from a large synthetic attachment.
2. **Symlink wording.** `knowledge/FORMAT.md` contains a broad directory-symlink warning. The actual current enforcement is entries plus corpus-root ancestry, not arbitrary root siblings. The new behavior preserves that executable validation boundary; do not describe it as a general relaxation of entries symlink protection or a new race-proof filesystem sandbox.
3. **Logical work versus physical I/O.** Counting copyfile source bytes proves avoided logical copy payload for these fixtures, not physical disk traffic, cold-cache performance or production latency.
4. **Runtime capability boundary.** This document cannot satisfy a machine-authenticated `ReviewSession` API. Do not run or advertise the managed runtime as approved through this document; maintain the explicit blocker for that independent branch.

## Compact verdict

```json
{
  "decision": "approve",
  "summary": "Approve the frozen entries-only staging plan for bounded local implementation and independent verification; no implementation/results/publication acceptance is implied.",
  "plan_sha256": "b9ed2eda610c8001d9b2542702ff24d295e613ebaafc5bd92b09b5d7846935f2",
  "checks": {
    "intent": {"verdict": "pass", "reason": "Copy scope exceeds the actual entries-only consumer; the proposed change is narrow and authorized."},
    "guide": {"verdict": "pass", "reason": "Empty guide and human-only directory are respected; canonical task ownership and scope are clear."},
    "assumptions": {"verdict": "pass", "reason": "Actual source validates the full entries subtree; paths, dependencies, snapshots and final rename remain unchanged."},
    "prior_results": {"verdict": "pass", "reason": "Actual partial search is disclosed and unrelated or pending prior data are not reused as acceptance."},
    "acceptance": {"verdict": "pass", "reason": "Behavior equivalence, refusal boundaries, logical bytes, paired full-ingest timings and independent six-part verification are specified."},
    "risk": {"verdict": "pass", "reason": "Reversible local change with protected guide, retained subtree validation and explicit publication synchronization gates."},
    "resources": {"verdict": "pass", "reason": "Bounded local CPU/storage work; managed runtime unavailability is disclosed and remains outside this approval."}
  },
  "findings": []
}
```

## Evidence bindings

| File | SHA-256 |
| --- | --- |
| `agent_doc/task/TASK.md` | `61b9d5fe0e0ab1c43a69b83792f2b2a08fe83c488d1ece2530193f8cae4b51c4` |
| `agent_doc/task/task_details/INGEST-SCOPE-58.md` | `b9ed2eda610c8001d9b2542702ff24d295e613ebaafc5bd92b09b5d7846935f2` |
| `agent_doc/guide/GUIDE.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `agent_doc/guide/README.md` | `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261` |
| `agent_runtime/knowledge_ingest.py` | `2c2f2b85d0e2c2790bc1952df10ffda05555f8b8946e0adf3797605ac74a5333` |
| `agent_runtime/knowledge.py` | `9ee261d0e5ab8c803bc12a524308d783bdf18a259ce4c2ed06b0ca53f2c56770` |
| `agent_doc/results/ingest-scope58/prior-search.json` | `f52aa31d886b046f06ec1af7df41e30046dc009698c7de6600a7b10952b3d050` |

These hashes bind inspected bytes; they do not establish scientific applicability, human authorship or host authentication.
