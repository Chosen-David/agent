# Windows UTF-8 follow-up (deferred)

Task: REFLECT50-20261021. Disposition: **defer** beyond the requested fifty
counted iterations; this is a diagnosed pre-existing product defect, not a passed
platform check or merely a test-fixture problem. Current changes preserve those
paths; final acceptance covers the specified local behavior and frozen data only.

Evidence: `agent_doc/results/reflect50-20261021/regressions-r1/raw.txt`, tests
`test_isolated_plugin_ingest_and_byte_identity` and
`test_isolated_index_and_tree_cli`. At baseline `27195c7d`,
`agent_runtime/knowledge_ingest.py:43–44,51` writes staging Markdown/JSON and
provenance without explicit encoding; Windows isolated Python can emit CP936,
then KnowledgeStore's UTF-8 read fails. Knowledge CLI output also has an
unaccepted isolated GBK path. Independent final review identifies these defects.

Proposed follow-up: explicit UTF-8 storage/output, regenerate bundled copies,
then independently exercise non-ASCII ingest and binary CLI output with `-I`
and CP936 defaults. Preserve collision, candidate status and provenance checks.
Separately retain the unresolved Windows locked-file read difference; do not
classify every old-suite failure as harmless or claim full platform coverage.
