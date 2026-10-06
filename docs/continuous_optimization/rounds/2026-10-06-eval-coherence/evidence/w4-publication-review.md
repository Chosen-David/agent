# Independent review: T23 publication evidence helper

Review date: 2026-10-06. Reviewer: separate publication review agent, not implementation producer. Read repository AGENTS, decision-review protocol, current TASK, actual helper and tests. EXECUTE is limited to source inspection and isolated local Git fixtures. No real repository commit, push, remote access, or TASK/state changes were performed by this reviewer.

## Verdict and immutable scope

**Pass for the bounded observer helper after one substantive defect was reproduced and corrected.** This is not acceptance of the overall T21 release, T24 writing work, a deployed publication controller, or current repository publication. Initial source failed exact-tree binding despite all its 24 tests passing. Final source passes the 26 targeted tests and both independent adversarial probes below. No remaining blocker was demonstrated within the stated trusted-controller boundary.

Final SHA256 scope:

| File | SHA256 |
| --- | --- |
| `agent_runtime/publication.py` | `f523597d8059dd1b2accbb875cf1a89d7a7d0873ae247846887478590b95b6da` |
| `tests/test_publication.py` | `6e9425b9bda0b9a1b87c31b7a075e3d829c39d393374731c4a953c9d7f362ed7` |
| `agent_runtime/task_manifest.py` | `fc3d285cb87e25674b0adc28802bd9db5db74e8f5210e0a92ba338b663a7b3b1` |
| `agent_runtime/project_memory.py` | `d60a186167d6d0c9127dfd7a84041e96cffc917ba339b9aea0a0359dce8698d6` |

Git version: 2.51.1. Hashes were checked again after final tests. Review accepts these bytes, not subsequent edits or a whole uncommitted repository snapshot.

## Actual behavior inspected and tested

- Freeze requires every changed/add/delete path relative to HEAD to have exactly one mapping entry with existing stable TASK IDs. It hashes staged file bytes, Git object identities and modes; rejects untracked, unstaged, symlink, submodule and unresolved-index candidates. Mapping proves ID coverage, not that an asserted TASK owner is semantically correct; trusted acceptance still owns that judgment.
- The candidate binds root TASK contents, original parent, acceptance evidence bytes and the exact candidate identity. Missing acceptance callbacks, changed evidence/source, uncovered changed requirements and corrected memory prevent advancement. The fixture callback actually executes the candidate program and compares output; its positive result is not merely a report `pass` flag.
- State survives reopening between tested, committed, pushed and remote_verified. Failed local push is retained as pending committed work. Commit observation checks the exact tested tree and original single parent. Pushed and remote_verified each require a separate fresh remote readback, and intervening remote drift is rejected.
- The implementation itself does not stage, commit or push. Source inspection and the suite's command/index/HEAD fixture support that bounded statement. The independent probes and suite explicitly create and push disposable **local** repositories as test setup; those are not helper actions or real repository publication.

## Defect R1: local Git replacement could certify the wrong published tree

Initial implementation SHA256: `521b9be35556f1cd30aae9e7fd1653ed5319c731522a206db9c8cbb5db1f6516`.
Initial tests SHA256: `afb5eeeb334ff1179c30cabd7871d47b4e2553b3e3d07166d1fd8062a460dc84`.
Initial targeted result: **24/24 passed**, yet the independent probe failed (exit 1).

The reviewer froze and actually tested `print('candidate')`, constructed a correct replacement commit and a different original commit whose tree still printed `baseline`, installed `refs/replace/original -> replacement`, and advanced main to the original commit. Ordinary local Git `show`/`ls-tree` followed the replacement. The ledger consequently accepted the original commit OID as having the tested replacement tree. A local bare-remote push transferred the original object, not its local replacement overlay. Both remote observations matched that original OID, so the ledger reached remote_verified while the remote program was wrong.

Observed failing output, retained before the producer fix:

```json
{
  "good_commit": "519879e5ff1ee317b9a3d09d4df0711360922274",
  "bad_commit": "88fcf2b73d47c14688f205a7411a93390e8f8f2f",
  "good_tree": "6e88869ab74075db1577319f335171ca422c3008",
  "bad_tree": "e5cdb6a5f5d82add33c5ed420418e23a3d54aefd",
  "rejected": false,
  "phase": "remote_verified",
  "actual_remote_program": "print('baseline')"
}
```

This is a correctness defect in the tree/OID relation, not a forged acceptance callback or state-file tampering scenario. The approval callback required the exact fixture repository/main/remote scope, and acceptance actually executed the intended candidate bytes.

The producer corrected `_git` by setting `GIT_NO_REPLACE_OBJECTS=1` and `GIT_GRAFT_FILE=os.devnull` after sanitizing inherited Git environment. The second override also prevents legacy grafts from fabricating the required original parent. Producer regression tests cover both overlays.

On the final frozen source, the **same unmodified independent replacement probe** rejects observe_commit with `commit must have the exact tested tree and original single parent`; phase remains `tested`. The independent legacy-graft variant creates a candidate-tree root commit with no real parent and writes a graft falsely assigning the frozen base. It also rejects observe_commit and remains `tested` on final source. An exploratory graft run overlapped the producer edit, so its pre-fix result is not assigned an immutable source hash and is not counted as a separate hash-scoped baseline.

## Commands and actual final results

Run from `/workspace/scratch/c12f3d9f92bd/agent`:

```bash
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/workspace/scratch/c12f3d9f92bd/publication-review python -m unittest discover -s tests -p test_publication.py -v
PYTHONDONTWRITEBYTECODE=1 python /workspace/scratch/c12f3d9f92bd/publication-review/replace_probe.py
PYTHONDONTWRITEBYTECODE=1 python /workspace/scratch/c12f3d9f92bd/publication-review/graft_probe.py
```

