# READ-BOUNDARY-56 independent result review

Date: 2026-10-19. Reviewer context: `/root/read56_plan_review`.

**Decision: usable-with-scope. No blocking implementation or evidence finding remains for the reviewed local bounded-read change.** This accepts the precise code/data scope below, not model performance, a security sandbox, universal race freedom, publication readback or an authenticated managed-runtime receipt.

## Frozen inputs and source review

The baseline is Git commit `ffd9abfeb2264a21e46322e4bedf310947229b2b`. I read the actual canonical diff, complete new regression test, complete measurement script, original before/after logs and environment binding. The plan_v1.md copy has SHA-256 `033d1269b04e031d078d9740f5d3134341aeece72fb25f98562866b82495cbbc`, matching the approved plan. All seven environment.json code/test/measurement hashes matched actual bytes at review; the independent binding is in reviewer-integrity.json.

Reviewed implementation hashes:

| File | SHA-256 |
| --- | --- |
| agent_runtime/knowledge.py and corresponding plugin mirror | `9ee261d0e5ab8c803bc12a524308d783bdf18a259ce4c2ed06b0ca53f2c56770` |
| agent_runtime/knowledge_ingest.py and corresponding plugin mirror | `2c2f2b85d0e2c2790bc1952df10ffda05555f8b8946e0adf3797605ac74a5333` |
| tests/test_knowledge_read_boundary.py | `3d814d3cdcfe6859b9d0fd296d10f40d566ebd1eeb882e440f5ab9ff0314009d` |

The shared helper makes one binary `read(max_bytes+1)`, checks returned byte length before strict UTF-8 decoding, and reproduces universal CRLF/CR newline translation. Both store and ingest preserve their existing path/regular-file/stat checks and distinct byte-budget errors. Both package and standalone import branches reference the helper. Inputs are read before any ingest staging, so failure at the new boundary has no canonical import side effect. No unrelated API or schema changes were found in the implementation diff.

## Independent executed checks

1. Re-ran the producer's targeted suite: `python -m unittest discover -s tests -p test_knowledge_read_boundary.py -v`. Five tests passed, including actual copied-plugin `python -I` ingest, mirror byte identity, all four entry paths, original corpus equality and provenance/newline checks. Raw output: reviewer-targeted.log.
2. Wrote and executed a separate harness, reviewer_probe.py. It loads the actual two baseline source modules from Git, independently constructs a minimal valid corpus and import pair, injects growth only at the target open, and records actual read request/return type. It does not import the producer's test helper. Eight baseline cases all accepted; the same four entry types × two growth amounts all rejected in the patched version. All patched read calls requested and returned exactly 1,048,577 bytes; all baseline calls were unbounded read(-1) returning text. These are 16 execution cases, not 16 distinct fault types. Raw detailed evidence: reviewer-probe.json and reviewer-probe.log.
3. Added six independent public-ingest cases across metadata/body: exact 1 MiB UTF-8 content accepted, short malformed UTF-8 raised UnicodeDecodeError, and oversized malformed UTF-8 raised the import byte-budget error before decode. Rejected imports left corpus files and directories unchanged.
4. Compared 343 triples drawn from CR, LF, CRLF, NEL, Unicode line/paragraph separators and a four-byte emoji against an independent `TextIOWrapper(BytesIO(...), newline=None)` reference. All decoded strings matched; Unicode separators were preserved.
5. Loaded the real 115-record knowledge corpus through baseline and patched KnowledgeStore classes. Entire records and snapshot matched exactly: `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`.
6. Independently ran `python scripts/sync_plugin_references.py --check` and `git -c core.whitespace=cr-at-eol diff --check`; both returned zero. Evidence: reviewer-checks.log. Existing CRLF source line endings were preserved.

The independent harness returned pass for 16 old/new growth executions, 6 additional import cases and 343 newline comparisons. These counts describe deterministic checks, not a statistical estimate of general filesystem race probability.

## Producer data and measurement validity

The original before.log shows eight growth subcases failing specifically because KnowledgeError was not raised, plus one invalid-UTF-8 error-order failure. This is genuine baseline failure evidence, not merely an import/setup error. after.log reports all five tests passing. I independently reproduced the core old/new outcome instead of relying only on these labels.

measure.py loads baseline source from the exact Git commit and uses the same input bytes for each before/after pair. I checked all eight paired input/grown hashes and actual post-growth file sizes. measurements.json reports eight accepted baseline cases and zero accepted patched cases. The baseline return count is explicitly text characters after universal-newline processing, whereas the patched count is bytes. These are deliberately not presented as comparable physical-I/O byte measurements. The corrected claim is bounded application read request/returned byte buffer and earlier rejection, not lower total memory, faster tasks or improved LLM answers.

