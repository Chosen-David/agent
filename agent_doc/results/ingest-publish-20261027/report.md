# Knowledge import publication repair

SYSTEM-99 / INGEST-PUBLISH-01, Plan51. This is a scoped reliability checkpoint; the system-level batch remains unfinished.

The last live corpus comparison now runs after all private copying. Complete entry directories publish without replacing an existing target: Linux renameat2/NOREPLACE, macOS renamex_np/EXCL, Windows native rename. Missing capability fails closed; syscall errors propagate without an unsafe replacement fallback. Candidate status, provenance, reference identity, declared dependency validation and complete-pair visibility remain covered.

| Frozen phase | New9 methods | Existing26 methods | Sync |
| --- | --- | --- | --- |
| baseline | 4 failures,3 explicit baseline-only ABI skips,2 passed | passed | passed |
| fixed | 9 passed, no skips | passed | passed |
| independent | 9 passed, no skips | passed | passed |

The original late body/dependency changes, empty-target replacement and after-final-guard target claim failures are retained. Same frozen tests now refuse the late changes, preserve claimed targets and clean private staging. Native collision tests include empty/nonempty directories, files and dangling links; normal imports verify the full three-file entry and receipt. ABI/error tests are mocks; they do not prove native Windows/macOS behavior. Existing suites also exercise real isolated copied-Skill CLI execution and index integration. Baseline/fixed/independent each ran once under the frozen limits. Elapsed times are execution metadata, not benchmarks.

Only the authoritative ingest source changed. The existing Skill entry is a tracked symlink to it, unchanged; no legacy production implementation was retained. Two source-plan reviews and an independent actual code/raw-data review accepted the finite Linux scope. V2 only sets the new macOS CI job's temporary directory to runner.temp so fixtures need not traverse a system temporary alias; no local checks were repeated. Five native jobs are pending at this publication: Linux/Windows3.10/3.12 plus targeted macOS3.12. No platform is accepted from workflow configuration alone.

Primary API references checked2026-10-27: [Linux renameat2](https://man7.org/linux/man-pages/man2/rename.2.html), [Apple xnu-12377.1.9 header](https://github.com/apple-oss-distributions/xnu/blob/xnu-12377.1.9/bsd/sys/stdio.h), [Python rename](https://docs.python.org/3/library/os.html#os.rename). No new paper-body credit is claimed;20 same-batch reading records remain.

This moves a best-effort live check and prevents destination replacement; it is not a corpus transaction. Edits during the final read or after comparison, hostile parent substitution, cleanup identity, crash durability and complete concurrency remain open. A corpus mount point can still yield EXDEV from sibling staging; errors propagate. Unsupported platforms/filesystems fail explicitly. No performance, model quality, token, billing, installed-host loading or whole-round acceptance claim follows. The actual delegated reviews are not authenticated repository runtime verifier receipts; historical catalog registration remains unknown. Original diagnosis and old exhausted gates are preserved. Future work continues these unresolved system boundaries within SYSTEM-99.
