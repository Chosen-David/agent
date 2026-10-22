# PAPER-SKILLS-01 independent result review

Verdict: **ACCEPT — usable-with-scope for embedded offline installation, invocation guidance, and the two bounded local writing/planning fixtures.** No implementation blocker found. Repository/runtime push and remote readback remain the main agent's publication step; this review does not certify persistence before that step occurs.

Reviewer: actual separate native collaboration context `/root/paper_skills_result`; review date 2026-10-22. This is an independent code/source/output review, not an authenticated runtime acceptance receipt and not cross-model-family evaluation. I read AGENTS.md, decision review, project document workflow, canonical PAPER-SKILLS-01 Plan v2, candidate diffs/new resources/tests, upstream source snapshots and both fixture outputs. Only this runtime review file was written by this reviewer; no tracked candidate files were modified.

## Code, provenance and closure

- Independently loaded both archives with the actual reader, then compared **every member's bytes** against `git show <pinned-commit>:<path>` in the actual source clones. ARIS: 584 members, commit `23745b69a14880b5716d1773e5d20f5f1e6ab1d6`; Nature: 99 members, commit `c6ae86c742705fd968b13c79db1a8518a84089d4`. Clone HEADs matched; no differing member and no missing skill-tree file in the selected upstream trees. LICENSE contents matched upstream exactly (MIT / Apache-2.0); source commits, archive/member hashes and attribution are retained. This is a selected source bundle, not a complete upstream application installation.
- Nature's entire writing/shared trees are present. Manifest always_load, all axes values and references.on_demand paths resolve in the selected trees; the targeted closure test checks >30 explicit manifest references. Uninstalled Nature sibling skills remain routing hints rather than falsely registered capabilities.
- ARIS includes all upstream `skills/` members (including Codex variants), all 51 tools and all 21 templates. Inspected plan/figure/write/compile/improvement main and Codex phase references and canonical helper resolver contracts; referenced shared contracts and named tool helpers are available. Moved helper shims' canonical skill-local destinations are covered by the entire selected skill trees. External models/MCP credentials/GPU/services and standalone CLI/monitor applications are not thereby deployed; docs expressly gate these dependencies and keep unavailable reviews blocked/provisional.
- Reader verifies archive digest, rejects unsafe/non-regular/duplicate/traversal members and verifies exact member inventory/digests before access. Extraction uses no-clobber mkdir and exclusive file creation; guide paths and resolved aliases are blocked. It deliberately retains an incomplete target after I/O failure and does not promise atomic publication or protection against same-permission concurrent processes. No upstream helper executes during list/read/extract. The controlled source manifest is not an independent cryptographic trust root.
- Navigation changes keep research-write as the existing entry, avoid competing host role registration, route host-specific ARIS sources correctly, preserve user/project/tool/budget authority and expose missing evidence/backends. No global settings/credential/service change is part of the implementation.

## Independent executable verification

I independently ran `python -m unittest discover -s tests -p test_paper_skill_bundle.py -v`: **8 tests passed**, including real setup symlink and copy installs, offline read/extract, uninstall, exact extraction, existing target refusal, guide/alias refusal, malformed CLI inputs, archive tamper and unsafe member rejection. I inspected the assertions rather than relying only on their pass label. These are local regression tests, not experiments supporting a scientific benefit.

Separately extracted each package to new temporary destinations and compared all **683 extracted file contents** to reader members, with no mismatch; checked CLI read bytes against archive contents. Independently checked runtime copies of helper, integration reference, lock, both archives and notice against repository bytes: exact matches. Runtime `agents/openai.yaml` and `references/workflow.md` hashes match runtime-before.json. Removing only the exact new entry paragraph and restoring the original description reconstructs runtime SKILL.md SHA256 `f485a6910de1c1b7fcb42601609e30e8b9281d73a19a1764c4c35816f814e3a7`, exactly the recorded original: original body otherwise preserved. The baseline record does not inventory every unrelated role; this review makes no independent whole-workspace preservation claim.

