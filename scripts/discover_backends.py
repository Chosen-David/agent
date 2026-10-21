#!/usr/bin/env python3
"""Report which optional external backends appear to be available.

This script never installs, authenticates, starts, or calls a backend. It only
checks importable Python modules, installed Python distribution metadata, and
executable names declared in the registry. Distribution metadata is used for
version reporting without importing or executing the backend itself.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.context_serialization import render_context
from agent_runtime.external_json import ExternalJSONError, load_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "config" / "backend_registry.json"


def validate_registry(data):
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] != 1
            or not isinstance(data.get("backends"), list)):
        raise ValueError("backend registry must be a schema_version 1 object")
    seen = set()
    for entry in data["backends"]:
        if (not isinstance(entry, dict)
                or any(not isinstance(entry.get(key), str) or not entry[key]
                       for key in ("id", "adoption", "category", "repo"))
                or entry["id"] in seen or not isinstance(entry.get("detect"), dict)):
            raise ValueError("backend registry entry has invalid structure")
        seen.add(entry["id"])
        for key in ("python_modules", "commands", "python_distributions"):
            values = entry["detect"].get(key, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValueError("backend detection fields must be string lists")
    return data


def _python_versions(detect: dict, modules: dict[str, bool]) -> tuple[dict[str, str], str | None, str | None]:
    declared = list(detect.get("python_distributions", []))
    candidates = set(declared)
    try:
        package_map = importlib.metadata.packages_distributions()
    except Exception:
        package_map = {}
    for module_name, available in modules.items():
        if available:
            candidates.update(package_map.get(module_name, []) or [])
    versions: dict[str, str] = {}
    for distribution in sorted(candidates):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            continue
        except Exception:
            continue
    preferred = declared + [name for name in sorted(versions) if name not in declared]
    for distribution in preferred:
        if distribution in versions:
            return versions, versions[distribution], f"python_distribution:{distribution}"
    return versions, None, None


def probe_backend(entry: dict) -> dict:
    detect = entry.get("detect", {})
    # find_spec('parent.child') imports parent. Probe only top-level modules so
    # inventory cannot run third-party initialization code.
    modules = {}
    errors = {}
    for name in detect.get("python_modules", []):
        if not name.isidentifier():
            modules[name] = False
            errors[name] = "only top-level module probes are supported"
            continue
        try:
            modules[name] = importlib.util.find_spec(name) is not None
        except (ImportError, ValueError, AttributeError) as exc:
            modules[name] = False
            errors[name] = type(exc).__name__
    commands = {name: shutil.which(name) is not None for name in detect.get("commands", [])}
    versions, detected_version, version_source = _python_versions(detect, modules)
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
        "readiness": "not_verified",
        "authorized": False,
        "probe_errors": errors,
        "detected_version": detected_version,
        "version_source": version_source,
        "python_versions": versions,
        "python_modules": modules,
        "commands": commands,
        "repo": entry["repo"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--only", action="append", default=[], help="backend id; repeatable")
    formatting = parser.add_mutually_exclusive_group()
    formatting.add_argument("--pretty", action="store_true")
    formatting.add_argument("--compact", action="store_true", help="preserve all JSON fields without formatting whitespace")
    args = parser.parse_args()
    data = validate_registry(load_json(args.registry, max_bytes=1024 * 1024))
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
    print((render_context(result, compact=True) if args.compact else json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ExternalJSONError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
              file=sys.stderr)
        raise SystemExit(2)
