# CHECK-HELPER-85 independent result review

Verdict: **usable-with-scope**. Reviewer: separate host-created agent
`/root/check_helper85_verify`, 2026-10-20. This review did not implement the
production/test changes. Scope is public `MemoryLedger.check` compatibility with
custom `_read_entry` call signatures and same-connection schema changes, while
retaining built-in traversal-local schema reuse. No speed, model-quality,
universal correctness, deployment, or installed-supervisor claim is accepted.

## Inputs and implementation review

Read `AGENTS.md`, `prompts/decision_review.md`, project-document and
result-validation workflows, the frozen result plan, current task index/detail,
actual production paths, test fixtures, and raw logs. `GUIDE.md` is empty;
the entire human-only guide directory, including its existing README, was left
untouched. Only this review file is reviewer-authored. Main owns task documents
and publication. The result plan records the bounded historical search and its
partial-scan limitation; old optimization passes were not reused as proof of
this new compatibility claim.

Baseline is `73fc913a7750054d520c0e57cdf0b084b9d317d8`. The sole production
change adds `_read_entry is _BUILTIN_READ_ENTRY` to the public-check fast-path
guard. On a custom reader, fallback proceeds through `_check` → `_walk` with
`schema_state=None` → `_get` → `_read_entry(db, entry_id)`. Thus it does not
inject a third argument, and the built-in reader called by an adapter queries
current schema separately for each hydrated node. The built-in path still
passes one shared empty state list to the traversal. No error handling,
validation ordering, root selection, dependency ordering or transaction code
was changed.

Both new fixtures create an actual SQLite parent/leaf ledger. The two-argument
fixture checks leaf/parent call order, not just successful output. The DROP
fixture mutates the actual traversal connection after leaf hydration and checks
both calls receive the default `None` state. These isolate the compatibility
boundary without mocking a successful result. The schema-count instrumentation
now profiles entry into the original function instead of replacing that
function; it installs tracing before the function's SQL and restores the
previous profiler in `finally`. It therefore observes the built-in identity
guard rather than inadvertently disabling it.

## Six required checks

| Check | Verdict | Evidence and acceptance |
| --- | --- | --- |
| implementation | pass | Reviewed the actual `_read_entry`, `_get`, `_check`, `_walk`, public `check`, `_connect`, identity bindings and exact one-line diff; fallback preserves two-argument calls and exception/transaction behavior. |
| reference_boundary | pass | Independently loaded the unchanged baseline source from Git: both new tests error for the stated reasons; candidate both pass. Independent CREATE-table/malformed-parent, reader-exception, and built-in present/absent probes below pass. |
| data_integrity | pass | The two baseline errors are retained, not omitted. Targeted and optimized logs each contain 62 tests; full log contains 1323 with 8 skips; Reader contains 3. Candidate code/test bytes are pinned below. No failed/skip cases are counted as passed. |
| numerical_sanity | pass | Claims are discrete test/call/query counts, not numerical measurements: 2 baseline errors → 2 candidate passes; leaf/parent order; exactly one built-in schema query for present and absent tables. No tolerance, floating-point estimate, or derived speedup is used. |
| measurement_validity | not_applicable | The pre-test plan explicitly excludes speed and end-to-end quality claims. Durations in unittest logs are metadata, not accepted performance measurements; no timing comparison is made. |
| reproducibility | pass | Python 3.12.14. Independently reran baseline/candidate regressions and custom probes below; independently reran schema suite (9/9) and Reader suite (3/3). Reviewed producer targeted/-O/full raw results; full suite was not redundantly rerun by reviewer. |

Full-suite raw log was independently read at `/tmp/check-helper85-full.log`:
`Ran 1323 tests in 86.150s`, `OK (skipped=8)`. This temporary log is a real
artifact, not a durable repository copy; its exact hash is below. Retaining or
publishing it is main-owned. The retained `full-summary.txt` accurately copies
its final result lines; it is not represented as the complete raw log.
`environment.txt` records Linux x86_64, Python 3.12.14 and SQLite 3.53.1.
`git diff --check` passed at review time.

Independent commands:

```bash
python -m unittest discover -s tests -p 'test_memory_schema_check.py' -v
python -m unittest discover -s apps/paper-reader/tests -v
```

## Reproducible independent baseline and edge probes

Run the following from the repository root. The baseline module is compiled
directly from the named Git revision; no checkout or production edits occur.
The two regression fixtures run unchanged against each module. Temporary
databases are isolated and cleaned up.

```bash
python - <<'PY'
import importlib.util, io, json, pathlib, subprocess, sys, tempfile, types, unittest
from unittest.mock import patch
import agent_runtime.project_memory as candidate
sha = '73fc913a7750054d520c0e57cdf0b084b9d317d8'
source = subprocess.check_output(['git', 'show', sha + ':agent_runtime/project_memory.py'], text=True)
baseline = types.ModuleType('agent_runtime._review_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(source, '<baseline-project-memory>', 'exec'), baseline.__dict__)
spec = importlib.util.spec_from_file_location('review_reader_tests', 'tests/test_memory_check_reader.py')
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
for name, module in [('baseline', baseline), ('candidate', candidate)]:
    tests.memory = module
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    print(name, output.getvalue())
    if name == 'baseline':
        assert result.testsRun == 2 and len(result.errors) == 2 and not result.failures
        assert any('takes 2 positional arguments but 3 were given' in err for _, err in result.errors)
        assert any('no such table: document_dependencies' in err for _, err in result.errors)
    else:
        assert result.testsRun == 2 and result.wasSuccessful()

def ledger(module, root):
    obj = module.MemoryLedger(root, create=True)
    obj.add('parent', 'claim', 'parent', 'synthetic', evidence='verified')
    obj.add('leaf', 'claim', 'leaf', 'synthetic', deps=['parent'], evidence='verified')
    return obj

for name, module in [('baseline', baseline), ('candidate', candidate)]:
    with tempfile.TemporaryDirectory() as tmp:
        obj = ledger(module, pathlib.Path(tmp))
        with obj._connect(write=True) as db:
            db.execute('DROP TABLE document_dependencies')
        original = module._read_entry
        states = []
        def create_bad_parent(db, ref, state=None):
            states.append(None if state is None else list(state))
            entry = original(db, ref, state)
            if ref == 'leaf':
                db.execute('CREATE TABLE document_dependencies(entry_id TEXT PRIMARY KEY,snapshot TEXT NOT NULL)')
                db.execute("INSERT INTO document_dependencies VALUES ('parent', 'broken')")
            return entry
        with patch.object(module, '_read_entry', create_bad_parent):
            try:
                obj.check(['leaf'])
                outcome = 'accepted'
            except json.JSONDecodeError:
                outcome = 'JSONDecodeError'
        print(name, 'CREATE malformed-parent edge:', outcome, 'states:', states)
        assert outcome == ('accepted' if name == 'baseline' else 'JSONDecodeError')
        if name == 'candidate':
            assert states == [None, None]
            assert obj.check(['leaf'])[0]['id'] == 'leaf'
            with obj._connect() as db:
                assert db.execute("SELECT 1 FROM sqlite_master WHERE name='document_dependencies'").fetchone() is None

with tempfile.TemporaryDirectory() as tmp:
    obj = ledger(candidate, pathlib.Path(tmp))
    original = candidate._read_entry
    failure = RuntimeError('reviewer reader sentinel')
    calls = []
    def throwing_reader(db, ref):
        calls.append(ref)
        if ref == 'parent':
            raise failure
        return original(db, ref)
    with patch.object(candidate, '_read_entry', throwing_reader):
        try:
            obj.check(['leaf'])
        except RuntimeError as error:
            assert error is failure
        else:
            raise AssertionError('reader error swallowed')
    assert calls == ['leaf', 'parent']
    assert obj.check(['leaf'])[0]['id'] == 'leaf'
    print('candidate reader-exception: original exception preserved; next builtin call succeeds')
    for present in [True, False]:
        if not present:
            with obj._connect(write=True) as db:
                db.execute('DROP TABLE document_dependencies')
        trace, states = [], []
        previous = sys.getprofile()
        def profile(frame, event, arg):
            if event == 'call' and frame.f_code is original.__code__:
                frame.f_locals['db'].set_trace_callback(trace.append)
                states.append(frame.f_locals['schema_state'])
        try:
            sys.setprofile(profile)
            obj.check(['leaf'])
        finally:
            sys.setprofile(previous)
        queries = [q for q in trace if 'FROM sqlite_master' in q]
        assert len(queries) == 1 and len(states) == 2 and states[0] is states[1]
        assert states[0] == [present]
        print('candidate builtin reuse:', present, 'one schema query, shared traversal state', states[0])
print('INDEPENDENT CHECKS PASSED')
PY
```