Inspected producer logs, separately from my rerun: 53 regression tests, 8 optimized tests, 35 integration tests and 3 reader tests passed. These are supporting producer logs, not independently rerun totals. Initial canonical detail heading schema error was reported; the main agent changed `## Plan v2` to `## Plan` with `Version: 2`. Current doc-validation.json is a successful project-documents/v1 record. Large-context cap handling is not runtime deployment evidence.

## Actual fixture output review

Nature `nature-use.md`: draft is exactly **100 whitespace-delimited English words**. Chosen axes match manuscript/algorithmic/abstract/zh-to-en/generic. It faithfully preserves fictional local scanning from 100 ms to 70 ms, small-project no-missed-target observation, untested larger projects, unknown complete-agent duration and memory. It adds no citation, mechanism, significance, novelty or universal accuracy claim. Fictional exercise status and lack of independent empirical verification are stated. The conditional local benefit follows the supplied invented figures; it is not a measured benefit of this integration.

ARIS `aris-use.md`: bounded plan-only Codex paper-plan draft with explicit provisional/unadjudicated and REVIEW_UNAVAILABLE status. Preserves subspace→near/far→L1/L2→main-attention design order, protected sink/window and fixed total budget. Budget conflicts are explicit rather than silently deleting protected tokens or expanding budget. Preserves the single user-reported local operator **3.31 times slower than dense**, distinguishes unknown ratio interpretation, and does not convert it into speedup or end-to-end evidence. Quality, full path and model end-to-end results remain unmeasured; future tests are only a plan. DAC year/track/template/page limits remain unverified because the fixture prohibited network; it does not import ICLR limits. No fabricated citations, positive performance result or completed review is asserted.

Both outputs list the actual fragments they report reading, distinguish plans from performed work, and avoid claiming whole-paper quality or submission readiness. Their visible content fits the supplied fixture requests. Root supplied native fresh-context identities `/root/paper_nature_use` and `/root/paper_aris_use`, observed requests/final outputs and stated explicit bans on network, experiments and other-model calls. This review did not receive a complete exported tool trace for those contexts: their negative action claims are **self-report plus root observation**, not independently authenticated proof that no external action occurred. That limitation does not prevent assessing output correctness or the independently tested offline interface; it precludes a stronger behavioral/compliance receipt.

## Acceptance boundaries and remaining owner

Accepted: byte-exact pinned resources and licenses; source/manifest closure for selected skills; offline reader/extractor and no-overwrite/guide refusal behavior; existing setup link/copy accessibility and uninstall; runtime resource/body preservation checks described above; bounded abstract/plan output fidelity and explicit unavailable-review behavior.

Not established: global host hot reload/slash-command discovery, complete upstream tool/backend operation, cross-family review, runtime-supervisor authenticated acceptance, real experiment correctness/performance, generalized paper quality, DAC/Nature submission compliance, completion of historical SYSTEM-99 or unrelated blocked work. Main agent owns exact-path commits/pushes, remote SHA readback and final user communication; completion must retain these distinctions.

## Reviewed candidate bindings

- `plugins/research-assistant/skills/research-write/SKILL.md`: `daba0d52b67c0aa4547f58182874ccfee17bb9ed6cbe47b8f87cb376dd0b635d`
- `plugins/research-assistant/skills/research-assistant/SKILL.md`: `14defef111bf7e5477cfe8ec1f83809c6254ec9fd97f682cd9a174ff1fe6c656`
- `plugins/research-assistant/skills/research-write/references/paper-skills.md`: `02bdae33c2d4275a118cf8d184c16f931f61618a3a25a2a689178df6bf11eb8c`
- `plugins/research-assistant/skills/research-write/scripts/paper_skill_bundle.py`: `6bba8b801f91fbab7aad99dff50f325e75020763060485db5ab0ef8168566eaa`
- `plugins/research-assistant/skills/research-write/assets/paper-skills/sources.lock.json`: `a9ec6b73fe6b3ea743e1f22208e5d33212b9d8a4ee556f285dbdd2f3193592b3`
- `tests/test_paper_skill_bundle.py`: `c06210ec20cad59bfd2276a02e1f29f4b84bfe4311c9f2faf4bf078dfee5d338`
- `.agent-runs/paper-skills-20261022/nature-use.md`: `95f0b82fc30dae02c2e45e5bc31742f95de4214c186b0f241d3e7e310dcc35ea`
- `.agent-runs/paper-skills-20261022/aris-use.md`: `b202ca1817b77698c037a9e8cb50e87136df6904ccf5b5622b29e1496cd41e20`

