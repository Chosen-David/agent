# Independent manual reading/source review — SABench 0658

Verdict: **accept, scoped to the frozen reading record and static source review**. No required revision to the reviewed reading.md. This is one manual review invocation, not an authenticated ReviewSession, empirical result validation, reproduction, or production acceptance. All-role tokens and cost remain unknown.

## Identity and authority

Project: `/workspace/scratch/95d615402a52/agent-run-1202`, Chosen-David/agent only. Observed HEAD: `83099823ba35384e7e2d6635bd5782035fa315e3`. SYSTEM-99 detail declares Version 54 and index leaves SYSTEM-99 open. Dispatch binds stable plan `f6acab0acab813d56ea379700221747fbfd354262bd7223290527a208161bbee`; this review checks the supplied current files/version, not trusted runtime authentication of that binding.

Read AGENTS.md, workflows/project_document_workflow.md and workflows/knowledge_access_workflow.md, current TASK SYSTEM-99 entry, SYSTEM-99 opening/stable relevant Version54 section and recent reading progress, and guide README. GUIDE.md is empty; no human requirements invented. Read-only review and this sole runtime feedback path are the assigned scope. Main owns publication and locks. No TASK, guide, public report or production edits; no fetching, installation, backend/model/probe calls, tests, source execution, retry, cleanup or old consumed gate reset.

Frozen inputs independently hashed:

- reading.md: `042ad9cb148a922dbc26d9fa5c9e0453518ef7c897968788fc5224a082e22d81`.
- inputs.json: `e87906a451785a571c8910f0811519ce6ec3dfebb69647dc4d17ef98b5d636be`.
- Cached paper.html: `35b8bcc0bc26bea4f89331af1c17886a11ce39ba0176eda414790a9c643a6ed1`.
- Cached paper.txt: `d683a67465cc657e2ab5cb816439d6b6d56ade23b780bfb325d98dbd50f32a5e`.
- Cached abstract.html: `8f5e056a3d705d44f10a35529e649651be27e2a4dd8beb05575b86d6afd91501`.
- author-source-refs.json: `71574092e77175f70ca9fead4b6cb9c5c932927862ae534ce6c67e6f3e707b91`.

All paper/author caches above are under `.agent-runs/continuation-0556/`. Abstract submission-history lines160–165 identify v1, 25 Oct 2026 08:54:08 UTC. The review used those actual cached primary materials rather than treating reading.md as its own evidence. No fresh network provenance or rendered-PDF verification was performed.

## Actual reading and paper findings

Read cached text covering main §§1–11, Limitations, A.1–A.11, Tables1–10 and figure captions. The first broad output was truncated in its middle, so explicit supplemental slices 18000–37800 and47982–64574 were read to cover main results/discussion and appendices. References and navigation/footer were excluded from substantive reading credit. Confirmed HTML §2/§4 method paragraphs directly, including separate ordered W and set(W), final-state replay, idempotent exclusion claim and outside-workspace visibility definition. No figure-pixel or PDF page inspection claimed. Producer's prior0556 and new0658 character ranges remain a single paper, not two independent readings.

The record preserves the decision-relevant evidence accurately:

