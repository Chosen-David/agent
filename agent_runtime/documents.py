"""Explicit, versioned document tools. No installation on import or ordinary setup."""
from contextlib import contextmanager
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import sysconfig
import tempfile
import time
import venv

try:
    import fcntl
except ImportError:
    fcntl = None

from .external_json import regular_bytes, strict_json


REPO = Path(__file__).resolve().parents[1]
LOCK = REPO / 'config/documents-linux-cp312-v1.json'
ADAPTER = Path(__file__).with_name('documents_adapter.py')
MARKER = 'agent-documents-root/v1'
OUTPUT_LIMIT = 8 * 1024 * 1024


class DocumentsUnavailable(RuntimeError):
    """The environment or backend is unavailable, rather than malformed input."""


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError('symlink path is unsupported')
    return path


def atomic_json(path, value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    fd, temp = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def read_json(path):
    return strict_json(regular_bytes(path, max_bytes=1024 * 1024))


@contextmanager
def managed_root(root, *, create=False):
    if fcntl is None or not hasattr(os, 'O_NOFOLLOW'):
        raise DocumentsUnavailable('unsupported: documents v1 requires POSIX file locks and O_NOFOLLOW')
    root = safe_path(root)
    if not root.exists():
        if not create:
            raise DocumentsUnavailable('documents root is not installed')
        root.mkdir(parents=True)
        atomic_json(root / 'owner.json', dict(schema_version=MARKER))
    if not root.is_dir() or read_json(root / 'owner.json') != dict(schema_version=MARKER):
        raise ValueError('root is not owned by the documents tool')
    fd = os.open(root / 'install.lock', os.O_CREAT | os.O_RDWR | os.O_NONBLOCK | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('install lock must be a regular file')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield root
    finally:
        os.close(fd)


def platform_identity():
    libc, libc_version = platform.libc_ver()
    if (sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12)
            or platform.system() != 'Linux' or platform.machine() != 'x86_64'
            or libc != 'glibc' or tuple(map(int, libc_version.split('.')[:2])) < (2, 28)):
        raise DocumentsUnavailable('unsupported: documents v1 requires CPython3.12 Linux x86_64 glibc>=2.28')
    return dict(python_version=platform.python_version(), system=platform.system(),
                machine=platform.machine(), libc=[libc, libc_version],
                executable=os.path.realpath(sys.executable), soabi=sysconfig.get_config_var('SOABI'))


def load_profile():
    raw = regular_bytes(LOCK, max_bytes=1024 * 1024)
    profile = strict_json(raw)
    if profile.get('schema_version') != 'documents-profile/v1' or len(profile['packages']) != 10:
        raise ValueError('invalid documents lock')
    # pip is only needed for the explicit installer; its bundled tag parser is
    # consulted here without installing packaging in the host environment.
    from pip._vendor.packaging.tags import sys_tags, parse_tag
    from pip._vendor.packaging.requirements import Requirement
    from pip._vendor.packaging.utils import canonicalize_name
    compatible = set(sys_tags())
    for item in profile['packages']:
        if not any(parse_tag(tag) & compatible for tag in item['tags']):
            raise ValueError('incompatible wheel: ' + item['filename'])
    locked = {canonicalize_name(item['name']): item['version'] for item in profile['packages']}
    if len(locked) != 10:
        raise ValueError('duplicate locked package')
    for item in profile['packages']:
        for text in item['requires_dist']:
            requirement = Requirement(text)
            if requirement.marker is not None and not requirement.marker.evaluate({'extra': ''}):
                continue
            version = locked.get(canonicalize_name(requirement.name))
            if version is None or version not in requirement.specifier:
                raise ValueError('incomplete dependency closure: ' + text)
    return profile, digest(raw)


def run_adapter(python, operation, payload, output_dir):
    output_dir = safe_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='documents-call-') as temp:
        temp = Path(temp)
        request = temp / 'input.json'
        request.write_text(json.dumps(payload), encoding='utf-8')
        stdout, stderr = temp / 'stdout', temp / 'stderr'
        with stdout.open('wb') as out, stderr.open('wb') as err:
            process = subprocess.Popen([str(python), '-I', str(ADAPTER), operation,
                                        str(request), str(output_dir)], stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=err, start_new_session=True,
                                       env={k: v for k, v in os.environ.items()
                                            if not k.startswith(('PYTHON', 'PIP_'))})
            deadline = time.monotonic() + 60
            try:
                while process.poll() is None:
                    if stdout.stat().st_size > OUTPUT_LIMIT or stderr.stat().st_size > OUTPUT_LIMIT:
                        raise ValueError('adapter output exceeds 8 MiB')
                    if time.monotonic() >= deadline:
                        raise DocumentsUnavailable('adapter timeout after 60 seconds')
                    time.sleep(0.02)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
        if stdout.stat().st_size > OUTPUT_LIMIT or stderr.stat().st_size > OUTPUT_LIMIT:
            raise ValueError('adapter output exceeds 8 MiB')
        if process.returncode != 0:
            if process.returncode == 3:
                failure = strict_json(regular_bytes(stdout, max_bytes=OUTPUT_LIMIT))
                raise ValueError(failure.get('error', 'invalid document input'))
            raise DocumentsUnavailable('adapter failed: ' + stderr.read_text(errors='replace')[:2000] +
                             stdout.read_text(errors='replace')[:2000])
        result = strict_json(regular_bytes(stdout, max_bytes=OUTPUT_LIMIT))
        if result.get('schema_version') != 'documents-result/v1' or result.get('status') != 'ok':
            raise ValueError('adapter did not return a successful result')
        return result


