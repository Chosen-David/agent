#!/usr/bin/env python3
"""Inspect, migrate or check project documents without writing human guides."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.project_docs import main

if __name__ == '__main__':
    raise SystemExit(main())
