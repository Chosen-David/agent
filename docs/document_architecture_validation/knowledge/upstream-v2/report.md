# Actual 907 corpus integration verification

Scope: independent, targeted knowledge/corpus integration checks for AIK-03 and DOC-04. Raw measurements and the native pending result contract are in [the centralized result run](../../../../doc/results/combined-corpus-delta-v2-20261007/final-summary.json). Final release acceptance remains owned by the independent release reviewer.

## Exact baseline and preservation

Actual remote baseline is `907890831929a5d200d3fb64c6299449391a1ee8`: 75 published entries plus one candidate. Combined corpus has 77 published entries plus the same candidate. All 152 baseline entry files are byte-identical; the two AIK cards match their accepted four-file hashes. The only existing corpus files changed are README, coverage and learning state: coverage adds exactly the two AIK IDs, and learning state adds one AIK history record. Removing those additions produces the exact upstream JSON, including cursors, priorities, gaps and earlier history.

- Baseline snapshot: `f70265eb89bcab4f76af08333e01f15007ab16203dbeb29647f183d126211b6e`
- Combined snapshot: `35d6a2001b51a55b5b73dee77a817e51ac04391114ca57f7abf9b93d1b41a85b`

The holdout registry is unchanged from the accepted staged AIK addition. Source metadata was checked before loading corpus bodies; no reserved DOI/URL collisions were found, and no reserved target material was read. Metadata matching cannot rule out every possible semantic leak.

The cephalopod entry remains candidate. Both corpora reject normal get, omit it from default file/SQLite searches and contain only published IDs in the index. This is an interface check, not new scientific acceptance. No papers, supplementary data or author code were reviewed in this delta.

## Authored retrieval catalogs: no added-card regression

The seven unchanged catalogs contain 58 queries, evaluated with both actual907 and combined runtimes/corpora: 116 query/backend comparisons. Per-query Recall@3, context recall, MRR and no-hit correctness show zero regressions. Separate inherited context8 checks cover 21 queries and 42 backend comparisons, also with zero regressions. All exit statuses and failed cases are preserved.

Current inherited default results:

| Catalog | Files Recall@3 / context | SQLite Recall@3 / context |
| --- | --- | --- |
| Original | 17/21 / 6/7 | 17/21 / 6/7 |
| Round2 | 0.75 / 0.75 | 0.75 / 0.875 |
| Morphology | 0 / 0 | 0.5 / 0.75 |
| Engineering, RL/probability, neuroscience, bee | 1 / 1 | 1 / 1 |

With context8, original context recall is 1 for both backends, round2 remains files 0.875 / SQLite 0.75, and morphology is files 0 / SQLite 1. These are distinct configurations, not a claim that larger context universally fixes retrieval. Raw Top3 scores are unchanged.

All 40 backend output summaries, covering 316 raw query/backend rows across baseline/candidate and configurations, were recomputed from expected, actual and context IDs. Mean equality was not substituted for per-query comparison. See [catalog comparison](../../../../doc/results/combined-corpus-delta-v2-20261007/catalog-comparison.json) and [metric/metadata audit](../../../../doc/results/combined-corpus-delta-v2-20261007/metric-and-metadata-audit.json).

## Frozen AIK development cases and informed recovery

The 12 unchanged authored cases retain their frozen query/gold hash. Default context finds 21/24 targets; domain-scoped context finds 23/24. Raw Top3 is 16/24 default and 22/24 domain. Baseline has neither new AIK target and therefore records 0/24 target hits; that is not a pre-existing baseline quality requirement.

Default gaps remain files A12, SQLite A03 and A12. Domain filtering leaves SQLite A12. The existing, explicitly informed relevance-selection recovery script restores all three known default gaps with full text, valid strong-dependency refs and at most 14,118 of the unchanged 20,000-character budget. This is manual/agent relevance selection on known development cases, not automatic recovery, blind evaluation or a ranking repair.

## Fresh tests exposed and fixed an inherited fixture error

The initial 67-test knowledge run had four failures: the index correctly contained 77 published records while the fixture expected all 78 records. Actual907 independently reproduces the same four failures with 75 indexed versus 76 total. Both failed logs remain unchanged.

The sole source writer corrected the fixture to distinguish total and published counts and strengthened exact indexed-ID equality plus candidate exclusion. No runtime retrieval code changed. The final stable-hash rerun passes all 67 knowledge tests, including schema, mirrors, indexing, handoffs and maintenance. Another 34 handoff-basis/selective-context tests pass. A first consumer invocation failed due to its module import path; that log is retained, followed by successful repository-compatible invocation with tests on PYTHONPATH.

An isolated copy of the plugin runs under Python `-I -B`, with cwd `/` and PYTHONPATH unset. It validates 78 records, indexes 77 published entries, retrieves the AIK sampling card and rejects normal access to the candidate. The copied corpus exactly matches source. This does not claim that any pre-existing host installation updated.

See [supplement and exact dependency hashes](../../../../doc/results/combined-corpus-delta-v2-20261007/supplement.json). No full730 rerun was duplicated; the parent owns full-suite evidence and scope reconciliation.

## Acceptance boundary and result registration

Observed outcome: scoped integration non-regression, preserved candidate/holdouts, 101 fresh focused tests passed after fixture correction, and isolated package smoke passed. Original retrieval failures, first test failures, old reports and preliminary summary remain historical evidence.

The [native result contract](../../../../doc/results/combined-corpus-delta-v2-20261007/contract.json) binds the [manifest](../../../../doc/results/combined-corpus-delta-v2-20261007/manifest.json), code, inputs, raw outputs, configuration and environment. It is registered as native and pending; registration itself supplies no independent acceptance. The [final summary](final-summary.json) supersedes the initial test status without rewriting the initial record. A receipt-generation error after successful registration was resolved by reading the saved record, without altering manifest or result bytes.

No live-model quality, semantic retrieval, general scientific applicability, GPU/latency/token benefit, new paper review, formal proof or automatic deployment claim is supported here. Timings are recorded only as raw execution provenance. Final independent review must evaluate these limits and the actual result artifacts before release consumption.