def smoke(python):
    with tempfile.TemporaryDirectory(prefix='documents-smoke-') as temp:
        try:
            return run_adapter(python, 'probe', {}, temp)['result']
        except ValueError as exc:
            raise DocumentsUnavailable('capability smoke failed: ' + str(exc)) from exc


def binding(license_choice):
    if license_choice not in ('agpl-3.0', 'commercial'):
        raise ValueError('explicit --pymupdf-license agpl-3.0|commercial is required; see https://pymupdf.io/licensing')
    identity = platform_identity()
    profile, lock_sha = load_profile()
    value = dict(schema_version='documents-binding/v1', profile=profile['profile'],
                 lock_sha256=lock_sha, adapter_sha256=digest(ADAPTER.read_bytes()),
                 interpreter=identity, pymupdf_license=license_choice)
    return profile, value, digest(json.dumps(value, sort_keys=True).encode())


def verify(root, version, expected):
    if type(version) is not str or len(version) != 64 or any(c not in '0123456789abcdef' for c in version):
        raise ValueError('invalid environment id')
    directory = safe_path(root / version)
    if (directory / '.incomplete').exists():
        raise ValueError('incomplete environment requires manual recovery; not reused')
    receipt = read_json(directory / 'receipt.json')
    if receipt.get('binding') != expected or receipt.get('venv') != str(directory):
        raise ValueError('receipt does not match current tool/lock/interpreter/license')
    observation = smoke(directory / 'bin/python')
    profile, _ = load_profile()
    if observation['packages'] != {p['name']: p['version'] for p in profile['packages']}:
        raise ValueError('installed packages do not match lock')
    if receipt.get('observation') != observation:
        raise ValueError('capability observation changed')
    return receipt


def install(root, license_choice, *, wheelhouse=None, offline=False):
    profile, expected, version = binding(license_choice)
    with managed_root(root, create=True) as root:
        directory = safe_path(root / version)
        if directory.exists():
            receipt = verify(root, version, expected)
            atomic_json(root / 'current.json', dict(schema_version='documents-current/v1',
                        version=version, receipt_sha256=digest((directory / 'receipt.json').read_bytes())))
            return dict(status='reused', receipt=receipt)
        if offline and wheelhouse is None:
            raise ValueError('offline first install requires --wheelhouse')
        directory.mkdir()
        atomic_json(directory / '.incomplete', dict(schema_version='documents-install/v1', binding=expected))
        # Keep a failed incomplete directory for diagnosis; never delete unknown
        # environments or rewrite the previous current/receipt on failure.
        venv.EnvBuilder(with_pip=True).create(directory)
        requirements = directory / 'requirements.lock'
        lines = []
        for item in profile['packages']:
            location = item['url']
            if wheelhouse is not None:
                wheel = safe_path(Path(wheelhouse) / item['filename'])
                if digest(regular_bytes(wheel, max_bytes=64 * 1024 * 1024)) != item['sha256']:
                    raise ValueError('wheelhouse hash mismatch: ' + item['filename'])
                location = wheel.as_uri()
            lines.append(f"{item['name']} @ {location} --hash=sha256:{item['sha256']}")
        requirements.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        command = [str(directory / 'bin/python'), '-I', '-m', 'pip', '--isolated',
                   '--disable-pip-version-check', 'install', '--require-hashes',
                   '--only-binary=:all:', '--no-deps', '--no-index', '-r', str(requirements)]
        subprocess.run(command, check=True, timeout=300, stdout=subprocess.DEVNULL)
        observation = smoke(directory / 'bin/python')
        if observation['packages'] != {p['name']: p['version'] for p in profile['packages']}:
            raise ValueError('installed packages do not match lock')
        receipt = dict(schema_version='documents-receipt/v1', binding=expected,
                       venv=str(directory), observation=observation)
        atomic_json(directory / 'receipt.json', receipt)
        (directory / '.incomplete').unlink()
        atomic_json(root / 'current.json', dict(schema_version='documents-current/v1', version=version,
                    receipt_sha256=digest((directory / 'receipt.json').read_bytes())))
        return dict(status='installed', receipt=receipt)


