#!/usr/bin/env python3
"""Use an existing Windows Codex login from a WSL-owned bounded runner.

Paths arrive as native Windows paths. Credentials are never copied into WSL.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request


def sync_host_skills(repo, run, environment, *, before=False):
    """Synchronize a verified snapshot between model runs, preserving local edits."""
    result = subprocess.run([sys.executable, str(Path(repo)/'scripts/setup_codex.py')],
                            cwd=repo, env=environment, capture_output=True,
                            text=True, encoding='utf-8', timeout=120)
    receipt = {'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
               'phase': 'before' if before else 'after',
               'scope': ('Verified fetched main before model launch' if before else
                         'Explicit host skill synchronization after complete published-tree verification')}
    if result.returncode == 0:
        checked = subprocess.run([sys.executable, str(Path(repo)/'scripts/setup_codex.py'), '--check'],
                                 cwd=repo, env=environment, capture_output=True,
                                 text=True, encoding='utf-8', timeout=120)
        receipt['check'] = {'exit_code': checked.returncode,
                            'stdout': checked.stdout, 'stderr': checked.stderr}
    name = 'host-skills-before.json' if before else 'host-skills.json'
    (Path(run)/name).write_text(json.dumps(receipt), encoding='utf-8')
    failure = receipt if result.returncode else receipt['check']
    if failure['exit_code']:
        prefix = 'No model launched; ' if before else 'Published changes retained; '
        raise RuntimeError(prefix+'local skill synchronization blocked: '+
                           (failure['stdout']+failure['stderr'])[-1500:])
    return receipt


def git_sync(repo, run, environment, *, before):
    """Trusted host owns Git; the model's sandbox keeps .git read-only.

    After connector publication, update the index/branch only when every working
    file exactly matches the fetched public tree. Never discard a working file.
    """
    def git(*args, env=None):
        result=subprocess.run(['git',*args],cwd=repo,env=env or environment,
                              capture_output=True,text=True,encoding='utf-8',timeout=60)
        if result.returncode:
            raise RuntimeError('Git synchronization failed: '+result.stderr[-1500:])
        return result.stdout.strip()
    if before and git('status','--porcelain'):
        raise RuntimeError('Working tree is dirty; no model launched')
    git('fetch','origin','main')
    if before:
        git('merge','--ff-only','origin/main')
        head = git('rev-parse','HEAD')
        if head != git('rev-parse','origin/main') or git('status','--porcelain'):
            raise RuntimeError('Preflight is not clean fetched main; no model launched')
        return {'phase':'before','head':head,'tree':git('rev-parse','HEAD^{tree}')}
    # Only knowledge maintenance output is eligible for local reconciliation.
    changed=git('diff','HEAD','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines()
    prefixes=('knowledge/','evals/knowledge/','docs/knowledge_learning/',
              'doc/task/','doc/results/',
              'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/')
    if any(p not in ('TASK.md','README.md','CODEMAP.md') and not p.startswith(prefixes) for p in changed):
        raise RuntimeError('Changes outside knowledge maintenance scope; preserve for review')
    index=Path(run)/'reconcile.index'
    if index.exists(): raise RuntimeError('Existing reconciliation index; inspect before recovery')
    temporary=dict(environment,GIT_INDEX_FILE=str(index))
    git('read-tree','HEAD',env=temporary)
    git('add','-A','--','.',env=temporary)
    working=git('write-tree',env=temporary)
    remote=git('rev-parse','origin/main^{tree}')
    if working!=remote:
        raise RuntimeError('Working tree differs from published main; preserve all files for recovery')
    # --mixed updates Git metadata only, after exact equality; never --hard.
    git('reset','--mixed','origin/main')
    index.unlink()
    return {'phase':'after','head':git('rev-parse','HEAD'),'tree':remote,'working_files_preserved':True}


def prepare_host(repo, run, environment, *, skills=False):
    """Pull and verify main, then update skills before launching a new model."""
    preflight = git_sync(repo, run, environment, before=True)
    (Path(run)/'host-before.json').write_text(json.dumps(preflight), encoding='utf-8')
    if skills:
        sync_host_skills(repo, run, environment, before=True)
    return preflight


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--codex',required=True,help='explicit trusted native codex.exe')
    p.add_argument('--model',help='Optional account-supported model for this runner only')
    p.add_argument('--host-git-sync',action='store_true',help='Trusted host sync before/after connector publication')
    p.add_argument('--host-skill-sync',action='store_true',help='Sync skills after verified pull before launch and after verified publication')
    p.add_argument('--repo',required=True)
    p.add_argument('--prompt',required=True)
    p.add_argument('--run-dir',required=True)
    p.add_argument('--timeout',type=int,default=2700)
    a=p.parse_args()
    if a.host_skill_sync and not a.host_git_sync:
        p.error('--host-skill-sync requires --host-git-sync')
    if os.name!='nt': raise RuntimeError('Windows runner must execute on Windows')
    if not 30 <= a.timeout <= 2700: raise ValueError('timeout must be 30..2700 seconds')
    exe=Path(a.codex).resolve(); repo=Path(a.repo).resolve(); run=Path(a.run_dir).resolve()
    if not exe.is_file() or exe.name!='codex.exe': raise ValueError('native executable missing')
    run.mkdir(parents=True,exist_ok=True)
    # Connector writes require actual approval review. Enable only that review
    # category for this process; sandbox escalation stays disallowed.
    approvals='{ granular={ sandbox_approval=false, rules=false, mcp_elicitations=true, request_permissions=false, skill_approval=false } }'
    args=[str(exe),'exec','--sandbox','workspace-write','-c','approval_policy='+approvals,
          '-c','approvals_reviewer="auto_review"',
          '-c','sandbox_workspace_write.network_access=true',
          '-c','web_search="live"','-C',str(repo),'--json','-o',str(run/'final.md'),'-']
    if a.model:
        args[2:2]=['--model',a.model]
    prompt=Path(a.prompt).read_text(encoding='utf-8')
    environment=dict(os.environ, PYTHONUTF8='1', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    # Git does not automatically use the Windows proxy setting that the native
    # model client already uses. Respect existing process overrides first.
    for scheme,proxy in urllib.request.getproxies().items():
        if scheme in ('http','https'):
            environment.setdefault(scheme.upper()+'_PROXY',proxy)
    if a.host_git_sync:
        prepare_host(repo,run,environment,skills=a.host_skill_sync)
        prompt=('宿主已先执行 Git fetch/fast-forward 并确认干净。模型 sandbox 的 .git 只读；不要尝试修改 Git 权限或写 .git。'
                '使用已连接 GitHub 工具按 expected_sha 非强制发布，发布前再次读回 main 并整合并发。'
                '无需本地 git commit；宿主在模型结束后仅当本地全部文件与远端内容树一致时更新本地 Git 索引/分支，保留工作文件。\n\n'+prompt)
    with (run/'events.jsonl').open('w',encoding='utf-8') as log:
        child=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,env=environment)
        (run/'process.json').write_text(json.dumps({'pid':child.pid,'started_at':time.time(),
             'timeout_seconds':a.timeout,'scope':'knowledge maintenance in explicit repository'}),encoding='utf-8')
        try:
            child.communicate(prompt.encode('utf-8'),timeout=a.timeout)
        except subprocess.TimeoutExpired:
            # PID came from this exact Popen; never terminate unrelated agents.
            subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],capture_output=True)
            child.wait(timeout=30)
            (run/'timeout.json').write_text(json.dumps({'timed_out':True,'pid':child.pid}),encoding='utf-8')
            return 124
    if child.returncode==0 and a.host_git_sync:
        result=git_sync(repo,run,environment,before=False)
        (run/'host-after.json').write_text(json.dumps(result),encoding='utf-8')
        if a.host_skill_sync:
            sync_host_skills(repo,run,environment)
    return child.returncode


if __name__=='__main__': raise SystemExit(main())
