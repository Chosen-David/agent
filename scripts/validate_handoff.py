#!/usr/bin/env python3
"""Validate local handoff integrity, not truth or LLM compliance. No network."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def validate(record: dict, root: Path, require_complete: bool = False) -> list[str]:
    errors = []
    try:
        root = root.resolve()
    except (OSError, ValueError, RuntimeError) as exc:
        return [f"root: cannot resolve path ({type(exc).__name__})"]
    if not isinstance(record, dict):
        return ["handoff must be an object"]
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        errors.append("unsupported schema_version")
    for key in ("run_id", "role", "input_version"):
        if not isinstance(record.get(key), str) or not record[key].strip():
            errors.append(f"missing {key}")
    status = record.get("status")
    if not isinstance(status, str) or status not in {"completed", "partial", "blocked", "failed", "not_run"}:
        errors.append("invalid status")
    if require_complete and status != "completed":
        errors.append("completion gate: run is not completed")
    limitations = record.get("limitations")
    if not isinstance(limitations, list) or any(not isinstance(x, str) for x in limitations):
        errors.append("limitations must be a list of strings")
    elif status != "completed" and not limitations:
        errors.append("non-completed run needs limitations/recovery conditions")

    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        errors.append("artifacts must be a list")
        artifacts = []
    if status == "completed" and not artifacts:
        errors.append("completed run needs an artifact (a saved answer is sufficient)")
    artifact_ids = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append(f"artifact {index} must be an object")
            continue
        aid = artifact.get("id")
        if not isinstance(aid, str) or not aid.strip() or aid in artifact_ids:
            errors.append(f"artifact {index}: missing/duplicate id")
        else:
            artifact_ids.add(aid)
        raw = artifact.get("path")
        if not isinstance(raw, str) or not raw.strip() or "\0" in raw or Path(raw).is_absolute():
            errors.append(f"artifact {index}: path must be relative to root")
            continue
        try:
            path = (root / raw).resolve()
            if not path.is_relative_to(root):
                errors.append(f"artifact {index}: path escapes root")
                continue
            if not path.is_file():
                errors.append(f"artifact {index}: file missing")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except (OSError, ValueError, RuntimeError) as exc:
            errors.append(f"artifact {index}: cannot read path ({type(exc).__name__})")
            continue
        if artifact.get("sha256") != digest:
            errors.append(f"artifact {index}: sha256 mismatch")

    checks = record.get("checks")
    if not isinstance(checks, list):
        errors.append("checks must be a list")
        checks = []
    if status == "completed" and not checks:
        errors.append("completed run needs acceptance checks")
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"check {index} must be an object")
            continue
        if not isinstance(check.get("criterion"), str) or not check["criterion"].strip() or not isinstance(check.get("status"), str) or check["status"] not in {"pass", "fail", "not_run"}:
            errors.append(f"check {index}: criterion/status required")
        refs = check.get("artifact_ids")
        if not isinstance(refs, list) or any(not isinstance(x, str) or x not in artifact_ids for x in refs):
            errors.append(f"check {index}: invalid evidence references")
        elif check.get("status") == "pass" and not refs:
            errors.append(f"check {index}: pass without evidence")
        if status == "completed" and check.get("status") != "pass":
            errors.append(f"check {index}: incomplete check on completed run")

    tasks = record.get("tasks", [])
    if not isinstance(tasks, list):
        errors.append("tasks must be a list")
        tasks = []
    by_id = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("task_id"), str) or not task["task_id"].strip():
            errors.append("task missing task_id")
            continue
        tid = task["task_id"]
        if tid in by_id:
            errors.append(f"duplicate task: {tid}")
        by_id[tid] = task
    graph = {}
    for tid, task in by_id.items():
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            errors.append(f"{tid}: invalid dependencies")
            deps = []
        graph[tid] = deps
        if not isinstance(task.get("status"), str) or task["status"] not in {"todo", "doing", "done", "blocked", "skipped"}:
            errors.append(f"{tid}: invalid task status")
        if status == "completed" and task.get("status") not in ("done", "skipped"):
            errors.append(f"{tid}: unfinished task on completed run")
        for dep in deps:
            if dep not in by_id:
                errors.append(f"{tid}: unknown dependency {dep}")
            elif task.get("status") == "done" and by_id[dep].get("status") != "done":
                errors.append(f"{tid}: done before dependency {dep}")
        evidence = task.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(x, str) or x not in artifact_ids for x in evidence):
            errors.append(f"{tid}: invalid evidence references")
        elif task.get("status") == "done" and not evidence:
            errors.append(f"{tid}: done without evidence")
        reason = task.get("reason")
        if task.get("status") in ("blocked", "skipped") and (not isinstance(reason, str) or not reason.strip()):
            errors.append(f"{tid}: reason/recovery required")
    # Iterative topological elimination avoids recursion limits on a long DAG.
    pending = set(graph)
    while pending:
        ready = {tid for tid in pending if not (set(graph[tid]) & pending)}
        if not ready:
            errors.append("task dependency cycle")
            break
        pending -= ready
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        errors = validate(record, args.root, args.require_complete)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"integrity_valid": not errors, "errors": errors,
                      "scope": "local integrity only; no semantic or visual certification"}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
