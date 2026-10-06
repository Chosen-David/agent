# Independent scientific review: systems attempt 1

Reviewer: /root/full_paper_controller/scientific_review. Review date: 2026-10-06. Frozen working-paper rubric, not a submission score. PDF SHA256: 0a57d3dfb82b0aa28032c80503ca2507a6ee20e65219e406b938e708c79baed6. Adjacent JSON binds the complete collection output_hashes exactly.

## First-pass understanding before companions

Read the complete seven-page paper.txt before companions or this case’s implementation, followed by all seven final rendered pages. The question is whether a normal report of unfinished work should consume a bounded execution attempt and whether repeated observation should monopolize dispatch. The proposed local contract refunds only an accepted opted-in pending return, counts it against finite poll/time allowances, and persists a rotating scan origin. Strongest evidence is matched actual-runtime traces that isolate one-task accounting and a two-task ordering contrast, plus a contract suite. The study demonstrates local transitions, not general liveness, production reliability, exactly-once effects or latency gains. Both new rules are simple established design patterns; the manuscript presents a bounded regression characterization rather than claiming algorithmic novelty.

## Acceptance and findings

All eight criteria pass for the requested working-paper artifact. No confirmed blocker or mandatory revision. The manuscript is a small scientific argument about a concrete counterexample and operational contract; that does not establish venue-level novelty. The independent replay and source review support its narrow conclusions, including negative outcomes.

### 1. research question and specific gap motivate mechanism — pass

pp1–2 Introduction asks separately when pending consumes an attempt and whether repeated pending excludes an independent ready task. The candidate mechanism in §2 separates observation bounds from attempts and persists rotating selection. The specific motivating gaps are the predecessor immediate failure and six-turn exclusion; p2 explicitly disclaims new scheduling theory.

### 2. design definitions/conditions sufficient for reconstruction, distinguish existing method from this study — pass

p2 §2.1 distinguishes handler outcomes, persisted statuses, attempts, polls, dispatches and verification; §2.2 gives valid policy ranges and conditional accounting Eq1. pp2–3 Eq2 and text specify both budget checks, claim-time t0, cumulative counters across retries and diagnosis before due polling. p3 §2.3 specifies cursor algorithm and accepted-result token/lease/cancellation conditions. §3 gives clock, task ordering, handler responses, attempt limits and all seven scenarios, with replay in p7 AppendixA. Actual source diff and candidate tick/validation/wait_limit agree.

### 3. claims/numbers/citations agree with supplied evidence and negative results, no false novelty, significance, timing or GPU/training claim — pass

Independent replay using copied frozen cores returned byte-identical traces.csv (84 rows) and test_results.json. Completion: baseline fails after1 dispatch; candidate completes dispatch5 with a1,p4. Competing task: baseline slow x6; candidate slow,quick,slow,slow,slow,slow and quick done turn2. Poll limit: candidate blocked at p2,a0 after2 dispatches. Elapsed limit: blocked pre-dispatch at1101 with p1,a0. Legacy/cancel and pending-then-retry match Table1.

Read unchanged suite source and verified identical baseline/candidate test hashes. Replayed suite has candidate12 methods pass; baseline failures15/errors4 across12 methods, as p5 §4.3 explains. No conversion to19 independent tests or statistical superiority. SHA256 of actual core bytes agrees with source_versions.json and AppendixA prefixes. GPipe §2.2/Figure2/§3 source passages support the limited comparison.

### 4. results organized around discriminating questions and interpretation with actual comparative evidence — pass

§4.1 compares completion and explicit retry to resolve counter meaning; §4.2 keeps both variants below A20 during six ticks so premature exhaustion does not explain absence of quick service. Figure1 separates cumulative count from dispatch identity. §4.3 and Table1 retain all seven scenarios, blocked/failed/cancelled distinctions, missing fields and unchanged legacy behavior. p6 acknowledges bundled intervention and missing factorial ablation rather than inventing causal latency estimates.

### 5. paragraphs develop scientific argument with precise terminology and natural connective prose, process logs separate, no fabricated polish — pass

The opening develops the observation-versus-failure problem rather than a build/audit narrative. p2 paragraph beginning We use attempt counter corrects the tempting failure-count interpretation. p5 paragraph beginning This is evidence about service order links equal dispatch totals to different task service and explains why finite exclusion is not infinite starvation. p6 explains realistic-handler and coupled-eligibility limits. Definitions support natural connected argument; commands are in AppendixA and operational records in companions.

### 6. full source compiles, every figure/table corresponds to evidence and final PDF all pages are readable — pass

Compiled copied full source with pdflatex exit0 in review-owned systems-build. Opened and read all seven original final PDF pages at1.3x, including AppendixA and references; no clipping, garbled formula or unreadable figure/table observed. Figure1a values1 versus1,2,3,4,5,5 and Figure1b task identities agree with full JSON traces; Table1 agrees with all14 variant/scenario outcomes. PDF SHA256 0a57d3dfb82b0aa28032c80503ca2507a6ee20e65219e406b938e708c79baed6.

