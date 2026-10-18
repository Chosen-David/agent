# Independent report-only crosscheck

Verdict: **pass for the inspected report's bounded claims**, with one nonblocking wording typo below. This is a report consistency review, not another experiment, full-integration acceptance, publication confirmation or native runtime certificate.

- Reviewer: `/root/fts22_result_review`.
- Reviewed `report.md` SHA-256: `0bfe1ca55bbc123d28dac44d86a9455853f933f38e72f4b0d3d0d2db1103e1f0`.
- Compared with `independent-audit.json` SHA-256: `d4a36d9e6de4964850e273c568ed32ca8c6a66f80958538e3d0791f7988899aa`, its raw-data bindings and the earlier complete independent review.
- Rechecked production/mirror SHA-256 `8eb136aae4fab28b0f887c745e8d9e276948347a53af215e12659224b65c34d9`, and runner `15350846959d84bb64d792045eced373c3a26f851db40413367671aaf7067c62`: unchanged.

Independently regenerated every displayed table cell from the audited raw-derived numbers: all 14 primary rows, 12 rerun percentages and two explicitly unmeasured rerun rows agree at the shown precision. Counts are correct: 196/168 retained arm samples and 980/840 calls, excluding warmups, expected-output oracle calls and untimed boundaries. Each run's 96 boundaries and 115-record real corpus agree with the evidence. The producer targeted log confirms 82 passing tests; the prior independent log confirms 18.

The report faithfully preserves positive and negative cases, the absolute 0.5 ms allowance, lack of reliable general real-corpus speedup, noisy 256×512 behavior, full-function warm-cache timing boundaries, complete exclusion of `contended.jsonl`, and the native-provider limitation. It does not turn synthetic gains into model quality, throughput, memory, GPU or universal performance claims. Pending full-repository/Reader integration and publication are explicitly pending; this check does not certify their later outcomes. Research citations are described consistently with the retained research notes; this report-only check did not re-open external sources or certify their scientific interpretation.

Nonblocking typo: the final sentence's `未来源/输入/依赖变更后需重新验证` should read `来源/输入/依赖变更后需重新验证` (remove the stray `未`). The intended revalidation rule is clear from the independent review and the surrounding scope. Main owns that correction; no report bytes were changed here.

Only this assigned `independent-report-check.md` was written. No tests or benchmarks were rerun. Later report changes are outside this exact byte-level crosscheck; substantive changed claims need a new check, while main may record separately evidenced integration progress as such.

## Final report follow-up

The revised report SHA-256 is `917ca12dc92a5c5a6b618472352f540b6ed9a6a0421322b319aeedf467d7a556`. I read this complete revision: the numerical table, benchmark scope and limitations remain consistent with the prior review; the stray `未` is corrected and the integration paragraph now records completed local checks while explicitly withholding publication/deployment success. **Report consistency verdict remains pass.**

Read-only evidence checks confirmed:

- `full.log` ends `Ran 1273 tests in 128.963s` and `OK (skipped=8)`; SHA-256 `43e1421cd5d31a6d26c7f2b6272074de896ead10cab29712b33425b1a192db3f`.
- `reader.log` ends `Ran 3 tests in 1.632s` and `OK`; SHA-256 `356e303d3ef9e14a7c91177b412d4ae09160d1ce15b7519a17ae8aa214d12e27`.
- The eight skips comprise seven visualization dependency/font checks and one opt-in real-tmux check. They are not successful external-host integration tests.
- `doc-validation.json` is a successful canonical project-document snapshot, not an error object, and binds the current TASK index hash `42278b558f828448952a26b9c8506eade8f16b9ece88fae9e402450f82be9b0f`. Its SHA-256 is `581bc24696f6bdfc225b759f8dd952a1c9fdc1a419f9ea412a877510e992c389`. I inspected the CLI path: `validate` emits `snapshot_project_docs` on success and an error object/nonzero exit on failure. This is local document validation, not native runtime acceptance.
- Production, mirror and runner hashes still match the original review. The stable Plan prefix remains `b1318599c07a88bc45f384c0a6dd382926fbd3e3e7fadc5dc2b117ab66d4232e`.
- TASK marks the bounded optimization verified and explicitly leaves publication/readback main-owned; this check does not reinterpret that checkbox as remote publication.

These full-suite/document observations are independent **inspection of producer logs**, not independently rerun full suites. No experiment or test was rerun in this follow-up, and only this review file was appended. Remote push/readback and external deployment remain outside this verdict.
