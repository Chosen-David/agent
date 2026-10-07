"""Deterministic bounded CPU observations. Invocation receipt is not acceptance."""
import datetime
import json
from pathlib import Path
import sys

p = Path(__file__).resolve().parent
inputs = json.loads((p / "inputs.json").read_text())["values"]
config = json.loads((p / "config.json").read_text())
if any(type(x) is not int for x in inputs):
    raise ValueError("integer input required")
raw = [{"input": x, "repeat": r, "value": x*x}
       for r in range(config["repeats"]) for x in inputs]
(p / "raw").mkdir(exist_ok=True)
(p / "derived").mkdir(exist_ok=True)
receipt = p / "raw/producer-invocations.jsonl"
with receipt.open("a") as stream:
    stream.write(json.dumps({"command": sys.argv, "time": datetime.datetime.now(datetime.timezone.utc).isoformat()}) + "\n")
(p / "raw/samples.json").write_text(json.dumps(raw, indent=2) + "\n")
(p / "derived/summary.json").write_text(json.dumps({"sum_of_squares": sum(row["value"] for row in raw), "samples": len(raw)}, indent=2) + "\n")
