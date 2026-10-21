#!/usr/bin/env python3
"""CLI for the output-ladder structural validator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.output_ladder import validate_output_ladder


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--artifacts", required=True)
    args = parser.parse_args(argv)
    try:
        result = validate_output_ladder(args.request, args.manifest, args.artifacts)
    except Exception as exc:  # Internal failures are distinct from contract rejection.
        print(json.dumps({"schema_version": "output-ladder-validation/v1",
                          "state": "internal-error", "error": type(exc).__name__},
                         sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {"ready-for-independent-review": 0, "pending": 2, "invalid": 3}[result["state"]]


if __name__ == "__main__":
    raise SystemExit(main())
