# Pinned source inspection, not installed or executed

`obra/superpowers` SHA `8ca22dba9a94f28898bbce59f2537ff4d87c747d`,
commit date 2026-09-25; remote resolved again 2026-10-07 Shanghai date.
This SHA was already in the source ledger. The paths below are new reading,
not a claim that an unchanged upstream release is new.

- [receiving-code-review/SKILL.md](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/receiving-code-review/SKILL.md): full entry read; no script dependency. Verify applicability and compatibility before fixing feedback. Not a durable communication protocol.
- [subagent-driven-development/SKILL.md](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/SKILL.md): read setup/plan identity, report contracts, task review, finding/fix loops, scoped re-review, final review and finish. Diagram details and some model-selection/preflight text are not counted as independently complete coverage. Main prompts/templates not all read.
- [scripts/review-package](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/scripts/review-package): full script. Validates nonempty descendant commit range, writes commit list/stat/full contextual diff to a named file, then prints location. Calls `sdd-workspace` when output is not explicit.
- [scripts/sdd-workspace](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/scripts/sdd-workspace): full dependency. Plan-path marker disambiguates basename collisions, but adopts markerless legacy workspaces. Identity is path, not content hash; concurrent mkdir/marker writes are not a transaction. No claim this solves our receipt crash window.
- [re-review-prompt.md](https://github.com/obra/superpowers/blob/8ca22dba9a94f28898bbce59f2537ff4d87c747d/skills/subagent-driven-development/re-review-prompt.md): full template. Carries previous findings and exact fix range; verifies each original finding and new fix breakage, logs unrelated observations separately.

Useful comparison: artifact references and scoped original-finding rechecks are
already strengths here. Existing eval snapshots add byte hashes rather than
trusting filenames. Review-package's one-file interface can inform the next
targeted real communication task without copying the runtime or adding seats.

Do not adopt automatic workspace deletion, five-round/model-tier policies or
unilateral parking of important findings: user preservation, current budget,
authorization and strict release gates govern this repository. An addressed
label and a ledger completion line are not independent scientific acceptance.
No external tool/runtime/Skill installed; no repository Skill modified.
