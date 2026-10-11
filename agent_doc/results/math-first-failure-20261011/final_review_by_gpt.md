**Decision: approve, limited to the ordinary finite analytic document candidate.** No blocking mathematical or documentary finding. This is the second and final ordinary review in the two-review budget. It is not a trusted `ReviewSession` receipt, scientific result validation, production certification, or authorization to dispatch a protected DAG.

Reviewed read-only under `/workspace/scratch/e902062ab206/agent`: `AGENTS.md`, decision-review and project-document workflows, MATH-81 task detail and advice, and the saved sources, navigation, knowledge-use, prior-disposition, plan-review, report, registration, cost and preservation records. I also inspected the current tracked diff, the empty GUIDE, the loaded knowledge record, four registered artifact hashes, and the cited original source passages. I made no edits, ran no tests or scientific experiments, and used no subagents.

| Review dimension | Verdict | Basis |
| --- | --- | --- |
| intent | pass | The candidate addresses finite-chain first-failure risk and distinguishes conditional hazard, actual deployment marginals and population calibration. It claims no model or deployment benefit. |
| guide | pass within document scope | `agent_doc/guide/GUIDE.md` is empty. No additional guide requirement can be inferred from it. The current tracked diff contains no guide modification, and advice remains proposal material rather than authorization. |
| assumptions | pass | Finite probability space and horizon, adapted failure events, measurable survival history, predictable caps in `[0,1]`, and survivor-history conditional bounds are explicit and sufficient. |
| prior_results | pass with disclosed limits | Saved disposition reports 131 scanned records, 45 errors and partial search. Unrelated Fano/convex results are declined; old measurements and validation are not reused. This supports documented screening, not exhaustive absence of prior work. |
| acceptance | pass for analytic candidate | Two finite proofs, six public handworked examples, refusal conditions, source limits and navigation are present. Public examples are accurately distinguished from unseen/model tests, numerical experiments and formal proof. |
| risk | pass | No population expected-risk guarantee is upgraded to per-history hazard. Averaged random caps are not inserted into a product. Intervention failures, distribution changes, unknown certificates and incomplete task outcomes remain explicit limitations. |
| resources | pass for this bounded review | Cost metadata declares 1200 seconds and two ordinary reviews, with no scientific CPU/model/GPU runs or formal proof. This review stayed read-only and within the assigned ordinary document-review scope; it does not independently audit all prior runtime consumption. |

The mathematical definitions and proofs are correct within their stated scope. With \(E_t\in\mathcal F_t\), \(S_{t-1}\in\mathcal F_{t-1}\) and \(h_t=P(E_t\mid\mathcal F_{t-1})\), the conditional bound is required only on surviving histories. For deterministic caps,

\[
P(S_t)=E[1_{S_{t-1}}(1-h_t)]
\ge (1-a_t)P(S_{t-1}),
\]

so iteration gives \(P(\bigcup_tE_t)\le1-\prod_t(1-a_t)\). The subsequent union-style bound by \(\min(1,\sum_ta_t)\) is valid. Independence is unnecessary.

For random predictable caps, the first-failure events \(D_t=S_{t-1}\cap E_t\) are disjoint and their union equals the failure union. Consequently,

\[
P\!\left(\bigcup_tE_t\right)
=\sum_tE[1_{S_{t-1}}h_t]
\le E\!\left[\sum_t1_{S_{t-1}}a_t\right]
\le E\!\left[\sum_ta_t\right]
\le B.
\]

Nonnegativity and the pathwise budget justify the last inequalities. The document correctly also observes that an expected total cap bound suffices for the overall probability bound but does not establish pathwise budget feasibility. No optional-stopping theorem or infinite-horizon assertion is needed.

The treatment of \(T=0\), caps equal to one, \(B\ge1\), null histories and initial failure is adequate. The genuine deployment-marginal union bound is correctly retained and separated from the stronger conditional product bound.

