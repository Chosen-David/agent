# MATH-80 ordinary independent final document/indexing review

**Decision: approve for the bounded historical discovery bridge. Blocking findings: none.**

This review covers document accuracy, historical registration, actual retrieval outputs, reference integrity, preservation, and the mathematical refusal boundary. It is an ordinary independent review, not an authenticated `ReviewSession`, `verify_experiment_result` acceptance, scientific validation, or publication authorization. I performed no writes, scientific experiments, model calls, or runtime changes.

## Checks

| Check | Verdict | Finding |
|---|---|---|
| intent | pass | The work repairs discovery of existing MATH-78/79 documents through the existing historical registry. It does not introduce a theorem, canonical entry, Skill, or production strategy. |
| guide | pass | `GUIDE.md` remains empty; the guide directory is unchanged against the stated base. No substantive guide requirements were invented. |
| assumptions | pass | The report correctly describes lexical metadata search, caller-controlled document loading, and explicit reference hashing. It does not equate retrieval with applicability. |
| prior_results | pass | Before-search outputs retain actual unsuccessful discovery, missing-record errors, and unrelated returned candidates. Existing mathematical material is consulted as scoped documentation; old scientific measurements are not reused. |
| acceptance | pass | Identical public queries produce the reported new first-ranked targets. All 15 historical artifact references match current bytes. The three registrations retain unknown validation. |
| risk | pass | Old tracked regular files are preserved except the three intended metadata files, whose diffs are additive. MATH65, canonical knowledge entries, runtime, guide, Skills, and SGLang are unchanged. |
| resources | pass for scope | Only read-only review and metadata checks were required here. No measured model/token/cost or scientific performance conclusion is claimed. Trusted managed-review and experiment capabilities remain outside this approval. |

## Independently verified retrieval and registration

I read the actual `ResultStore.register_history`, `_save`, `show`, and `search` implementations.

- `register_history` checks artifact hashes before registration and emits historical origin, `contract: null`, unknown validation, and no proof.
- `_save` refuses an existing record and publishes without overwriting another registration.
- `search` indexes only `summary`, `run_id`, `result_id`, `producer_task_id`, and `context`.
- `show` returns the record and its hash; it does not automatically rehash its historical artifacts.

The report accurately explains these boundaries.

I independently reran all three searches with `limit=3` and `max_scan=200`. Each complete current search response exactly equals its saved `after_*.json` response.

| Identical before/after query | Target absent from saved before top three | Verified after first result |
|---|---|---|
| `compressed state transition history` | yes | `math-state-aggregation-20261010` |
| `whole task probability any failure` | yes | `math-marginal-contraction-20261010` |
| `device alarm sequence distribution` | yes | `math-marginal-contraction-20261010` |

Each saved before and after response scans 127 directories. Error counts decrease from 45 to 42. The removed errors are exactly the three newly registered rounds; no new errors appear. The report properly leaves the remaining 42 errors unresolved.

`partial: true` is correctly qualified: the implementation sets it for bounded directory enumeration or omitted hits beyond the result limit. It is not evidence of exhaustive coverage or a guarantee that enumeration reached its bound.

The summaries contain the same task language used by these public queries. This is a valid deterministic discovery check, with the report’s explicit restriction against presenting it as unseen or model-selected retrieval.

## Reference integrity and historical preservation

Independent hashing confirms every historical reference:

| Record | Verified artifact references | Validation | Contract / measured time |
|---|---:|---|---|
| MATH-78 history | 5 | unknown; proof null | null / null |
| MATH-79 history | 6 | unknown; proof null | null / null |
| MATH-80 history | 4 | unknown; proof null | null / null |

All three records retain `origin: historical-external-reference` and empty experimental context. No code version, execution environment, metrics, or scientific measurement time was fabricated.

I independently compared every tracked regular file at base `00a0d917eb35271b8973094fa9207228364d3ce3` with current bytes using Git object hashes. The base contains 8,232 regular files. Exactly three differ:

- `agent_doc/task/TASK.md`
- `knowledge/coverage.json`
- `knowledge/learning_state.json`

The other **8,229 original regular files are unchanged**, corroborating `preservation_check.json`. The three intended diffs add the MATH-80 index entry, coverage limitation, and learning-history item. The prior learning history is an exact prefix; other top-level learning-state values are unchanged.

Original MATH-78/79 advice, reports, navigation, review records, failures, and other evidence retain their bytes. MATH-78’s limited JSON review history is described honestly; its missing full feedback is not reconstructed. MATH-79’s complete Markdown review references are preserved.

## Mathematical content and refusal boundary

The report’s conditional mathematical statements are consistent with the existing advice and the loaded `math.sequence-tv-coupling@1` content.

1. **State aggregation:** Equal transition mass into every target block for every pair of microstates within a source block supports one common macro transition kernel for any initial law. Stationary averages and one fixed action do not establish the general condition. Authorization, evidence version, and other decision fields still require their own preservation checks.

2. **Whole-path events:** With a common initial condition, finite common alphabet and horizon, matching stopping conventions, and complete relevant shared-prefix conditional-kernel bounds,
   \[
   |P(A)-Q(A)|\leq \operatorname{TV}(P_{\mathrm{path}},Q_{\mathrm{path}})
   \leq 1-\prod_t(1-\epsilon_t).
   \]
   The report presents this as conditional analysis, with actual task kernels and certified error envelopes unknown.

3. **Alarm-sequence transfer:** The report maps the conditional probability structure without claiming a verified physical fault mechanism or real device sampling model.

4. **Marginal refusal:** For rows \(P=(.99,.01)\), \(Q=(1,0)\), and common initial state zero, each positive-time marginal TV is `.01`, while the probability difference for any failure over \(T\) transitions is \(1-.99^T\). At \(T=2\), this equals `.0199`, exceeding `.01`. Thus a marginal \(\epsilon/(1-\rho)\) bound cannot replace the path-event bound. The report correctly retains this refusal and does not label the hand calculation as a new scientific experiment.

No statement certifies real model behavior, successful automatic refusal, actual task success probability, or production safety.

## Source and evidence limitations

The report appropriately limits the classical Powell source to finite discrete TV, maximal coupling, and the coupling inequality; the sequence transfer is identified as existing project derivation.

The recent-source section distinguishes the observed arXiv version/related DOI from failed fresh HTML access and unverified final article content. The failed additional preprint access supports no new version or publication conclusion. This review does not independently authenticate those live webpage observations; they remain bounded by the saved source record and the parent’s retrieval evidence.

The initial knowledge query’s miss and manually refined query are disclosed. Neither knowledge loading nor historical registration is represented as canonical promotion or automatic application.

Search timings are explicitly local metadata timings. There are no unsupported model, unseen-test, token-saving, GPU, Lean, deployment, or end-to-end performance claims.

## Nonblocking closeout observations

The task detail still says final ordinary review is pending. After receiving this review, the designated main writer should append its outcome and evidence location before final reporting. The current task-index completion label can then be supported by the completed ordinary review.

The MATH-80 immutable history record binds navigation, knowledge use, prior search, and plan review; it does not bind the final report or this later final review. That is consistent with its narrow historical-reference scope. Consumers must not describe that record as an immutable binding of the complete final package.

**Approved scope:** discovery of the existing documents through three public lexical queries, integrity of registered references, preservation of original evidence, and accurate conditional mathematical/refusal documentation. Scientific adoption, authenticated managed dispatch, model evaluation, and production decisions remain deferred.
