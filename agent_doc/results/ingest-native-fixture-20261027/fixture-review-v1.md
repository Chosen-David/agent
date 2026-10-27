# Native fixture maintenance source/raw review

Verdict: **approve for the bounded fixture correction and report wording**, with corrected native execution still pending. No blocking source finding. This is low-impact CI portability maintenance review, not a third publication-repair plan review, a new local result acceptance, or a reset of any consumed budget.

I read the complete report draft, changes.json and static-delta.json, the actual complete diff for all four test files, and the selected decoded test/sync excerpts for all five jobs of workflow `40480391048` at `f34fbadac9b296debf344b7b3d5ded34748ec2eb`. I hashed actual candidate files and the evidence below. No tests, benchmarks, CLI/model/backend probe, replay, rerun API or production change was performed. This file is the sole review output.

## Raw failure and applicability

Both Windows excerpts show eight publication methods passing and the integrated after-final-guard method failing at its expected-exception assertion. Each also shows five scope errors in setUp: default-encoding read_text selects cp1252 and fails decoding UTF-8 metadata at byte 0x90. Both FIFO methods are explicitly skipped as POSIX-only. The combined ingest step reports 16 methods, one failure, five errors and two skips, with exit 1. These are retained failures; they cannot support a Windows suite-pass claim. Later read-boundary/index methods are not present in these Windows excerpts and must remain unexecuted/skipped for that workflow, as reported.

The macOS and both Ubuntu excerpts show the nine publication plus seven scope methods passing, then all five read-boundary and fourteen index methods passing; they include execution of the sync step. These are actual native evidence for the old fixture bytes in their recorded environments, not proof for every platform or the revised fixture version. I inspected selected test-step excerpts, not full binary job-log archives or a fresh provider readback of the job-status API; root owns the job conclusion/readback provenance.

The integrated hook compares `Path(path)` to a destination derived from the unnormalized temporary fixture path, while ingest resolves its corpus root and returns absolute guarded paths. That comparison can miss the actual guard calls when temporary paths have different alias/canonical spellings. Resolving the temporary base before deriving all paths is a legitimate way to align this fixture with the runtime path contract. However, the original exact Windows path pair and hook call counter were not captured because the expected-exception assertion failed first. The raw failure alone cannot establish which spelling differed or exclude every alternative cause. The report correctly labels the short-alias mechanism as inference, preserves the failure, and requires corrected native execution to reach the unchanged two-call assertion.

## Source correction and preserved assertions

The four actual diffs contain only explicit `encoding='utf-8'` on intended corpus/draft text I/O and `.resolve()` on `Path(self.tmp.name)` fixture construction. The production corpus contract is already UTF-8; removing locale-dependent decoding/writing in these fixtures makes the input bytes match that contract. Resolving owned temporary fixture paths does not relax KnowledgeStore's symlink rejection, replace the native publisher, mask an exception, or remove a collision condition. TemporaryDirectory retains its original cleanup ownership.

No test case, assertion, skip predicate, native mock, expected errno, injected edit, method count or test command was removed or weakened. In particular the integrated test still asserts refusal, exactly two matching guard calls, empty claimed-target preservation and cleanup. The read-boundary suite still checks exact byte limits, invalid UTF-8, Unicode/newline preservation, provenance/ref identity and isolated execution. Existing index candidate exclusion and stale/ref/CLI checks remain. My inspection of the actual diff agrees with the reported AST projection equality, while AST equality by itself is only a static preservation check.

Production SHA-256 remains `5349e9c44f3be03d1a7dbc291562dfe98a71f1c532d302c49a8ffd5aa381e039`. All four actual candidate hashes match changes.json:

| File | Previous SHA-256 | Corrected SHA-256 |
| --- | --- | --- |
| test_knowledge_ingest_scope.py | `a09576e86f870d8aaba3199663e45826127ca0042fa5c18d6f49e800d074efde` | `bf8bb7f24c75ec617dcd8ef63e46558fe5f3a0ed622f2ab3497914d9e6b72a04` |
| test_knowledge_read_boundary.py | `a816582b4cd169749234c19622f4e9abcb833abb9738f59cce75f3b7e81d57da` | `3811cc9dcf2f2de94fd5b601c1c3b3c9c56a8000878ae8f3df7cdf6db3ba0f9c` |
| test_knowledge_index.py | `7b57535f9f1c6c74c02cf3aa66c1f376de9cc000a2b54db65348ecffacc2f67d` | `13e20d0dd24f38e3409003e2259d23a1cb3fda3e813a67521d29e1812fee52dd` |
| test_knowledge_ingest_publication.py | `5414b964d3892b83cc07424a4ce0583bb5d1cd0522cc6469a13f8864ecb641a6` | `2cffc72c3deaa4dc7128189b5119e154933dbfebfb09aaacddfd891e6578cc4c` |

## Wording, execution limits and remaining acceptance

Report SHA-256 `1e91b927602eab21fbb609446f60d76354253facd0c17a9b20936e21b31dad1c` is accurate within the reviewed source/raw scope. It distinguishes selected decoded excerpts from full archives, the unlogged alias hypothesis from measurement, old local results from revised fixture inputs, and source review from future native acceptance. It does not claim the corrected fixtures ran locally, excuse the Windows failures as passes, claim a performance benefit, or close SYSTEM-99.

Persistent user CI-fix/main authorization and the repository low-impact maintenance boundary are supplied by root; this review does not create authorization. The corrective ordinary push is explicitly a new fixture-input version, not an unchanged-test replay or a hidden rerun of the original frozen phases. Preserve the first YAML zero-job failure, both actual Windows failures, and the previous complete raw results. Original two-of-two plan reviews and one-each baseline/fixed/independent phases remain consumed. No new local execution is accepted or requested. The one corrective native workflow must show the revised fixture hashes' actual outcomes, including integrated hook reachability and any remaining Windows errors; preserve any failure and do not automatically retry.

The original production acceptance remains bounded by final-read/check-to-syscall, hostile-parent and cleanup-identity limitations and the other unresolved SYSTEM-99 quality/cost/host gaps.

## Reviewed evidence hashes

| Evidence | SHA-256 |
| --- | --- |
| changes.json | `d4a7ca6d81d796272274f94008a2ed8b82e89f3a4839ed732387b01ff7da0678` |
| static-delta.json | `9bdf332b7ca1c561241483598f4e520154f188da2411c53cc561f6f87aea2822` |
| native-122108928252.json (macOS) | `86d3853287592e695819d343606a8dbceda7112d9e910209936254bf2061c67c` |
| native-122108928543.json (Ubuntu 3.12) | `a92d212acac70a9da73d242287fa81732086793eb75cf1cdc4f05d66f5dfff5a` |
| native-122108928563.json (Ubuntu 3.10) | `c24d7ef3a367b1d6d399eacd647cce9c365ee6f409e3ae0883cda413e6e9c81d` |
| native-122108928585.json (Windows 3.10) | `5af7f6913ac4016f9a6bc428b579dea9fdef4e02f11c499dabfb3f8f0cd62f13` |
| native-122108928684.json (Windows 3.12) | `021b9f075b9e7addb7ecd59bbf86fa8816b742a6f76200e6cc584718cb6603d5` |
