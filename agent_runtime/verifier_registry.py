"""Load named host-owned result verifiers. Worker manifests never select executable code."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat


def trusted_file(path):
    path = Path(path).resolve(strict=True)
    if not path.is_file():
        raise ValueError('expected a regular verifier file')
    for part in (path, *path.parents):
        info = part.stat()
        if info.st_uid not in (0, os.getuid()) or info.st_mode & stat.S_IWOTH:
            raise PermissionError(f'untrusted owner or world-writable path: {part}')
    return path


def resolve(registry, capability):
    config = json.loads(trusted_file(registry).read_bytes())
    if config.get('schema') != 'host-verifiers/v1':
        raise ValueError('unsupported verifier registry')
    entry = config['capabilities'][capability]
    path = trusted_file(entry['path'])
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        raise ValueError('host adapter changed since registration')
    spec = importlib.util.spec_from_file_location('registered_result_verifier', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(data, str(path), 'exec'), module.__dict__)
    if not callable(getattr(module, 'verify', None)):
        raise TypeError('adapter has no verify(root, manifest, plan) callback')
    return module.verify


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Discover and check host-registered verifier callbacks')
    parser.add_argument('registry', type=Path)
    parser.add_argument('capability', nargs='?')
    args = parser.parse_args()
    if args.capability is None:
        entries = json.loads(trusted_file(args.registry).read_bytes())['capabilities']
        print(json.dumps(sorted(entries)))
        return
    verifier = resolve(args.registry, args.capability)
    import inspect
    inspect.signature(verifier).bind(None, {}, {})
    print(json.dumps({'capability': args.capability, 'callback': 'available'}))


if __name__ == '__main__':
    main()
