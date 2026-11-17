import argparse
import io
import os
from pathlib import Path
import re
import subprocess
import tokenize


DIRECTIVE = re.compile(
    r"#\s*(?:SPDX-License-Identifier: [A-Za-z0-9.()+ -]+|Copyright\b.*|"
    r"noqa(?:: [A-Z]+[0-9]+(?:,\s*[A-Z]+[0-9]+)*)?|type: ignore(?:\[[a-z0-9_, -]+\])?|"
    r"pragma: no (?:cover|branch)|(?:fmt|isort): (?:off|on|skip))\s*", re.I)


def violations(source, added_lines):
    problems = []
    for token in tokenize.tokenize(io.BytesIO(source).readline):
        if token.type != tokenize.COMMENT or token.start[0] not in added_lines:
            continue
        line, column = token.start
        text = token.string
        if line == 1 and column == 0 and text.startswith("#!"):
            continue
        if line <= 2 and re.fullmatch(r"#.*?coding[:=]\s*[-\w.]+(?:\s*-\*-)?\s*", text):
            continue
        if DIRECTIVE.fullmatch(text):
            continue
        problems.append(line)
    return problems


def changed_python(root, base):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)
    base = git("rev-parse", "--verify", base + "^{commit}").decode().strip()
    tracked = set(git("diff", "--name-only", "-z", base, "--").split(b"\0"))
    untracked = set(git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))
    for raw in sorted((tracked | untracked) - {b""}):
        path = root / os.fsdecode(raw)
        if path.suffix != ".py" or not path.exists():
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("redirected Python path: " + str(path))
        source = path.read_bytes()
        if raw in untracked:
            added = set(range(1, len(source.splitlines()) + 1))
        else:
            patch = git("diff", "--no-ext-diff", "--no-textconv", "--unified=0", base, "--", os.fsdecode(raw)).decode("utf-8", "replace")
            added = set()
            for start, count in re.findall(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", patch, re.M):
                added.update(range(int(start), int(start) + int(count or "1")))
        yield path, source, added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(os.environ.get("AGENT_TEST_PROJECT_ROOT", ".")))
    parser.add_argument("--base", default=os.environ.get("AGENT_TEST_BASE", "HEAD"))
    args = parser.parse_args()
    failed = False
    try:
        for path, source, added in changed_python(args.root.resolve(), args.base):
            for line in violations(source, added):
                print(f"{path}:{line}: new explanatory comment; express intent in names/interfaces and enforce requirements with tests")
                failed = True
    except (OSError, ValueError, tokenize.TokenError, SyntaxError, subprocess.CalledProcessError) as exc:
        print(f"blocked: comment check could not complete: {exc}")
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