| Public example | Independent handwork and verdict |
| --- | --- |
| 1. Two `.01` survivor-history caps | \(1-.99^2=.0199\). Independent Bernoulli failures attain equality, while the proof itself does not require independence. **Pass.** |
| 2. Mutually exclusive `.1` marginal events | The failure union is `.2`; the marginal product expression `.19` underestimates it. The surviving second-step hazard is `.1/.9=1/9`, exceeding `.1`. **Pass.** |
| 3. Rare bad context | A `.01` bad-context population with failure exactly on bad contexts has population failure `.01` and bad-context conditional failure `1`. Restricting deployment to bad contexts gives failure `1`. This invalidates the conditional/transfer upgrade while leaving the original marginal statement intact. **Pass.** |
| 4. Random cap means | On a fair, execution-before-known branch, caps are `(.5,0)` or `(0,.5)` and failure occurs with probability `.5` at the funded step. Each path spends `.5`; total failure is `.5`, whereas \(1-.75^2=.4375\). A finite branch-and-coin space supplies the construction. **Pass.** |
| 5. Early stopping | A first `.02` allowance and at most `.03` further pathwise spending imply total failure at most `.05`. Decisions precede the next exposure; stopped steps have empty failure events and zero caps. Already incurred failure remains counted, and potentially failing interventions must be included. **Pass.** |
| 6. Device operations | \(.99\times.98\times.97=.941094\), so the conditional-cap failure bound is `.058906`. The document makes this a hypothetical probability-model mapping and refuses certification of an actual device. **Pass.** |

Source attribution stays within appropriate limits. Powell’s notes provide conditional-probability and conditional-expectation background; the first-failure composition is explicitly presented as the project’s derivation rather than a newly sourced theorem. The cited notes contain the identified probability-revision and conditional-expectation sections. genui{"citation":{"ref":"turn539view1"}}

CORA’s inspected Appendix F.2 defines a harm-times-execution loss and its population expectation; F.5 describes episode/block splitting to reduce temporal leakage. Those passages support the candidate’s distinction between the paper’s risk object and a per-history hazard certificate. The candidate does not inherit the paper’s calibration proof, deployment safety or experimental benefits, and leaves formal publication unverified. genui{"citation":{"refs":["turn540view0","turn540view1"]}} The stored conformal-policy knowledge record is used for the same refusal boundary, with its original proof limitations preserved; this review does not revalidate that other paper’s theorems.

Registration and preservation are appropriately scoped:

- The advice, navigation, sources and knowledge-use hashes match all four values in `record.json`.
- `contract=null`, validation `unknown` and proof `null` remain intact. Registration establishes references, not scientific usability.
- Navigation explicitly declines canonical promotion and defers runtime adoption.
- The tracked diff appends the task entry, a coverage note and a learning-history entry; it does not rewrite earlier substantive entries or change tracked historical result artifacts.
- `preservation_check.json` labels its claim “integrity only.” I inspected that assertion and the current tracked diff, but did not independently recount or hash all 8,363 archived files. The archive-wide count must not be attributed to this review.

**Blocking findings:** none for retaining and publishing this document as an ordinary analytic candidate. Real deployment certificates, intervention models, budget ledgers, trusted scientific validation and fair model-benefit comparisons remain prerequisites for any later adoption; this approval does not discharge them.

**Nonblocking findings and closeout actions:**

1. `TASK.md` already marks MATH-81 complete, while the task progress and report still say final review is pending. The main author should reconcile these closeout statements after saving this actual review. The checkbox alone did not establish completion.
2. The registration deliberately excludes the mutable report and final review. Preserve that distinction: appending a final report or review does not retrospectively extend the four registered hashes or confer scientific validation.
3. The example-4 phrase “另一部无失败” is a harmless typo; “另一步无失败” is clearer. Example 2’s wording can also be simplified to “两个互斥事件，各自概率为 `.1`.” Neither affects correctness.
4. Keep the disclosed partial prior search, manual refined knowledge retrieval, unknown validation and absence of unseen/model tests visible in final reporting. These are material boundaries of the evidence.

Approve the reviewed candidate within this scope, preserve the full ordinary review, and leave production/canonical adoption deferred.