## Compression-only revalidation, 2026-10-22

Verdict retained: **ACCEPT — same scope**, for the current xz candidate. Original review above is preserved as historical evidence for the gzip candidate. Root reported the first remote-skills push returned HTTP 422 and old remote remained `8f28ac2`; this reviewer has not independently established the rejection's cause. Changing encoding is not evidence that any particular size rule caused the rejection. Persistence/remote readback remains pending main-agent evidence.

Reviewed changes: source archives now use `.tar.xz`; the helper uses tarfile auto-detection `r:*`; lock archive names/digests, NOTICE filenames and tamper-test filename follow this encoding. Independently compared all 584 ARIS + 99 Nature members again against the same pinned upstream `git show` bytes: zero differing members. Independently extracted both new archives and compared all 683 file contents: zero differences. The selected upstream commits, member bytes and licenses remain unchanged. Archive SHA256 is now `03ac657cf212600e11f299c49fb75f45b413bdb7c608a3411f1f0146161c79d0` (ARIS) and `2ca9189c7078d5676aabe15c0de9f2cab1885c0579564e4e62d7b9a765d3773a` (Nature).

Independently reran `python -m unittest discover -s tests -p test_paper_skill_bundle.py -v` against xz: **8 tests passed**, including actual setup symlink/copy install and offline extraction. Runtime helper, reference, lock, notice and both xz archives exactly match repository copies; no stale gzip archive remains at runtime. Direct runtime offline ARIS list succeeds. Runtime whole SKILL.md intentionally differs from repository's newer preexisting skill body; independently reconstructing its original body still matches the original recorded `f485a691...` hash, and original runtime workflow/openai files still match their recorded hashes. This is preservation, not whole-SKILL repository equality.

Nature/ARIS fixture files were not rerun for the compression change. Their previous invocation outputs accurately identify the original gzip archive; that old archive digest must not be cited as the current xz digest. Their source instruction bytes and bounded content review remain applicable because every selected source byte is identical. No new behavioral execution claim is inferred from recompression.

Current candidate bindings (supersede matching earlier gzip bindings for changed files):

- `plugins/research-assistant/skills/research-write/scripts/paper_skill_bundle.py`: `799808a04b1aa46a9cbaa4ce75d48c1ab460474234432564c91e6f77bbd33fa2`
- `plugins/research-assistant/skills/research-write/assets/paper-skills/sources.lock.json`: `bd9888f0c0f0dcc76807bbfb91e13b58e8e4a55da9a29f375d4259ae24c247a0`
- `plugins/research-assistant/skills/research-write/assets/paper-skills/NOTICE.md`: `c5f6a058f7b9eac2aaef42e81f3c3b69bd078c9673dc96d61d9273bd85c8f09b`
- `plugins/research-assistant/skills/research-write/assets/paper-skills/aris.tar.xz`: `03ac657cf212600e11f299c49fb75f45b413bdb7c608a3411f1f0146161c79d0`
- `plugins/research-assistant/skills/research-write/assets/paper-skills/nature-writing.tar.xz`: `2ca9189c7078d5676aabe15c0de9f2cab1885c0579564e4e62d7b9a765d3773a`
- `tests/test_paper_skill_bundle.py`: `2b839672ba0371c14f9d2d1fe437c921daec65d545d1cc8973ffb4ed5f351315`
