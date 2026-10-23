# Independent bounded compatibility validation

Task: SYSTEM-99 continuation, Python 3.9 knowledge ingestion. Base HEAD a1f61112366bff8393d6f85b2b1c8c35e4829c31. Reviewer /root/python39_ingest_review. Verdict: usable-with-scope for this patch; no blocking defect found.

Read AGENTS.md, decision review, project document authority, model-with-knowledge SKILL/execution/workflow and actual source/diff. Reviewed three source changes from Path.write_text to Path.open/write with the same UTF-8 and explicit LF behavior. Serialization, normalized input hashes, candidate status, corpus snapshot validation, destination check and atomic rename path unchanged. Generated copy is byte-identical. Only the modified ingestion path is validated for Python 3.9; the Skill still documents Python 3.10+ and this does not certify the entire agent/runtime/skill catalog.

Independent commands (all executed from repo):
```text
/root/.local/bin/python3.9 --version
Python 3.9.25
python --version
Python 3.12.14
/root/.local/bin/python3.9 agent_doc/results/py39-ingest-20261023/independent-probe.py
python agent_doc/results/py39-ingest-20261023/independent-probe.py
```
Both probes exited 0 and printed module + isolated candidate outcomes. Probe code retained at the exact path above. Each interpreter ran a separate module import and standalone `python -I <copied skill>/scripts/knowledge.py --root <temporary corpus> ingest <draft.json> <draft.md>` with CRLF, bare CR, LF, Chinese UTF-8, U+2028 and no final newline. Independent assertions checked exact stored UTF-8/LF body bytes; exact serialized metadata bytes; source-normalized metadata/body hashes; LF provenance and candidate refs; every prior corpus file hash and record unchanged; duplicate import rejected without altering existing imported bytes.

```text
/root/.local/bin/python3.9 -m unittest tests.test_knowledge_read_boundary tests.test_knowledge_ingest_scope
............
Ran 12 tests in 2.343s
OK
```
`git diff --check`, `cmp agent_runtime/knowledge_ingest.py plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_ingest.py`, and `python scripts/sync_plugin_references.py --check` all exited 0 with no output.

Validated candidate source hashes:
- agent_runtime/knowledge_ingest.py: 29a1b5e75232bfc2d5badf103f102ae045cec61ff24948abb626ab5412309c44
- plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_ingest.py: 29a1b5e75232bfc2d5badf103f102ae045cec61ff24948abb626ab5412309c44
- tests/test_knowledge_read_boundary.py: a816582b4cd169749234c19622f4e9abcb833abb9738f59cce75f3b7e81d57da

Limitations: Linux x86_64 only; no actual Windows execution, all Python 3.9 APIs/runtime modules, live gateway/model/tmux, LLM/task quality, token cost, performance, publication or remote readback claim. Temporary corpus only; original repository knowledge files untouched. The fresh fixture's source metadata was reused for format/behavior testing, not scientific endorsement of new knowledge.

## Public probe relocation recheck

Reviewer /root/python39_ingest_review independently compared the retained private probe with the public relocated probe. The sole code difference is repository-root discovery `parents[2]` → `parents[3]`, required by the extra directory level. Independently executed both public commands listed above with Python 3.9.25 and 3.12.14; each exited 0 and reported both module and isolated-import checks passing. Public probe SHA-256: `7f469dcc79bfe157f14adfecedaf762c10578427e4916bd019f5dd0d7d607b9b`. Relocation accepted within the same bounded scope and limitations; no production/quality/performance claim.