1. Method is task-specified authorization plus a narrow implicit allowance, with goal and CD separated. CD is contract noncompliance, not estimated harm severity or a universal permission rule. Ambiguous first decisions and vacuous goals require special handling. This synthetic policy must not narrow actual user authorization.
2. 201 tasks/47 templates/11 models/2211 pairs, one temperature0 run with stated16-step cap are paper-reported collection conditions. Unequal16-cell counts and overlapping state attributes are retained. Template-clustered10,000-resample intervals quantify corpus/template composition, not repeated-run/model-drift uncertainty; McNemar/Holm supplements do not create independent replication.
3. 337/2211 CD,252 joint and169 external-CD runs have distinct denominators from421 flagged writes and170 external flagged writes. The record correctly separates headline12.8% conditional CD from A.7's60/1477=4.1% nonambiguous successful cases. AB495 splits192/281/22 and unnecessary-clarification2.6–17.3% are accurately qualified as first-decision/proxy outcomes, not useful completed follow-up conversations.
4. A.8 relaxation is policy sensitivity, not evidence that linked-object writes are harmless. The same-entity13.3%, external-only7.6%,12/421 removed bookkeeping events and103/148 outside-entity events are faithfully distinguished.
5. Human audit is106 selected writes/62 tasks/3 unpaid non-author annotators,78 decisive majorities/72 agreements,28 without decisive majority,75 unsure ratings. Six oracle-flagged candidates judged authorized and contestable ambiguity labels preclude a population false-positive-rate claim.29-task/3-person behavioral study is descriptive and does not support human–model ranking.
6. A.10 is115 selected tasks, three models, paired prompt-only changes. Confirmation52–71% CD reduction costs13–17 goal points and retains5–12% CD. Preview cost1.7–6.9 goal points and significance only for Qwen; Holm-six correction and exploratory external-CD comparisons are retained. This does not justify installing a default confirmation gate, nor establish total latency/token/review cost or deployment benefit.
7. A.11 is an internal linked-ticket comment outside explicit/implicit authority alongside a permitted external reply; a permitted external action does not make the CD external. The paper's limitations explicitly leave coding-domain validation, long-horizon/memory transfer and follow-up-dialogue utility open. No repository rates or real-world security guarantees follow.

## Author source inspection and findings

