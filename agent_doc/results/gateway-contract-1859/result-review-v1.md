# GATEWAY-CONTRACT-01 independent result review — candidate 1

Verdict: REVISE. One blocking finding remains against the already approved error-redaction contract. Native separate-context review, not an authenticated runtime receipt or publication authorization.

## Blocking finding

`fetch_models` constructs `urllib.request.Request` before its protected network block. A malformed supplied base URL can make that constructor raise ValueError whose message includes the URL. main catches ValueError and prints its full string. Independently executed `main` with the synthetic schemeless URL `//user:reviewer-password-sentinel@fixture.invalid`, with urlopen mocked, returned 1 with zero network calls but printed the synthetic password in stderr. `reviewer-invalid-url.log` preserves the actual output. This violates Plan v1's requirement not to echo auth-token/base-URL credentials. It is not a live credential incident; only synthetic sentinels were used.

Repair within the same approved scope: catch Request-construction ValueError and raise a generic RuntimeError without URL or raw exception text. Add a regression on this malformed credential-bearing URL requiring controlled error, no sentinel/traceback and zero network calls. Preserve this failure and rerun the affected complete discovery regression/independent checks on the final source. Do not print credentials to improve diagnostics.

## Checks passed on this candidate

- Candidate final annotation/comment hash: scripts/discover_models.py `670b738fcfa9ecb942e1ccb34628492b706aae98299fbb0702e147b6c5de6da3`. The last source-only adjustment deleted misleading comments and corrected `_classify`'s return annotation to list[str]; no executable function body changed. I reran the 13-case suite normally and with -O on this final hash: 13/13 each, reviewer-final-normal.log and reviewer-final-optimized.log.
- Combined setup/portable/discovery/doctor/recovery/model-routing/install-profile/role-process integration: 73/73 pass, reviewer-integration.log. This ran before the comment/annotation adjustment; body equality plus final targeted runs cover that non-body edit, not a live service claim.
- Independently loaded `git show 44110e54:setup.py` as a module with the actual repository resource root, loaded the old discover_models.py and launched that actual old script for CLI tests. Final 13 regressions reproduce failures=17/errors=9, reviewer-baseline.log. Counts include subtests and are not distinct bug counts.
- Independent reviewer_probe.py executed actual discovery.main with bounded HTTP fixture, wrote its output, called real setup.install, then actual run_role.py --dry-run with no supplied inventory: default fallback. Explicit valid host inventory then selected the exact original opus policy model. Ordinary reinstall retained the explicit snapshot.
- Actual doctor CLI against a fake owned tmux executable exiting 7 returned configured JSON with warnings, empty fixes, and no actual tmux server call.
- HTTPError/URLError/TimeoutError paths did not print synthetic auth token, URL userinfo password or raw server reason. These checks do not cover the constructor error above.
- Exactly 1 MiB valid padded model JSON accepted; +1 byte rejected. Direct malformed model-ID inputs raise ValueError without string-method exceptions. Additional fixture output is reviewer-probes.log.

## Source and behavior assessment

Discovered entries are inactive false/[] schema values, so names cannot falsely establish model/tool/vision access. The native transport field is an inactive schema placeholder, not verified support. Explicit host inventory validation preserves availability, capabilities and transport exactly. strict_json and a +1 bounded read reject malformed/nonfinite/duplicate/oversize JSON before routing; invalid entries are rejected instead of silently filtered. Preview name labels do not feed resolve. These changes conform to the unchanged unknown-to-default resolver and explicit-model consumer contract.

The old doctor test adjustment is justified: nonzero tmux now belongs in warnings rather than fixes_applied, success remains in fixes; it retains exact command and five-second assertions and adds checks that the opposite list is empty. It does not weaken preservation of health results or promise a server.

## Evidence integrity and limits

I inspected original producer baseline and candidate/optimized/integration logs, and independently generated complete logs with 13/13/73 summaries and OK. The earlier unrelated partial-log issue is not treated as a pass here. Original evidence is retained; this review does not change source, tests, canonical TASK or human guide. GUIDE.md is empty. Plan stable prefix SHA256 is `1e9da3a515780d9944020bfaefe16633154723b51799404a890aa848fb5d1b68`.

No live gateway/model/authentication/tmux server, native Windows, throughput, model quality, total cost, automatic remediation of historical guessed snapshots or SYSTEM99 completion is accepted. Old stored inventory provenance remains unknown and is not mass-invalidated. Existing needs_restart semantics, exact endpoint wall-time behavior beyond configured socket/process limits, and broader unrelated installer limitations remain open. Publication remains blocked on the finding above and final source/result revalidation.
