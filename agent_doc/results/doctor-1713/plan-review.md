# SETUP-DOCTOR-01 independent plan review

Verdict: APPROVE, bounded ordinary correctness repair. This is a native independent review call, not a machine-authenticated ReviewSession receipt or permission grant.

Reviewed plan Version 1 stable prefix SHA256 `742ba93aaf083509fc1d76a6c0b6dc143f4c40be075e99529b7315a2db007d1a`; baseline setup.py SHA256 `9ed8af9ff3f0d7665cf30579732aef7d627e441d7cfb01830173622b810963e1`, repository base c4a0311bf9d059ac97a865b91f0f5c195cf864a7. Read AGENTS, decision review, project document workflow, dual-main workflow, task detail, actual module imports/doctor/main caller. GUIDE.md is zero bytes; no guide writes authorized or performed.

- Intent: pass. Restore the authorized installer diagnosis entry without changing policy or promising system completion.
- Guide: pass. Empty human GUIDE; all guide paths remain read-only. Existing canonical TASK and one detail writer retained.
- Assumptions: pass. AST confirms `import re, os` is conditional inside doctor; Python therefore binds os locally throughout this function. Module-level os/re already exist. Removing redundant local import restores references on absent discovery as well as successful branch. Caller main does not catch UnboundLocalError, so this is a real unhandled entry failure.
- Prior results: pass. Prior MODEL-DISCOVERY-02 identified the suspicion but explicitly excluded doctor acceptance. Fresh baseline regression is necessary; no old passing count is reused as evidence for this fix.
- Acceptance: pass. Baseline failure, no-gateway and nonfallback paths, fallback None, mocked TMUX success/failure and unchanged subprocess arguments, real install/check/uninstall lifecycle and CLI JSON behavior are appropriate. Preserve exit 2 with errors for an uninstalled target; a JSON response is not a healthy-install claim. Include a successful-discovery fixture if convenient to confirm global re use; do not broaden to live gateway success.
- Risk: pass. Removing one redundant import has low risk and no added writes/commands; existing doctor model file mutation/manifest mismatch, stale pre-fix report, always-needs-restart and explicit discover ownership remain outside acceptance and must remain open. Mock tmux does not establish real server/config/scroll functionality.
- Resources: pass. Local CPU/temp fixtures, no network/model/server required. Do not alter other worktrees or deploy services.

No blocking finding. Independent result review and exact-file/nonforce remote publication checks remain required by the declared plan. Acceptance does not certify performance, model quality, whole doctor correctness, Windows or SYSTEM-99 completion.
