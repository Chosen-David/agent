# Independent plan review: VALIDATION-UTF8-01

Decision: approve bounded implementation and regression plan.

Reviewed AGENTS.md, project-document workflow, read-only guide directory contents, SYSTEM-99 navigation/detail, both actual CLIs, configure_utf8_output, validation-context tests, make_fixture and existing four-entry CI matrix. Plan SHA256: 88846d59b6f91a3e721fe1b388d7eed98ed5895cbf7c506b6c9c492471bdf222.

The defect is concrete: both CLIs serialize with ensure_ascii=False and neither configures native output encoding. Calling the existing helper at the beginning of each main preserves JSON data, formatting, adapter selection, validation policy and exit rules while fixing stdout and handled stderr encoding. No display cap or new policy is warranted.

Approved acceptance: native byte-capturing subprocesses with PYTHONUTF8=0 and PYTHONIOENCODING=cp936, without -X utf8; strict UTF-8 decode and exact parsed-object equality against in-process results. Cover non-BMP Unicode throughout full display-only invalid/pending/usable-with-scope restores in compact and pretty modes; preserve restore exit 0 and all fixture-file hashes. Cover actual pending inspection with matching Unicode contract/manifest/validation-plan scopes and refreshed plan references, exit 2 and empty stderr. Negative missing Unicode contract path must preserve exact error object, empty stdout and exit 2. Synthetic saved usable statuses must not be presented as authenticated acceptance.

Keep existing context-write/restore roundtrip coverage. Freeze tests before production changes and retain separate original/fixed evidence. Run only the two relevant modules for each scoped round and one independent result run. Adding validation-context coverage to the existing Ubuntu/Windows × Python 3.10/3.12 matrix is appropriate; local evidence does not establish remote CI success. Keep the guide entirely read-only and all previous blocked gates/history intact. No model, performance or batch-completion claim is supported.

No blocking plan issue found. This approves scope/oracles only; implementation correctness awaits actual diff, test and evidence review.

## Exact proposed-test follow-up

Decision: revise the negative fixture before insertion; other two methods approved.

Reviewed proposed-tests.txt and actual external_json implementation without executing tests. The missing-path oracle is incorrect: regular_bytes wraps os.open failure in the fixed ASCII message `external JSON input is unavailable or not a regular file`. Consequently checking that its error contains the Unicode missing filename fails under the intended fixed implementation, and the fixture cannot exercise Unicode stderr.

Replace the Unicode error fixture with a real UTF-8 contract file containing a duplicate non-BMP key, e.g. `{"异议𐀀":1,"异议𐀀":2}`. strict_json produces the stable message `duplicate JSON key: 异议𐀀`. Require exact parsed stderr object `{'status': 'error', 'error': 'duplicate JSON key: 异议𐀀'}`, exit 2, empty stdout and unchanged file hashes. The missing-path case may additionally assert its actual fixed ASCII error object, but is insufficient as the native Unicode stderr regression. This fixture-only adjustment preserves the approved scope.

## Corrected exact-oracle approval

Decision: approve corrected plan and exact proposed tests before execution.

Verified current plan SHA256 `361f4085ad17a9bb667e741199de49934d234e310b4c12dbdd5b6a57a4880c6a` and proposed-tests SHA256 `024c1e8231ba3fd098fd5e94eb6d0e120bff78e0238222bc4265a92873f5ec4c`. The third method now writes an actual duplicate non-BMP Unicode JSON key before freezing file hashes and requires the complete exact handled error object. This matches strict_json's real duplicate-key path and exercises stderr encoding. The prior missing-path fixture flaw is resolved. No tests or production code executed by this reviewer; prior reviews remain preserved above. Independent result acceptance remains pending.

Final pre-insertion cleanup approved: proposed-tests SHA256 is now `08be5576045f92186cf1c387b5351a4dc155123a49310ae6a8ab81769e5b8b23`. Removed only the unused pre-fixture file-hash read from the third method; the authoritative post-fixture hash and all acceptance assertions remain. Plan approval unchanged.
