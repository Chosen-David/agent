# Resume without losing review state

This is an archive, not an installed/published knowledge entry. The live corpus and its metadata were restored to integrated main59ad8d962ce934085f76171f651370ef5dcd9944. The old neuro candidate has no restored ledger and must not be resubmitted under a new lineage.

Read report.md, publication-blocker.json, resume.json, independent_review.md and independent_results.json before any action. The latter retains prior runs, exact verifier sources, recorded failures and source hashes; independent_cases.json was frozen before the first independent run. Candidate_history and its manifest supply every candidate JSON/MD revision that matches those hashes. The production test is verify.py; the independent verifier does not import it.

Preserve the original start baseline38d3764b23412aab6c29152b4b92e6cc27c25692 and the concurrent integrated baseline separately. integrated-baseline-* excludes this card; final-* is the rejected integrated published trial. The raw gate failure is english-alias/sqlite, not a context failure. All three old retrieval suites still have inherited exit1. An incremental comparison alone is insufficient to lift the original publication gate.

Reproduction should use an isolated checkout at the recorded source version. To reproduce a historical trial, copy the corresponding candidate_history pair into knowledge/entries only in that isolated checkout, retaining that revision's actual status. The independent verifier expects those source paths to exist for hashing; --corpus-root chooses the retrieval corpus, not the source checkout. Do not run a historical published-trial setup against the live corpus. Review code before running local scripts; no upstream code is needed.

For scientific promotion, first resolve the recorded regression or explicitly version the plan and obtain the required independent acceptance. Then refresh remote/holdout metadata, re-register candidate and metadata, rebuild derived indexes and rerun affected tests/queries/ref checks. Frozen queries exposed during this round are now regression cases, not newly unseen tasks. No current archive receipt is a runtime ReviewSession proof or permission to reset another lineage.

Archive-only persistence is independently reviewed and authorized; no canonical knowledge publication is authorized by that outcome. Identify the archive commit through Git history and the handoff's remote readback, without embedding a self-referential commit hash.
