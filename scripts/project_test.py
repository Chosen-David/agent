#!/usr/bin/env python3
"""Run trusted, serial project checks against an explicitly selected Git root."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE).decode().strip()


def source_state(root):
    names = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"])
    entries = {}
    for raw in sorted(set(names.split(b"\0")) - {b""}):
        name = os.fsdecode(raw)
        path = root / name
        if path.is_symlink():
            value = "link:" + os.readlink(path)
        elif path.is_file():
            value = digest(path.read_bytes()) + ":" + str(path.stat().st_mode)
        else:
            value = "missing-or-submodule"
        entries[name] = value
    return {"head": git(root, "rev-parse", "HEAD"),
            "status": git(root, "status", "--porcelain"),
            "content_sha256": digest(json.dumps(entries, sort_keys=True).encode())}


def suite_state(directory):
    files = {}
    for path in sorted(directory.rglob("*")):
        if "__pycache__" in path.parts:
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise ValueError("suite contains a redirected Python file")
        if path.is_file():
            files[str(path.relative_to(directory))] = digest(path.read_bytes())
    return files


def worker(directory, target, result_path):
    sys.path.insert(0, str(target))
    os.environ["AGENT_TEST_PROJECT_ROOT"] = str(target)
    suite = unittest.TestLoader().discover(str(directory), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    passed = result.wasSuccessful() and result.testsRun > 0 and not result.skipped and not result.expectedFailures
    Path(result_path).write_text(json.dumps({"tests": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "expected_failures": len(result.expectedFailures), "passed": passed}))
    return 0 if passed else 1


def prepare_suite(workflow, project, target, *, task=None):
    if not project or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in project):
        raise ValueError("project must be a single stable identifier")
    workflow, target = workflow.resolve(), target.resolve()
    if Path(git(target, "rev-parse", "--show-toplevel")).resolve() != target:
        raise ValueError("--target must be the exact Git repository root")
    directory = workflow / "agent_doc" / project / "test"
    if task is not None:
        if not isinstance(task, str) or not task or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in task):
            raise ValueError("task must be a single stable identifier")
        directory = directory / task
    if directory.resolve() != directory:
        raise ValueError("test workspace must not use symlink redirects")
    manifest_path = directory / "suite.json"
    if manifest_path.is_symlink():
        raise ValueError("suite manifest must be a regular file")
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict) or set(manifest) != {"version", "origin", "checks"} or type(manifest["version"]) is not int or manifest["version"] != 1 or not isinstance(manifest["origin"], str):
        raise ValueError("unsupported suite manifest; expected version and origin")
    if git(target, "remote", "get-url", "origin").removesuffix(".git") != manifest["origin"].removesuffix(".git"):
        raise ValueError("target origin differs from suite.json; select the intended repository")
    checks = manifest["checks"]
    if not isinstance(checks, list) or not checks:
        raise ValueError("suite must declare at least one required check")
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "kind", "path", "timeout_seconds", "requirement"}:
            raise ValueError("invalid check fields")
        if not isinstance(check["id"], str) or not check["id"].isalnum() or check["id"] in seen:
            raise ValueError("check IDs must be unique alphanumeric strings")
        seen.add(check["id"])
        if check["kind"] not in ("python", "shell", "unittest") or not isinstance(check["path"], str):
            raise ValueError("unknown check kind or path")
        path = directory / check["path"]
        if not path.resolve().is_relative_to(directory) or path.is_symlink() or not path.exists():
            raise ValueError("check path must exist within the test workspace")
        if (check["kind"] == "unittest") != path.is_dir():
            raise ValueError("unittest requires a directory; script checks require files")
        if type(check["timeout_seconds"]) is not int or not 1 <= check["timeout_seconds"] <= 300:
            raise ValueError("check timeout must be 1..300 seconds")
        if not isinstance(check["requirement"], str) or not check["requirement"].strip():
            raise ValueError("check must identify its prompt/guide requirement")
    return workflow, target, directory, manifest_bytes, manifest, checks


def run(workflow, project, target, output, *, task=None):
    workflow, target, directory, manifest_bytes, manifest, checks = prepare_suite(
        workflow, project, target, task=task)
    manifest_path = directory / "suite.json"
    output = output.absolute()
    if output.resolve().is_relative_to(workflow) or output.resolve().is_relative_to(target):
        raise ValueError("write run evidence outside workflow and target repositories")
    output.mkdir(parents=True, exist_ok=False)
    before = source_state(target)
    sources = suite_state(directory)
    report = {"version": 1, "project": project, "target": str(target), "origin": manifest["origin"],
        "before": before, "suite_sha256": digest(manifest_bytes), "sources": sources,
        "runner_sha256": digest(Path(__file__).read_bytes()), "python": sys.version, "status": "blocked"}
    report["checks"] = []
    failed = False
    try:
        for check in checks:
            item = {**check, "status": "not-run"}
            report["checks"].append(item)
            if failed:
                continue
            result_path = output / (check["id"] + ".result.json")
            path = directory / check["path"]
            if check["kind"] == "unittest":
                command = [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(path), str(target), str(result_path)]
            else:
                command = ([sys.executable, "-B"] if check["kind"] == "python" else ["bash"]) + [str(path)]
            env = {**os.environ, "AGENT_TEST_PROJECT_ROOT": str(target), "AGENT_TEST_OUTPUT": str(output),
                   "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": str(output), "PYTHONPATH": str(target)}
            started = time.monotonic()
            with (output / (check["id"] + ".log")).open("w") as log:
                try:
                    process = subprocess.run(command, cwd=target, env=env, stdout=log, stderr=subprocess.STDOUT,
                                             timeout=check["timeout_seconds"])
                    item["returncode"] = process.returncode
                    item["status"] = "pass" if process.returncode == 0 else "fail"
                    if check["kind"] == "unittest":
                        item["result"] = json.loads(result_path.read_text()) if result_path.exists() else None
                        if not item["result"] or not item["result"]["passed"]:
                            item["status"] = "fail"
                except subprocess.TimeoutExpired:
                    item["status"] = "blocked"
                    item["reason"] = "timeout; do not advance until child effects are reconciled"
            item["wall_seconds"] = time.monotonic() - started
            failed = item["status"] != "pass"
        report["after"] = source_state(target)
        stable = before == report["after"] and sources == suite_state(directory) and manifest_bytes == manifest_path.read_bytes()
        report["stable_inputs"] = stable
        report["status"] = ("blocked" if any(item["status"] == "blocked" for item in report["checks"])
                            else "pass" if stable and not failed else "fail")
    finally:
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    receipt = {"status": report["status"], "report": str(output / "report.json"),
               "stable_inputs": report.get("stable_inputs", False), "checks": []}
    for item in report["checks"]:
        check = {key: item[key] for key in ("id", "status", "returncode", "reason", "result") if key in item}
        if item["status"] != "not-run":
            check["log"] = str(output / (item["id"] + ".log"))
        receipt["checks"].append(check)
    if report["status"] == "pass":
        receipt = {"status": "pass", "report": str(output / "report.json")}
    print(json.dumps(receipt))
    return 0 if report["status"] == "pass" else 1


def main():
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        return worker(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow-root", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task", help="run only this task directory and its suite.json")
    args = parser.parse_args()
    try:
        return run(args.workflow_root, args.project, args.target, args.output, task=args.task)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
