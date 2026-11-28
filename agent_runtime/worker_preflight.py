"""No-inference probes for the Linux native CLI developer worker."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

from .codex_host import AppServer

MODE = 'workspace-write'
CONFIG = ['-c', 'sandbox_workspace_write.network_access=false',
          '-c', 'sandbox_workspace_write.exclude_slash_tmp=true',
          '-c', 'sandbox_workspace_write.exclude_tmpdir_env_var=true',
          '-c', 'sandbox_workspace_write.writable_roots=[]']
CAPABILITIES = {'file_read', 'file_write', 'shell_exec', 'git_worktree', 'test_exec'}


def execution_mode(project, tree, binary):
    """Only the operator's private host file may opt an exact checkout into full access."""
    path = Path.home() / '.codex/chosen-agent/trusted-research.json'
    if not path.exists():
        return MODE
    with path.open() as source:
        stat = os.fstat(source.fileno())
        if stat.st_uid != os.getuid() or stat.st_mode & 0o077 or path.is_symlink():
            raise PermissionError('private operator-owned research profile required')
        settings = json.load(source)
    if (settings['host'] == platform.node() and settings['binary'] == str(Path(binary).resolve())
            and str(tree) in settings['projects'].get(project, [])):
        return 'danger-full-access'
    return MODE


def _identity(binary, tree, output, requirements, mode):
    version = subprocess.run([binary, '--version'], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    status = Path('/proc/self/status').read_text().splitlines()
    config_home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
    files = [config_home / 'config.toml', Path('/etc/codex/requirements.toml'),
             *(p / '.codex/config.toml' for p in (tree, *tree.parents))]
    configs = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
    info = dict(backend='codex-command-exec', version=version, binary=binary,
                executable_stat=list(os.stat(binary))[0:3] + [os.stat(binary).st_mtime_ns],
                host=platform.node(), boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                uid=os.geteuid(), groups=os.getgroups(), envelope=[x for x in status if
                    x.startswith(('CapEff:', 'Seccomp:', 'NoNewPrivs:'))],
                namespaces=[os.readlink('/proc/self/ns/' + ns) for ns in ('mnt', 'user', 'net')],
                tree=str(tree), output=str(output), capabilities=sorted(requirements),
                config=CONFIG if mode == MODE else [], config_hashes=configs, mode=mode)
    return json.dumps(info, sort_keys=True)


def check(store, codex, tree, output, requirements, *, refresh=False, project=None):
    if requirements != CAPABILITIES:
        raise ValueError('developer backend requires authorized worktree writes; unsupported capability profile')
    binary = shutil.which(str(codex))
    if binary is None:
        raise ValueError('Codex executable unavailable')
    if not output.is_relative_to(tree):
        raise ValueError('output outside authorized worktree')
    mode = execution_mode(project, tree, binary)
    binding = _identity(os.path.realpath(binary), tree, output, requirements, mode)
    with store.transaction() as db:
        db.execute('CREATE TABLE IF NOT EXISTS worker_capabilities(binding TEXT PRIMARY KEY, checked REAL, error TEXT)')
        prior = db.execute('SELECT checked,error FROM worker_capabilities WHERE binding=?', (binding,)).fetchone()
        if prior and prior['error'] and not refresh and 0 <= time.time()-prior['checked'] < 300:
            raise RuntimeError('worker sandbox circuit open: ' + prior['error'])
    policy = dict(type='workspaceWrite', writableRoots=[], networkAccess=False,
                  excludeTmpdirEnvVar=True, excludeSlashTmp=True)
    config = CONFIG
    if mode == 'danger-full-access':
        policy = {'type': 'dangerFullAccess'}
        config = []
    server = AppServer([binary, *config, '-s', mode, '-a', 'never'], tree, 25)
    try:
        args = dict(cwd=str(tree), sandboxPolicy=policy)
        result = server.call('command/exec', dict(args, command=['/bin/pwd']))
        if result['exitCode'] == 0 and result['stdout'].strip() == str(tree):
            result = server.call('command/exec', dict(args, command=['/bin/sh', '-ec',
                'git rev-parse --is-inside-work-tree | grep -qx true; '
                'f=$(mktemp .worker-probe.XXXXXXXX); trap \'rm -f -- "$f"\' EXIT; '
                'printf probe > "$f"; test "$(cat "$f")" = probe; rm -- "$f"']))
        elif result['exitCode'] == 0:
            raise RuntimeError('sandbox returned unexpected working directory')
    finally:
        server.close()
    error = result['stderr'].strip()[:1000] if result['exitCode'] else ''
    if result['exitCode'] and not error:
        error = 'sandbox capability probe exited ' + str(result['exitCode'])
    if error and 'bwrap: Failed to make / slave: Permission denied' not in error:
        raise RuntimeError('worker capability unavailable: ' + error)
    with store.transaction() as db:
        db.execute('INSERT OR REPLACE INTO worker_capabilities VALUES(?,?,?)',
                   (binding, time.time(), error))
    if error:
        raise RuntimeError('worker sandbox preflight failed: ' + error)

    return mode
