# Knowledge access validation — 2026-10-07

User-authorized bounded integration, separate from the ongoing broad research batch. Baseline c66b5ce: coordinator knowledge routing exists; not all role entries route to it; Mailbox does not check knowledge references.

Acceptance fixed before evaluation: all 15 registered roles and both main prompts navigate to an executable access contract; consumer-owned knowledge root and required refs reject stale/missing/omitted dependencies without ACK; unaffected no-knowledge deliveries continue working. Actual fresh-context producer retrieves and applies or declines knowledge to a task, reviewer consumes actual output through Mailbox and independently checks it. Preserve command traces, output and limitations. No efficiency/quality A/B claim.

First test attempt: 6 passed / 1 error because the test author guessed non-existent math.buckingham-pi; runtime correctly rejected it. Corrected test to existing physics.dimensionless, without changing runtime behavior.

Host scope: current-turn host dispatch is available; no long-running model adapter is configured for this isolated check, so no tmux/daemon claim. Existing cloud automation is retained.