The completed producer full-tests.log was inspected and hashed before the planner's announced private checkpoint archival: SHA-256 `643afbc0e6eed00700718d42399d88c6cfd26f587ebc144214ce6b1e53b06679`. Parsing its actual named outcomes yielded 1,282 ok and 8 skipped, agreeing with the footer `Ran 1290 tests in 96.103s`, `OK (skipped=8)`. reader-tests.log reports three tests passing. I did not independently rerun the entire repository or Reader suite; this review independently reran targeted tests and examined the completed producer evidence. The full log hash and original footer are preserved in reviewer-integrity.json. Any private archival path is planner-owned; this report does not claim that an omitted large log is committed or remotely available.

## Research evidence boundary

I read both complete research_a.md and research_b.md. They document ten distinct successful original-text readings, methods, experiment/ablation evidence or explicit absence, limitations, and adopt/adapt/defer decisions. The failed `2608.14680` source is explicitly excluded. They do not claim model replication or pixel-level PDF inspection. Their relevance is methodological context; none is used to prove the file helper correct or to count paper benchmark numbers as local gains.

I independently reopened all ten original arXiv HTML URLs and checked one concrete evidence point per paper against the actual source:

| Source | Independently checked point |
| --- | --- |
| [AgentChaos v1](https://arxiv.org/html/2608.06790v1) | Table 4 AutoGen tool-call ratio 6.55×; this is fault response overhead, not file-boundary validation. |
| [ACON page](https://arxiv.org/html/2510.00615) | Table 4 reports 73.24s without compression and 87.68s with history compression, consistent with the report's rejection of universal speedup. |
| [AgentFold v1](https://arxiv.org/html/2510.24699v1) | Table 1 BrowseComp 36.2 and Figure 3 context-growth description. |
| [AgentFly v1](https://arxiv.org/html/2508.16153v1) | Table 3 average sequence and Table 5 DeepResearcher 59.9/72.2 versus 66.6/80.4. |
| [Reflexion v4](https://arxiv.org/html/2303.11366v4) | Table 3 ablation sequence .60/.52/.60/.68 on the 50-hardest HumanEval Rust subset. |
| [MemGPT v2](https://arxiv.org/html/2310.08560v2) | Table 2 GPT-4 DMR 32.1% versus 92.5%. |
| [Mem0 v1](https://arxiv.org/html/2504.19413v1) | Table 2 full-context and memory method judge-score/latency tradeoff. |
| [MemoryBank v3](https://arxiv.org/html/2305.10250v3) | Table 2 English ChatGPT retrieval .763 versus correctness .716. |
| [A-Mem v1](https://arxiv.org/html/2502.12110v1) | Table 2 provides no-LG-and-ME, no-ME and full-system rows, not a full factorial design. |
| [MEM1 v1](https://arxiv.org/html/2506.15841v1) | Table 3 Wiki-RAG MEM1 .405 EM / 3.79s versus Search-R1 .445 / 2.23s. |

This is independent source spot verification of the two reading records, not a claim that the verifier repeated every full-paper reading or all numerical calculations. No source mismatch was found in these ten checks. The ACON exact-number search initially returned no match; locating its Table 4 displayed and resolved the numbers, so that search miss is not an unresolved factual issue.

## Required verdict dimensions

| Dimension | Verdict | Evidence and limit |
| --- | --- | --- |
| implementation | pass | Actual source diff inspected; bounded binary read and decode order correct; path prechecks and diagnostics retained; two mirrors exact. |
| reference_boundary | pass | Exact Git baseline, frozen plan, whole-corpus comparison, byte versus character units and filesystem/model non-goals explicit. |
| data_integrity | pass | Seven environment bindings verified; paired source/grown hashes consistent; original failure logs retained; reviewer hashes bind raw evidence. |
| numerical_sanity | pass | Budget 1,048,576; overflow probe 1,048,577; eight paired growth cases; 1,282+8=1,290; no unsupported percentage or timing claim. |
| measurement_validity | pass | Deterministic open-time mutation actually fires; accepted/rejected and read buffer are directly observed; no thread timing dependence or physical-I/O extrapolation. |
| reproducibility | pass | Exact baseline retrievable; producer test/measurement scripts and independent reviewer script execute; standalone plugin path exercised. Full-suite rerun remains producer evidence. |

## Remaining limits and next owner

No blocking finding remains for the reviewed repair. The accepted scope is regular-file application reads that grow after the existing stat precheck and before/during bounded reading, plus the tested compatibility behavior. It does not establish an atomic snapshot, eliminate symlink/directory replacement attacks, constrain buffered physical read-ahead, bound whole-corpus memory, or guarantee behavior on every special filesystem. No model/GPU/end-to-end performance experiment was run.

Planner owns any final task/index/report updates, reconciliation with newer main, publication and remote byte/tree readback. If the reviewed implementation or tests change, revalidate the affected claims rather than reusing these hashes as if they described new bytes. This reviewer wrote only result_review.md and reviewer-prefixed evidence files in the assigned result directory; no source, guide, index or publication changes were made.
