#!/usr/bin/env python3
"""Read immutable Git source evidence; never import or execute target code."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import subprocess


def git(repo, *args):
    return subprocess.check_output(
        ["git", "--no-pager", "--no-replace-objects", "-C", str(repo), *args], stderr=subprocess.PIPE,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )


def symbols(tree, prefix=""):
    """Include definitions nested inside control-flow and qualified scopes."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name = prefix + node.name
            start = min([node.lineno] + [d.lineno for d in node.decorator_list])
            yield name, start, node.end_lineno
            yield from symbols(node, name + ".")
        else:
            yield from symbols(node, prefix)


def capture(repo, commit, path, start=None, end=None, symbol=None, label=None):
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit):
        raise ValueError("commit must be a full lowercase object ID, not a moving ref")
    if git(repo, "cat-file", "-t", commit).strip() != b"commit":
        raise ValueError("object must be a commit")
    p = PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts or str(p) != path or "\\" in path:
        raise ValueError("path must be a canonical repository-relative POSIX path")
    if git(repo, "cat-file", "-t", f"{commit}:{path}").strip() != b"blob":
        raise ValueError("path must identify a source blob, not a tree")
    raw = git(repo, "show", f"{commit}:{path}")
    if b"\0" in raw:
        raise ValueError("binary source is unsupported")
    source = raw.decode("utf-8")
    lines = source.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    bounds = None
    if symbol:
        if p.suffix != ".py":
            raise ValueError("AST symbols support Python only; use lines and --label")
        if "\r" in source.replace("\r\n", ""):
            raise ValueError("bare CR is incompatible with Git LF line anchors; use explicit lines")
        matches = [(lo, hi) for name, lo, hi in symbols(ast.parse(source)) if name == symbol]
        if len(matches) != 1:
            raise ValueError("symbol missing or ambiguous; supply a unique qualified name")
        bounds = matches[0]
    if (start is None) != (end is None):
        raise ValueError("provide both start and end")
    if start is None:
        if bounds is None:
            raise ValueError("provide a Python symbol or explicit line range")
        start, end = bounds
    if not (1 <= start <= end <= len(lines)):
        raise ValueError("line range is outside the source")
    if bounds and not (bounds[0] <= start <= end <= bounds[1]):
        raise ValueError("line range is outside the selected symbol")
    return {
        "schema_version": 1, "evidence_kind": "source_fact",
        "commit": commit, "path": path,
        "symbol": symbol or label,
        "symbol_resolution": "python_ast" if symbol else "manual_label",
        "start_line": start, "end_line": end,
        "blob_sha256": hashlib.sha256(raw).hexdigest(),
        "excerpt": "\n".join(lines[start - 1:end]),
        "limitation": "Location evidence only; no call-graph, semantic or runtime verification.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("repo", "commit", "path"):
        parser.add_argument("--" + field, required=True)
    for field in ("start", "end"):
        parser.add_argument("--" + field, type=int)
    parser.add_argument("--symbol")
    parser.add_argument("--label")
    args = parser.parse_args()
    try:
        result = capture(**vars(args))
    except (ValueError, SyntaxError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"source evidence failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
