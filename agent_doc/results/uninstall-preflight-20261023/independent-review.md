# Independent uninstall manifest review

Reviewer /root/python39_ingest_review. Base 0b2453a67b6b22a537bdd3dcefd2c457a33a57f3. Bounded local compatibility and destructive-action preflight review; no performance/whole-system assertion.

## Independent minimal probe

```python
import importlib.util,json,subprocess,tempfile,types
from pathlib import Path
import setup

def snapshot(root):
    return {p.relative_to(root).as_posix(): ('link',str(p.readlink())) if p.is_symlink() else ('file',p.read_bytes())
            for p in root.rglob('*') if p.is_symlink() or p.is_file()}
def fixture(root,copy=False):
    setup.install(root,model_inventory=setup.EMPTY_INVENTORY,copy_skills=copy)
    path=root/'.claude/agent-workflows/installation.json'
    return path,json.loads(path.read_text())
old=types.ModuleType('old_setup');old.__file__=str(setup.REPO/'setup.py')
exec(compile(subprocess.check_output(['git','show','0b2453a67b6b22a537bdd3dcefd2c457a33a57f3:setup.py']),old.__file__,'exec'),old.__dict__)
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);path,m=fixture(root);m['links']=[];path.write_text(json.dumps(m));before=snapshot(root)
    try:old.uninstall(root)
    except Exception as e:print('baseline',type(e).__name__,'removed',len(before.keys()-snapshot(root).keys()))
    else:raise AssertionError('baseline did not fail')
mutations=[lambda m:None,lambda m:True,lambda m:{},lambda m:{**m,'files':{'x':7}},
           lambda m:{**m,'links':{k:{} for k in m['links']}},lambda m:{**m,'skill_copies':[]}]
for i,mutation in enumerate(mutations):
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);path,m=fixture(root);path.write_text(json.dumps(mutation(m)));before=snapshot(root)
        try:setup.uninstall(root)
        except ValueError as e:assert 'invalid installation manifest' in str(e)
        else:raise AssertionError('invalid shape accepted')
        assert snapshot(root)==before
print('candidate malformed extra cases',len(mutations),'preserved exact file/link snapshots')
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);path,m=fixture(root);m.pop('skill_copies');path.write_text(json.dumps(m))
    assert setup.uninstall(root)['status']=='uninstalled'
    assert not path.exists()
print('legacy no skill_copies accepted')
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);path,m=fixture(root,True)
    agent=root/'.claude/agents/agent-research-assistant.md';agent.write_text('keep edited agent')
    skill=root/'.claude/skills/model-with-knowledge/SKILL.md';skill.write_text('keep edited skill')
    result=setup.uninstall(root)
    assert agent.read_text()=='keep edited agent' and skill.read_text()=='keep edited skill'
    assert '.claude/agents/agent-research-assistant.md' in result['preserved_local_edits']
    assert '.claude/skills/model-with-knowledge' in result['preserved_local_edits']
    assert not path.exists()
print('copied install local edits preserved; ordinary owned files removed')
```

Command: `/root/.local/bin/python3.9 -` using the exact probe above. Exit 0.
```text
baseline AttributeError removed 22
candidate malformed extra cases 6 preserved exact file/link snapshots
legacy no skill_copies accepted
copied install local edits preserved; ordinary owned files removed
```

Command: `python -` using the exact probe above. Exit 0.
```text
baseline AttributeError removed 22
candidate malformed extra cases 6 preserved exact file/link snapshots
legacy no skill_copies accepted
copied install local edits preserved; ordinary owned files removed
```

## Adjacent regressions

Actual commands:
```text
/root/.local/bin/python3.9 -m unittest tests.test_uninstall_manifest tests.test_setup tests.test_setup_portable tests.test_install_recovery
Ran 39 tests in 2.440s
OK
python -m unittest tests.test_uninstall_manifest tests.test_setup tests.test_setup_portable tests.test_install_recovery
Ran 39 tests in 2.646s
OK
```
Both exit 0. These cover CLI invalid manifest diagnostics without traceback/deletions, malformed CLAUDE block preflight, edited agent/block preservation, copy update/uninstall, symlink ownership, existing setup/recovery behavior and UTF-8 CLI paths.

## Code review and conclusion

Verdict: usable-with-scope, no blocking defect found in the reviewed patch. Dictionary validation is performed before expected-file resolution or either deletion loop. It rejects malformed top-level/files/links/skill_copies shapes and every non-string files/links value, closing the late links `.items()` or `Path(source)` type failures. JSON keys are always strings. Remaining malformed nested copy fingerprints cannot trigger a new removal-loop type exception: they are only compared to an actual snapshot, causing edited/unrecognized copies to be preserved. Omitted skill_copies remains the historical symlink-compatible default. Ownership checks, allowed path preflight, guide protections, file hashes and edited-copy preservation were not relaxed.

Independent old-code probe confirmed the original defect on both interpreters: invalid links list raised AttributeError after 22 files were removed. Candidate probes rejected extra malformed cases before any file/link snapshot changed. Legacy omitted-copy metadata and copied installs with local edits retained prior behavior.

This is an invalid-manifest preflight fix, not transactional uninstall or malformed-manifest auto-repair. Concurrent filesystem mutation, disk permission/I/O failures mid-uninstall, process crash/power loss, actual Windows, every catalog/runtime API on Python3.9, external host/model/tmux and performance remain unverified. A syntactically valid tampered ownership record is not authenticated by these type checks.

Reviewed file hashes:
- setup.py: e098651000a79ea8f0d1d356f4c78eaf2f61134f828247b26ef09828a61afc2d
- tests/test_uninstall_manifest.py: 418e13152492e40e59f967c2984b03b9f792728e1163f73f2086d868efe1c81b
