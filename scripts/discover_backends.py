#!/usr/bin/env python3
"""Report which optional external backends appear to be available.

This script never installs, authenticates, starts, or calls a backend. It only
checks importable Python modules and executable names declared in the registry.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "config" / "backend_registry.json"


def probe_backend(entry: dict) -> dict:
    detect = entry.get("detect", {})
    modules = {
        name: importlib.util.find_spec(name) is not None
        for name in detect.get("python_modules", [])
    }
    commands = {
        name: shutil.which(name) is not None
        for name in detect.get("commands", [])
    }
    probes = list(modules.values()) + list(commands.values())
    if probes:
        status = "available" if any(probes) else "not_detected"
    else:
        status = "manual_check"
    return {
        "id": entry["id"],
        "adoption": entry["adoption"],
        "category": entry["category"],
        "status": status,
        "python_modules": modules,
        "commands": commands,
        "repo": entry["repo"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--only", action="append", default=[], help="backend id; repeatable")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    data = json.loads(args.registry.read_text(encoding="utf-8"))
    selected = data["backends"]
    if args.only:
        wanted = set(args.only)
        selected = [item for item in selected if item["id"] in wanted]
        missing = sorted(wanted - {item["id"] for item in selected})
        if missing:
            raise SystemExit(f"unknown backend ids: {', '.join(missing)}")

    result = {
        "registry": str(args.registry),
        "schema_version": data["schema_version"],
        "backends": [probe_backend(item) for item in selected],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