### 7. related-work distinction and limitations are substantive — pass

pp5–6 §5 attributes durable state, leases, authorization and verification to the predecessor, identifies actual new deltas and distinguishes GPipe model pipelining from observer service order. Explicitly leaves novelty relative to workflow/fair-queue/retry literature unestablished. Substantive limitations include fixed token verifier, immediate deterministic handlers, no real jobs or contention, global rotation affecting legacy multitask scheduling, bundled intervention, cumulative wait counters and trustworthy-pending assumption. No broad reliability, latency or general fairness claim.

### 8. exemplar-derived blueprint choices implemented with actual locations and appropriate rejections — pass

All five blueprint decisions visibly implemented: organization pp1–3 problem->semantics->design; claim/evidence p2 conditional equations versus pp4–5 finite contrasts; figures p4 counts/identity and p5 all-scenario table; rhetoric p4 attempt meaning and p5 service interpretation; content rejection p6 omits production/throughput/theorem claims and p7 houses commands. Actual source anchors inspected: EX05 Figure2 p3 pixels and §§2.2/3 pp3–4 text; EX04 pp4–6 and p5 pixels; EX06 p2 conditions. The analogy transfers question-driven schedules/conditional claims, not GPipe performance data. No claim that all182 exemplar pages were re-read by this reviewer.

## Artifact fit, prose and contribution assessment

The manuscript’s result is intelligible without the acceptance records. It introduces the two failure mechanisms, defines counters before using them, specifies an executable transition contract, and asks distinct questions of the traces. Table1 is not merely a log: it shows that completion behavior changes while explicit retries remain bounded, observation exhaustion blocks and selected legacy/cancellation behavior stays the same. The interpretation following the competing-task result (pp4–5) matters: equal total dispatches cannot imply equal useful service, and a finite attempt bound prevents an unjustified infinite-starvation claim. The method’s cumulative time origin (p3) and the global nature of rotation for legacy tasks (p5) are concrete subtleties often omitted from a promotional account.

The contribution is modest: a reproducible implementation-specific case study and a clarified pending contract. Related work is the weakest part for a future venue submission. GPipe is a useful schedule-visualization and resource-problem contrast, but not a close retry/observer scheduler baseline. Crucially, pp5–6 explicitly name the actual predecessor as the closest tested comparator and leave broader novelty unestablished. For this bounded working paper, the honest positioning satisfies the rubric; it would not satisfy a claim to novel general scheduling. If the target changes, a focused comparison against real workflow heartbeat/retry semantics and fair-queue literature should precede stronger novelty or deployment claims. No forced additional benchmark is required to validate the present local characterization.

The title and §4.1 heading use retry/failure-opportunity language while attempts includes successful completion, but §2.1 explains this exact mismatch and the result follows that definition. This is not a confirmed error. Repetition of bounded scope is proportionate to avoiding specific overinterpretations. AppendixA occupies a sparse seventh page; that is readable and does not weaken the argument under this task’s non-venue format.

## Actual checks and limits

Used frozen research-review guidance already loaded for attention; no change of rubric. Read full manuscript, actual baseline/candidate diff, candidate validation/wait_limit/tick transaction and result paths, suite source, source manifest, protocol section S, and reproducer systems function. Read raw CSV and full JSON dispatch identities, and recomputed variant/scenario outcomes in systems-data-check.json. The suites’ source hashes are identical. Copied the study to review-owned systems-replay and executed the actual reproducer, not a rewritten semantic model. All84 CSV trace rows and test_results.json are byte-identical with supplied run01. Random tokens/paths/database bytes were not claimed identical. Inspected suite logs:12 candidate methods pass; baseline15 failures and4 errors reproduced. Copied source compiles with pdflatex; all original seven PDF pages were actually viewed, not inferred from successful rendering.

Checked GPipe’s actual original §2.2, Figure2 and §3 passages on pp3–4 and its Figure2 original pixels. Checked blueprint anchors against actual FlashAttention pp4–6, Deep Sets p2, and shared preflight analysis/synthesis. The ten-paper reader records are available; this reviewer did not redo their entire182-page coverage. A bounded current-source search on2026-10-06 found the official GPipe publication and Temporal’s Tasks and long-running-activity/heartbeat documentation (https://docs.temporal.io/tasks and https://github.com/temporalio/documentation/blob/main/docs/design-patterns/long-running-activity.mdx). The latter is a follow-up literature direction, not a tested baseline or evidence of equivalence. I did not complete a comprehensive current scheduler survey; the manuscript does not claim one or assert general novelty.

Support files: systems-data-check.json, systems-replay.log, systems-build-check.log and systems-page-1.png through systems-page-7.png. Third-party original-source previews remain private and are excluded from public archiving in review-manifest.json. English only; parity not applicable. The controller and separate PDF reader retain independent acceptance authority. No author output/repository modification, no held-out manuscript/grades read, no repository release statement.
