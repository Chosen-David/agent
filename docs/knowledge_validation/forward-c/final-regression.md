# Targeted final-copy regression C

This is the requested targeted regression against `/tmp/knowledge-forward-c/skill-final`, not a new blind test. No repository, tests, rubric, other agents, or network was inspected. Original report.md and evidence.txt remain byte-for-byte unchanged.

- Exact section fidelity: `section physics.dimensionless s3` returned lines 8–12 with the terminal blank line intact. UTF-8 bytes exactly equal the corresponding original source-file line slice. PASS; earlier observed defect is fixed.
- CLI help consistency: `--help` now says “File-first knowledge retrieval, validation and explicit candidate maintenance.” The previous inaccurate “Read-only” description is absent. PASS.
- Standalone persistent index/search: built fresh `/tmp/knowledge-forward-c/final-regression.sqlite` using explicit root `/tmp/knowledge-forward-c/skill-final/assets/knowledge`; index updated 5 of 5 published entries. Physical query `单摆 周期 长度 重力 单位 量纲` using the same root and new database succeeded with backend sqlite-fts5-rrf-v1, physics.dimensionless ranked first, and its s3 instance passage identified. PASS.

All four CLI commands exited 0. Full expanded commands, actual outputs, independent byte comparisons, and unchanged-original-artifact checks are in final-regression-evidence.txt. Python ran with bytecode writing disabled. No source files or corpus entries were edited and no external verification is claimed.
