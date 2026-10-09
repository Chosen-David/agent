# Communication research — checked 2026-10-10
Primary abstract The Cost of a Hop (submitted2026-10-02): https://arxiv.org/abs/2610.04053 . Connection overhead varies with hardware and end-to-end model dominance; only a mechanism analogy, not SQLite results.
AECP (submitted2026-10-05): https://arxiv.org/abs/2610.06481 ; previously selectedabstract/method reading, no reproduction. Structured artifact and consumer contracts motivate preserving every reference check even within batch; existing Mailbox is not AECP.
Author GitHub overview https://github.com/fujibee/agmsg inspected2026-10-10: sharedlocalSQLite cross-vendor messaging, not this repository's protocol/hostintegration. No upstream code copied orinstalled.
Primary engineering blog https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/ inspected2026-10-10: calleridentity and immutable intent important; duplicate event still revalidates refs/routes.
Official https://www.sqlite.org/lang_transaction.html manual: BEGIN transactions don'tnest, explicit rollback boundaries. Pythonruntime3.12 baseline contextmanager commits/rollsback/closes; https://docs.python.org/3.12/library/sqlite3.html (runtimeversionmatchedcheck required byreviewer).
Deepseek writebatching mirror search looked promising but primaryGitHubURL404; no reliance, no fabricatedimplementationfacts.
Novelty boundary: ordinary transaction amortization, explicit bounded opt-in atomicbatchAPI. No new scientific method or authorspeedup transfer; no token/network/LLMclaims.
