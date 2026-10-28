# MemPABench independent source review

Decision: **accept, with scope**. Blocking findings: **none**. This accepts the fixed reading record as a bounded source/static-code review; it does not certify a runtime, provider, experiment, performance result, or SYSTEM-99 completion.

## Fixed inputs and actual reading

PROJECT_ROOT: `/workspace/scratch/95d615402a52/agent-run-1202`.
Read-only HEAD: `418560d4a8d76b8c23d069bf7d587a5fb974c6eb`.
Read AGENTS.md; workflows/project_document_workflow.md; shared-references/project_memory_workflow.md and knowledge_access_workflow.md; current TASK navigation and SYSTEM-99 Plan Version54/current continuation entries. GUIDE.md is empty (SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855), not fabricated human authorization. No private `.agent-memory/` ledger exists here; no hidden memory was inferred. Existing advice search found DUAL-20261007-v1/MEM-SCOPE-01 navigation references, not task authorization or adopted new requirements.

Independently read the frozen text itself, not only the producer summary: Unicode character ranges [0,32500), [32500,48000), [135858,153001), [173271,181861), [279328,287500). These cover main1–6 and declared D.4/E/F/G.3–4/H plus opening I.4. Ranges are Python decoded-string offsets, not byte offsets. References [48000,73888), unlisted appendices, remaining I.4, rendered figures/PDF, author source, raw experimental data and replication remain excluded. SHA256 verification read complete file bytes but is not a claim to have semantically read excluded content. HTML and abstract were hash-bound only, not separately body-read.

Verified SHA256:
- reading.md: 7cb980a2fc713d7478541d42a3e736882927e9f1659d07fb783951d96d1bfe86
- inputs.json: 6de4d5326d2b11d1de64012d432d0adeefd601585fde779060f52c4509aaa105
- primary txt: 577bd146d261ab9ea8d88ca0a03ad96114f4b3b7e53edb660174722bc2e25ac6
- primary HTML: 3b8e5c1737a5aa6a52795288a5514e96e247d890715d94138c5f6ec3fa1cf72a
- abstract HTML: 65d83f87312b24089f4a9f505dd49ac33cf96330115c920a27abedc0dcf91cbf

## Findings against the original source

1. Main3.1–3.5 correctly separates acquisition, selection and realized public behavior. Four television-derived anonymized personas are not four sampled real people. Each timeline has94 live accumulation sessions plus5 fixed prerecorded changes;20/112 cells change once. Probe snapshots discard probe effects and prior raw conversations. Three repeats do not constitute independent longitudinal histories.
2. Main4 and F.1 explicitly preserve condition-specific histories. The reference worlds use the same user’s DeepSeek File checkpoint with memory cleared; this is not a common frozen world/history across all arms. File reads its full consolidated file while retrieval is top10/4000tokens; memory writers also differ (DeepSeek vs GPT5.5). The draft correctly avoids component-level causal superiority and matched-cost claims.
3. E.1–4 supports the wrapper descriptions: one selection per activated attribute/session, public delivery/action control, no gold-target repair, memory excludes held content/policy traces. Correct selection can coexist with a public contradiction; G.4 directly demonstrates hidden rationale being restated publicly.
4. F.2 supports the distinction between invalid-present selection, model-contract floors and unresolved missing artifacts. Required-call failures receive reminders and at least3 runs; six other floor cases are not rerun.67final/3pre floors remain in denominators. One Oracle PRS is absent (27/28 for that repeat). No claim to have enumerated all recovery calls is warranted.
5. F.3 resamples probes within each of four users, carrying all four backbone/three-repeat outcomes together; CS/PET resample pairs/cells. File PSA +9.6pp interval [+3.9,+15.6] is correctly quoted. CS difference -7.4pp [-17.1,+1.4] neither establishes equivalence nor proves deterioration. File carry-over increase and PET increase have positive difference intervals. The draft correctly keeps clustered units and conditioned populations distinct.
6. Main5 Finding2/3 supports7/334 vs60/111 applicable-evidence samples and the two UserB storage/retrieval cases. They do not establish universal retrieval failure, unobserved store contents, or full-file superiority on task quality/cost.
7. H and D.4 support shared Gemini BRS/PRS and the418-probe alternative judge, File-only preference-exposure audit, and1839 sentence judgments/~300 human reviews. The author’s whole-audit no-leakage finding is not exhaustive human inspection of every generated sentence. Agreement/correlation is not absolute correctness. Fictional/fallback persona cells further restrict generalization.
8. I.4 opening explicitly decouples task completion from preference score, gives direct preference questions score1, permits200character tool argument/result displays and discards/rescores invalid quote/tool evidence. The draft correctly does not convert those benchmark rules into a general prohibition on clarification/permission or a guaranteed single-call cost.
9. No read source establishes matched full-role billing, actual complete model input, complete wall-time, or gains for this repository. Reported cap/timing facts are not complete expenditure. The draft’s adoption is an evaluation direction, not implementation authorization.