Pinned author commit supplied: `1baf318fbdc55df2d190467a1b6bf91dfc5f6524`. Independently inspected oracle.py1–199 and registry.py1–238 in full, models.py1–120, state.py1–237 in full (producer's1–275 range simply extends past EOF), runner70–122/200–321/380–463, and README in full. SHA256 and `git hash-object` of each cached file match inputs.json's SHA256 and Git blob IDs. This verifies cached-byte consistency, not remote commit authenticity or exact paper collection configuration. The supplied commit timestamp was not independently authenticated here.

| Author path | SHA256 | Git blob |
|---|---|---|
| sabench_re/oracle.py |39d82b88442fd5980b03c9139d50cb80a94f7d6a833b35aabc0134ae16317279|ff03c2eed272f211661b0b62212687257b4f22b8|
| sabench_re/registry.py |fdec3cce529b851872ef2efdfaabdfb13ea6a6a8cacfe5209c91e331778b29f6|9446b5ed5b48bfc877b3942928b4a5419eafaf82|
| sabench_re/state.py |fbe1c17a2adcc9896f4a259c6017625a51982b6d93bf2c95f51344fe461ad57c|31f55fc0b5cb711c49cd7502158e8b5fa2f51273|
| sabench_re/models.py |b707ba769b81f5cd801ba8056a2208840080528062d7cb0e051a4f728f272f98|124105df43917aeffd65156a55d1a23be91db2db|
| scripts/run_pilot_streaming.py |28a0f664411b1076c4636960a786fc87cdfdc89b3a7edbf61ca829ea7118cc0e|763d848cc62e1250c0b6a589d807a4cc974432ca|
| README.md |0cfc2ab9fe33661355ae04ad814a61f822bf1f93fa1260e0672aac5327508b43|3a70ce2a330487a46dbe1f0cc44301db5a1d390b|

The five static cautions in reading.md are supported and properly bounded:

- **Replay sequence loss:** oracle73–79 returns a frozenset; models50–77 excludes step from equality/hash; oracle36 and state24–26 replay that set sorted by retained step at state14. Identical A updates separated by B updates can be deduplicated before replay, so a conceptual set-A→set-B→set-A history need not retain the last transition. This is a source-level counterexample to a general ordered-replay guarantee, not an executed fixture or a finding that any canonical published trace has this pattern. Paper's use of set(W) for authorization does not require discarding sequence order for goals. Global duplicate elimination is not an idempotence test relative to each intermediate state.
- **Externalness:** registry46–61 and134–155 fix external flags by API membership; the functions do not classify recipients or arbitrary ticket visibility from workspace state. This is narrower than the paper's general visibility language. No claim follows about actual service delivery or which released tasks are affected.
- **Clarification:** oracle43 uses all_agent_text and96–105 checks candidate identifier matches only. Question detection exists at113–124 and separate timing fields exist, but this entrypoint does not assemble A.7's zero-write/interrogative-final/distinguishing-candidate conjunction. Shared attributes can also count for multiple candidates. The record correctly leaves aggregation/analysis uninspected rather than calling published proxy counts disproved.
- **Successful registered writes:** registry134–155 trusts call.success; runner execute_tool_call constructs success=True and returns it for registered writes after apply_writes without a mutation-difference/target-validity check. State136–146 and155–157 can leave missing targets unchanged. Thus successful normalized operations are not a demonstrated guarantee of actual state mutation. No independent per-intermediate-state idempotence filter is visible in the inspected extraction path. This is not a claim about author data corruption or real APIs.
- **Collection binding:** A.4 lists email.move/ticket.close, absent from pinned WRITE_APIS; pinned registry instead includes email.label/ticket.set_priority/calendar.invite, and runner builds schemas from ALL_APIS. Runner defaults None temperature/12 steps and temperature-removal fallback differ from paper-reported0/16. Supplied flags or other collection versions may explain this; defaults alone cannot refute actual collection settings. Exact tasks, traces, metadata and analysis were not accessed, so impact and recomputability remain unknown.

Additional nonblocking source nuance: oracle82–93 discards task and permits mark_read whenever that message has another normalized email operation, even if the companion operation is unauthorized. This should not be silently promoted into a general user-permission rule. The reading already refuses such transfer, so no revision is required for its evaluation-only recommendation.

## Project source mapping and knowledge applicability

Independently read scripts/setup_codex.py in full, global template and CLAUDE.md in full, and publication.py1–65 header/shape only. Hashes match inputs.json: installer0172113dd327d4ea5ef43eacbb6a72c080373aee767b5d0fadd7939a653d288e; template024e4b1a2619fe3b63b6a2b1f6ac10fc8b7c3160dbbd98e49ca7b1df6e4a4790; CLAUDE a3afae8ea4d5f8452644c624ff0e818c0c91083e674fd6493112f059a099bb93; publication280bd9afa7650f7b203c00169ff4824fe98ddc71a442a930cb1977ad53bd04e6. AGENTS/TASK/detail/guide hashes also match inputs.json.

Installer checks committed snapshots, managed ownership, collisions, dirty export sources, backups/pending and post-write bytes. Its configured report explicitly says model_probe:not_run/scheduler:not_started. Those are file installation checks; they do not authenticate host-loaded prompts, semantic permissions, model behavior, complete recovery or end-to-end quality. Publication's inspected header states no stage/commit/push; no full publication lifecycle audit was performed. Existing race/multifile/recovery questions remain open, without claiming a newly confirmed production contract defect.

Independently ran the permitted read-only query `python -m agent_runtime.knowledge --root knowledge search 'authorization trace evaluation' --limit 3`. It returned snapshot767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18, backendfiles-lexical-v1, applicabilityunchecked, the same three mismatched candidate assumptions as the supplied query: similarity-invariants (linear endomorphism/change of basis), RS-GRPO (specified math-model training/sampling experiments), attention-output-geometry (fixed values/linear projection and margin). These objects do not establish authorization/oracle/trace validity. All rejected for this task; adopted knowledge_refs=[]; no theorem relied upon or candidate promoted. The CLI is the expressly permitted knowledge lookup, not execution/import of the inspected author source or a test/model call.

Read cached prior-result query: scanned329/results0/statusincomplete/partialfalse with25 missing-record errors. It supports no empirical reuse and no claim of exhaustive absence. No new experiment or measurement was planned or performed.

## Acceptance and remaining owner/action

Accept preserving all current limitations. Adoption is restricted to future evaluation design: compare actual authorized scope, useful goal achievement, unrelated writes, abstention/failure and total cost with explicit domain contracts. Defer a new scorer, automatic permission extraction, default confirmation/preview, model routing, shared-chat pool and architecture/directory migration. No numerical/performance/quality/security conclusion for this repository is accepted from the paper.

After main's public publication/readback, prior0556 plus0658 may count once toward34→35. This review alone neither increments a published count nor declares SYSTEM-99 complete. Main retains the open real-host/load/complete-input/task-quality/all-role-cost/concurrent-ownership/recovery work and all consumed/paused gates. Further author-impact verification would require canonical data/configuration/analysis and separately authorized, independently validated work; it is not implied by this acceptance.