| Check | Observed result |
| --- | --- |
| Final targeted unit/integration suite | 26 tests, 3.348 seconds, OK, no skips |
| Independent replacement probe | exit 0; rejected=true; phase=tested |
| Independent graft probe | exit 0; rejected=true; phase=tested |

Raw final fixture logs remain in the review scratch directory: `final-targeted.log`, `replace-fixed.json`, `graft-fixed.json`. Reproducible independent replacement code is embedded below so the defect mechanism survives scratch cleanup. The graft variant differs only by making the bad commit use the candidate tree with no parent and writing `<bad> <base>` to `.git/info/grafts` instead of creating refs/replace. Its failure-path-only remote push uses `--force` solely against the disposable local bare fixture; on corrected source execution stops at the expected rejection, before that push.

## Trust and integration limits

1. Host authorization is a trusted callback, rechecked at transitions. The helper is generic and does not hard-code `main` or this real repository. The fixture explicitly restricts both. Root must supply the equally narrow real callback and fresh authorization/revocation checks; these tests do not prove that integration exists.
2. Independent acceptance is supplied by a trusted controller. Evidence hashes cannot establish scientific validity, full-role execution, semantic TASK assignment or manuscript quality. Required whole-release gates must be included by the host acceptance policy, beyond merely the changed-task ID union.
3. The helper observes publication; it does not implement fetch/pull, reconciliation, commit, push, timers or deployed recovery. Parent/bytes changing after a refresh require a new freeze and acceptance. A pending state is usable recovery evidence, not automatic work completion.
4. Local state is not tamper-proof against its filesystem owner; callbacks, controller serialization, local Git executable and host configuration are trusted. This is not a credential sandbox or protection against arbitrary concurrently malicious filesystem writers. `status()` returns historical observations, including when later external state changes; only a fresh gated observation establishes current agreement.
5. Evidence may live outside the tree. Its bytes are rechecked, but tests do not prove external evidence retention after machine loss. Atomic local writes and process reopen were exercised; power-loss durability and remote service credentials were not.

## Independent replacement probe

Original script SHA256: `bc76969aec916351171a5677f19e5361dd60d3b59ff7af7cdc2a59fe97248f2a`. Adjust the import path when replaying in a different checkout. It creates only disposable local repositories under its own directory.

```python
import hashlib, json, os
from pathlib import Path
import subprocess, sys, tempfile
sys.path.insert(0, '/workspace/scratch/c12f3d9f92bd/agent')
from agent_runtime.publication import PublicationLedger, PublicationError, local_remote_reader

def git(path,*args,input=None):
    r=subprocess.run(['git','-C',str(path),*args],input=input,capture_output=True,text=True,check=True)
    return r.stdout.strip()

def main():
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
        area=Path(tmp); root=area/'repo'; root.mkdir(); remote=area/'bare.git'
        git(root,'init','-b','main'); git(root,'config','user.name','Independent reviewer'); git(root,'config','user.email','review@example.invalid')
        git(root,'init','--bare',str(remote)); git(root,'remote','add','origin',str(remote))
        (root/'.gitignore').write_text('.agent-runs/\n')
        (root/'TASK.md').write_text('- [ ] [T1] candidate output\n')
        (root/'app.py').write_text("print('baseline')\n")
        git(root,'add','.'); git(root,'commit','-m','baseline'); git(root,'push','origin','main')
        base=git(root,'rev-parse','HEAD')
        (root/'app.py').write_text("print('candidate')\n"); git(root,'add','app.py')
        expected_scope=dict(repository=str(root),remote='origin',remote_url=str(remote),branch='main',authorization_reference='local fixture only')
        def authorize(scope,action): return scope == expected_scope
        def accept(candidate,evidence):
            r=subprocess.run([sys.executable,str(root/'app.py')],text=True,capture_output=True)
            return r.returncode==0 and r.stdout=='candidate\n'
        state=root/'.agent-runs/publication.json'
        ledger=PublicationLedger(root,state,authorize=authorize,accept=accept,remote_reader=local_remote_reader)
        frozen=ledger.freeze({'app.py':['T1']},remote='origin',branch='main',authorization_reference='local fixture only')
        proof=area/'proof.txt'; proof.write_text('Independent actual output check\n')
        ledger.mark_tested([dict(path=str(proof),sha256=hashlib.sha256(proof.read_bytes()).hexdigest(),task_refs=['T1'],candidate_sha256=frozen['candidate']['sha256'])])
        good_tree=git(root,'write-tree')
        good=git(root,'commit-tree',good_tree,'-p',base,input='correct replacement\n')
        bad_tree=git(root,'rev-parse',base+'^{tree}')
        bad=git(root,'commit-tree',bad_tree,'-p',base,input='bad actual commit\n')
        git(root,'update-ref','refs/heads/main',bad)
        git(root,'replace',bad,good)
        result=dict(good_commit=good,bad_commit=bad,good_tree=good_tree,bad_tree=bad_tree)
        try:
            ledger.observe_commit()
        except PublicationError as exc:
            result.update(rejected=True,error=str(exc),phase=ledger.status()['phase'])
        else:
            git(root,'push','origin','main'); ledger.observe_pushed(); ledger.verify_remote()
            result.update(rejected=False,phase=ledger.status()['phase'],actual_remote_program=git(remote,'show','refs/heads/main:app.py'))
        print(json.dumps(result,indent=2))
        return 0 if result['rejected'] else 1
if __name__=='__main__': raise SystemExit(main())
```
