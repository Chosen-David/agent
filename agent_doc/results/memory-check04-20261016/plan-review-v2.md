# MEM-CHECK-04 independent final plan review v2

Decision: **adopt** for bounded manual implementation and validation. This
supersedes the missing-detail disposition in plan-review-v1.md, which remains
historical evidence. This is a separate agent context's actual read-only review,
not a managed ReviewSession receipt, user authorization or result acceptance.

The review object is `.agent-runs/memory-check04-20261016/plan.json`, SHA256
`6f6cf437db52ff9c39935edf4505ae43d4d43467e2a62cf718b9b1d62c0f671f`.
Baseline HEAD remains `2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10`;
working tree is clean before source edit. The actual plan was reread after the
planner's revision; no tests or new measurements have been run by this reviewer.

All v1 prerequisite gaps are resolved: seven exact fixtures include the primary
256-node/16KiB chain, shallow/small, 512-parent width, multiple requested roots,
layered shared dependencies and short-payload deep chain. Seed41016, three
warmups per arm,21 randomized wall pairs,7 traced pairs, per-arm median ratios,
per-fixture <=15% latency regression and primary >=70% traced-peak reduction are
fixed before measuring. GC and build/equality work lie outside timed windows;
traced allocation windows cover the full check through transaction close and
return and do not supply wall-latency claims. One candidate and a30-minute CPU
probing/review budget are fixed. All raw values and failures must remain intact.

The intended iterator-frame DFS follows parents lazily, preserving _get and
document-check order and checked-before-parent cycle behavior, and explicitly
drops non-requested packet locals before descending. It retains requested output
packets and traversal metadata only. No SQL/schema change or cross-call cache is
in scope. Tests still must verify v1's full packet, exception/order, malformed
store, string-subclass, shared-caller and freshness matrix against pinned source.
The1024/1200-depth reliability extension remains separate from ordinary parity.

Intent, guide, assumptions, prior-result applicability and scope findings from v1
remain valid. Prior check03 timing data cannot establish this memory claim; no
model KV, RSS, SQLite native cache, QA, token or TTFT inference is permitted.
Empty human guide remains protected and the main agent remains sole TASK writer.

Independent actual code/data verification must follow production before any
performance conclusion or publication, and final regression and publication
readback remain downstream requirements. If any fixed gate fails, retain baseline
or save an unadopted candidate and negative evidence without threshold tuning.
Material changes to this frozen plan require versioned review.