Observed independent output (tracebacks omitted here; baseline exception names
and messages were explicitly asserted by the probe):

```text
baseline: Ran 2 tests; FAILED (errors=2)
  TypeError: ...read() takes 2 positional arguments but 3 were given
  MemoryError: project memory ledger unavailable: no such table: document_dependencies
candidate: Ran 2 tests; OK
baseline CREATE malformed-parent edge: accepted states: [[], [False]]
candidate CREATE malformed-parent edge: JSONDecodeError states: [None, None]
candidate reader-exception: original exception preserved; next builtin call succeeds
candidate builtin reuse: True one schema query, shared traversal state [True]
candidate builtin reuse: False one schema query, shared traversal state [False]
INDEPENDENT CHECKS PASSED
```

The CREATE probe is deliberately the reverse schema transition of the new DROP
regression: initial absence must not suppress validation of a malformed parent
binding created by a reader before parent hydration. Candidate rejection also
rolls back that DDL, checked via a fresh connection. This distinguishes fresh
schema observation from merely avoiding the DROP error.

## Frozen evidence hashes (SHA-256)

| Artifact | SHA-256 |
| --- | --- |
| `agent_runtime/project_memory.py` | `6ea74a0ca0cb8f5b7c9be99fa1c9c7a0c7826e5c9242c0edd015d1be2db827cd` |
| `tests/test_memory_check_reader.py` | `e056a6ec6baeb2d0a9eb1a7e4e89f7ed4a4c69ce60c0580e3af078c5fa2bcfda` |
| `tests/test_memory_schema_check.py` | `43ee0bb73d50f652cc3e08b9b16d475851db9b61725f62567bbfa0b5257cf520` |
| `agent_doc/results/check-helper85/plan.md` | `03633e034d4032a2340997cdbaf1310395e5afc561e9068efdbc1496a07fb0dc` |
| `agent_doc/results/check-helper85/before.txt` | `7d126ff45a54837e28e6ce07bbc09a10844aed9306f28f711514b0e867478a99` |
| `agent_doc/results/check-helper85/targeted.txt` | `3158760fe7689fd59ea7fff963235e9000a77d17772064c6a9f827e0c262164c` |
| `agent_doc/results/check-helper85/optimized.txt` | `904fee32e4b5582bcddb6d8c2f5856a38d43ceb89fd0339fe2d011704e909e02` |
| `/tmp/check-helper85-full.log` | `696c1c5807b1bd9a89b0d36900d2dd643eceb523dd85f0b27d0a693955f99abd` |
| `agent_doc/results/check-helper85/reader.txt` | `42cd32abcf4f7073b2b92a3bc6b68a4d49b1966a2aade2c42e55f3a0e46917e1` |
| `agent_doc/results/check-helper85/full-summary.txt` | `5dcfe8b04da1e37dd9e17559deaf935ac7721cf7059a6c3da9e1bf7007181565` |
| `agent_doc/results/check-helper85/environment.txt` | `2700d0150431cff8f57c094385c34c862c5cd3b7a13f9f944aab932a4fd6c711` |

Limitations: finite local fixtures, Python 3.12.14/available SQLite, eight
full-suite skips, no concurrent monkeypatch race model, and no external
runtime/model/service validation. External research-note claims are outside
this code-result acceptance. No formal runtime verifier/provider or supervisor
installation is claimed by this Markdown review. Publication, remote fetch/
merge/push/readback and final task-index closure remain main-owned gates.
