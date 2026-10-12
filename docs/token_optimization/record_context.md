# Explicit NDJSON record context

For a meeting already stored as NDJSON, the host can read explicit required physical lines, including every relevant global rule:

```powershell
python scripts/record_context.py --root ABSOLUTE_PROJECT_ROOT --path agent_doc/advice/meeting.ndjson --sha256 SOURCE_SHA256 --global-line 1 --line 17 --compact
```

The API validates the entire exact-version UTF8 source, including omitted records, before returning any selected raw line. Duplicate keys, non-finite numbers including exponent overflow, malformed/blank records, links, stale SHA and selection/budget errors fail. LF defines physical lines; CRLF, Unicode separators inside JSON strings and final EOF bytes are preserved. Limits:2MiB source,50000records,128distinct positive lines per selection list,1million display characters maximum.

The host must enumerate all required global/current/dependency records. This tool cannot discover that closure; use the full exact source when it is unknown. No advice history is removed, summarized, accepted or marked closed. Original human guide/permissions and result validity remain required. This CLI is opt-in and does not alter an existing conversation automatically.

[Round02 result](../../agent_doc/results/token-fifty-02-20261012/report.md) is independently usable-with-scope: one native controlled synthetic32record pair total19942 ->18531, saving1411tokens (7.08%), paired spend38473.17WSL tests pass. This is no live retrieval, long-horizon, full workflow or cash saving claim. Main verification is required before success count.