Nonblocking wording refinement: replace “pass rates, conditional on correct selection and BRS>=4” with “within correctly selected final probes, the fraction with BRS>=4.” The denominator is correctly selected final probes; the numerator is those final probes with BRS>=4. The adjacent draft paragraphs make the intended distinction clear, so this does not block acceptance.

## Limited repository relation

Independently read relevant source sections; hashes match inputs.json:
- agent_runtime/project_memory.py:253–377, especially _descendants/_revise/correct/check/_context_closure. Declared dependency descendants become stale, old revision becomes superseded, raw external files are not rewritten. Hash1f0fe4edc8abf2371972817083c2c12cc33dbb07640ed57dffc2d8a744b35e41.
- agent_runtime/handoff_basis.py:144–188 and270–end. Consumer-required refs/claims are checked; selected basis retains required claims plus candidate/rejected claims and declared ancestors, hydrates memory/knowledge dependencies, and enforces serialized payload budgets. This explicitly leaves scientific applicability/hidden-dependency completeness unchecked. Hash20b4e127726f046b564086d2c5028ba92e986c6b796784a23cfe94971071f50a.
- agent_runtime/dispatch_context.py:14–end. Freshness depends on host settings_complete/needs_complete/history_required declarations; unknown history inherits. Guide and write boundaries are checked, but host declarations do not certify behavioral uptake. Hash5f07b28b44ec623191c331274a63e6c5599c6036086665ad774e9e8c2b734e5a.
- agent_runtime/record_context.py:55–end. Source SHA and exact physical selected/global records are retained with explicit partial scope; caller must enumerate required closure. Hashfa094243790483a9b4463136254b7f1ff2d365951adcae504b62f32032d2940e.
- agent_runtime/reference_context.py:39–end. Restore checks complete parsed values/order against fresh exact source, without authenticating artifact validity or permissions. Hashf830ba1b52942e32313381163b18e7b0ac43e429758ea70f90d20e053963a56c.

These sources support the draft’s limited relationship only. No new defect, performance effect, complete model behavior or deployed host is inferred from static reading.

## Knowledge and execution boundary

Knowledge need: source-specific methods/statistical units and current repository facts, satisfied by original text and static source; no extra theorem needed. Located knowledge/README.md and actual entries. Read-only lexical query `rg -n 'bootstrap|聚类自举|cluster bootstrap|interaction preference|交互偏好' knowledge/entries --glob '*.md'` returned no hits. Broader lexical search for preference/cluster terms surfaced DPO and neuroscience social/wiring/taxonomy entries by title/snippet; they are unrelated objects/assumptions and were rejected, not used as guarantees. No knowledge runtime validation, cache rebuild, borrowed theorem or substituted corpus was claimed. knowledge_refs=[] (no adopted external knowledge entries).

Actual independent role invocations:1, no retry. All-role tokens/cost:unknown. Tests/models/backend probes/installations/old gate reruns:0. Shell/Python calls only read/hash/navigation plus this sole permitted report write. No source, guide, TASK, production, count or lock mutation. The reviewer did not increment29→30 or close SYSTEM-99. Manual independent AI review is not trusted runtime/provider certification; historical registration remains unknown. Producer must separately preserve its public readback/count conditions. Plan54 and all consumed historical budgets remain unchanged.
