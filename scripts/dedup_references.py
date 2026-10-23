#!/usr/bin/env python3
"""Replace duplicate reference file copies with relative symlinks to a canonical copy.

Many skills ship byte-identical copies of the same workflow/reference files in their
local ``references/`` directory.  This blows up disk, install payload, and the number
of files the installer must copy.  For every group of identical files we keep ONE
canonical copy under ``shared-references/`` and replace the others with a relative
symlink pointing at it.  Symlinks travel with their parent skill directory symlink
(see ``installation.json``), so installed projects see the same deduplicated tree.

Usage::

    python3 scripts/dedup_references.py --dry-run   # preview
    python3 scripts/dedup_references.py              # apply
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFS_ROOT = ROOT / "plugins"
SHARED = ROOT / "shared-references"


def md5(path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def rel(target, start):
    """Relative path from ``start``'s parent directory to ``target`` (OS ups ok)."""
    from os.path import relpath
    return Path(relpath(target, start.parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    files = sorted(REFS_ROOT.rglob("references/*.md"))
    by_hash = {}
    for f in files:
        by_hash.setdefault(md5(f), []).append(f)

    groups = {h: paths for h, paths in by_hash.items() if len(paths) > 1}
    total_saved = 0
    links_created = 0

    for h, paths in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        canonical_name = paths[0].name
        canonical = SHARED / canonical_name
        if not args.dry_run:
            SHARED.mkdir(exist_ok=True)
            if not canonical.exists():
                canonical.write_bytes(paths[0].read_bytes())

        n = len(paths) - 1  # all-but-first become symlinks
        saved = paths[0].stat().st_size * n
        total_saved += saved
        links_created += n

        print(f"  {n+1}x {canonical_name}  ->  {SHARED.relative_to(ROOT)}/{canonical_name}")
        for p in paths[1:]:
            target = rel(canonical, p)
            print(f"      {p.relative_to(ROOT)}  ->  {target}")
            if not args.dry_run:
                p.unlink()
                p.symlink_to(target)

    print()
    print(f"Total: {links_created} symlinks created, {total_saved:,} bytes ({total_saved/1024:.0f} KB) saved on disk")
    print(f"Groups deduplicated: {len(groups)}")


if __name__ == "__main__":
    raise SystemExit(main())
