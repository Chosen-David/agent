# MEM-SCOPE-05 candidate2 / plan v3

Parent: approved plan.md+plan-v2.md and canonical stable detail v2. Preserve
v1 candidate source hash542e59295a75322e286a4a26d2d5381a8b4916b608497b87119e584d376e99a7,
raw-primary.json, benchmark-primary.log, red.log and targeted.log. Candidate1
control all-active-all-match regressed15.966%, beyond15%; rejected for promotion,
pending independent validity inspection of raw data. No threshold/sample removed.

Candidate2 coherent change: keep original mixed-status fastpath unchanged. For
newly homogeneous-status stores, require builtin-string scope AND evidence of
different raw scope values before metadata-first pruning. Query:
SELECT 1 FROM entries WHERE scope IS NOT (SELECT scope FROM entries LIMIT 1) LIMIT 1
If uniform/empty scopes, retain original eager fallback. IS NOT handles null and
BLOB safely as a conservative raw-SQL guard, not as Python membership evaluation.
All same raw scopes yield no discrimination among API-valid rows, so decoder
plus per-row filter adds overhead when allmatch; allnonmatch uniform stays slow
conservatively. Semantically equivalent JSON with different encodings may still
use new path; guard is not a complete selectivity estimate or universal speedup.

Still O(N) metadata work, no index/migration/cache, no test-ID or input-hash branch.
Exact thresholds/config/21pairs/budget remain unchanged. Candidate2 is last allowed
revision; stop on failure or original30min deadline. New raw paths exclusively
raw-primary-v2.json and reviewer/raw-independent-v2.json. Original runner hash and
aggregation unchanged. Both target gains and all five controls must pass in
primary and independent runs; do not count failed candidate1 as an accepted speed.

Before implementation, independent reviewer must inspect actual candidate1 code,
runner and raw samples/medians, plus this revised routing, approve or reject.
Stable canonical task Plan is explicitly version-reconciled by this file; before
publication root updates canonical Plan to v3 and reviewer checks exact bytes.
Tests must include uniform/mixed raw scopes, NULL/BLOB, no/all matches, all four
homogeneous statuses, all fallback types, correction and writer lifetime. Existing
structural test has varying raw scopes and should pass only withmatching hydration.
