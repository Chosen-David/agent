# Complete compact CLI JSON

Pass `--compact` before the subcommand to omit JSON formatting whitespace from
the complete response. Default output remains unchanged. All keys, values,
types, status, errors and exit codes remain part of the response; no memory,
result proof or blocker is summarized away. Persistent JSON/SQLite files retain
their existing format. No model or adapter request is changed by this flag.

Available entries (rollout tracked in TOK10-20261021):

| Entry | Invocation |
| --- | --- |
| Communication | `python -m agent_runtime.communication --compact --db DB --plan PLAN --root ROOT inbox reader` |

| Memory ledger | `python -m agent_runtime.project_memory --compact --root ROOT list` |

Use the existing default output for human inspection. Compact output is opt-in
for tools passing full JSON to a model. It is whitespace compression, not a
semantic summary and not a measured reduction in total session tokens. Each
round's result directory records the entire actual stdout (including the native
newline), stderr, exit status, tokenizer and immutable fixture bytes.