def current(root):
    pointer = read_json(root / 'current.json')
    if type(pointer) is not dict or set(pointer) != {'schema_version', 'version', 'receipt_sha256'} or pointer['schema_version'] != 'documents-current/v1':
        raise ValueError('invalid current pointer')
    version = pointer['version']
    # Validate version before it can be used as a path component.
    if type(version) is not str or len(version) != 64 or any(c not in '0123456789abcdef' for c in version):
        raise ValueError('invalid current version')
    path = safe_path(root / version / 'receipt.json')
    raw = regular_bytes(path, max_bytes=1024 * 1024)
    if digest(raw) != pointer['receipt_sha256']:
        raise ValueError('current receipt hash mismatch')
    previous = strict_json(raw)
    _, expected, expected_id = binding(previous['binding']['pymupdf_license'])
    if expected_id != version:
        raise ValueError('current environment is stale; explicitly install current profile')
    return version, verify(root, version, expected)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='Explicit dedicated managed environment directory')
    subs = parser.add_subparsers(dest='command', required=True)
    command = subs.add_parser('install')
    command.add_argument('--pymupdf-license', required=True, choices=('agpl-3.0', 'commercial'),
                         help='Explicit AGPL/commercial choice; https://pymupdf.io/licensing')
    command.add_argument('--wheelhouse')
    command.add_argument('--offline', action='store_true')
    subs.add_parser('probe')
    for name in ('pdf-read', 'markdown-render', 'pptx-create', 'latex-source'):
        command = subs.add_parser(name)
        command.add_argument('--input', required=True)
        command.add_argument('--output-dir', required=True)
        if name == 'pdf-read':
            command.add_argument('--pages', type=int, nargs='+', default=[1])
    args = parser.parse_args(argv)
    try:
        if args.command == 'install':
            value = install(args.root, args.pymupdf_license, wheelhouse=args.wheelhouse, offline=args.offline)
        else:
            with managed_root(args.root) as root:
                version, receipt = current(root)
                if args.command == 'probe':
                    value = dict(status='ready', receipt=receipt)
                else:
                    if Path(args.output_dir).exists() or Path(args.output_dir).is_symlink():
                        raise ValueError('output-dir must be a new dedicated directory')
                    limit = 16 * 1024 * 1024 if args.command == 'pdf-read' else 1024 * 1024
                    raw = regular_bytes(safe_path(args.input), max_bytes=limit)
                    if args.command == 'pdf-read':
                        payload = dict(pdf_hex=raw.hex(), pages=args.pages)
                    elif args.command == 'pptx-create':
                        payload = dict(slides=strict_json(raw))
                    else:
                        payload = dict(text=raw.decode('utf-8', errors='strict'))
                    value = run_adapter(root / version / 'bin/python', args.command, payload, args.output_dir)
        if args.command in ('install', 'probe'):
            value = dict(schema_version='documents-result/v1', status='ok',
                         operation=args.command, result=value)
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, DocumentsUnavailable, subprocess.SubprocessError) as exc:
        unavailable = isinstance(exc, (DocumentsUnavailable, subprocess.SubprocessError))
        print(json.dumps(dict(schema_version='documents-result/v1', operation=args.command,
                              status='unavailable' if unavailable else 'invalid', error=str(exc)[:2000])))
        return 2 if unavailable else 3


if __name__ == '__main__':
    raise SystemExit(main())
