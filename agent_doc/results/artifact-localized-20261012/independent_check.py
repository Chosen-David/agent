"""Independent ART-LOCAL-01 semantic, integrity, and timing cross-check.

This intentionally does not use ``restore_comparison``.  It loads the frozen
baseline from Git, calls only the public producer entry, and applies packets
with a small verifier-owned implementation.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = "71496c7b1f42b94616343683c7671b6a0e6e8a3b"
sys.path.insert(0, str(ROOT))
import agent_runtime.artifact_context as candidate


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def wire_size(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, allow_nan=False,
                          separators=(",", ":")).encode("utf-8"))


def independent_apply(root: Path, packet: dict, before_ref: dict,
                      after_ref: dict) -> tuple[str, str]:
    """Apply a comparison without calling either production restorer."""
    assert packet["schema_version"] == "artifact-comparison/v2"
    assert packet["project_root"] == str(root)
    assert packet["position_unit"] == "lines with terminators"
    old = packet["before"]
    assert old["ref"] == before_ref
    before = old["text"]
    assert sha(before.encode("utf-8")) == before_ref["sha256"]
    new = packet["after"]
    assert new["ref"] == after_ref
    representation = new["representation"]
    lines = before.splitlines(keepends=True)
    if representation == "full":
        after = new["text"]
    elif representation == "identical":
        assert before_ref["sha256"] == after_ref["sha256"]
        after = before
    elif representation == "splice":
        patch = new["splice"]
        assert patch["base_sha256"] == before_ref["sha256"]
        start, delete = patch["start"], patch["delete"]
        assert type(start) is int and type(delete) is int
        assert 0 <= start <= len(lines)
        assert 0 <= delete <= len(lines) - start
        after = "".join(lines[:start]) + patch["insert"] + \
                "".join(lines[start + delete:])
    elif representation == "edits":
        patch = new["patch"]
        assert patch["base_sha256"] == before_ref["sha256"]
        cursor = 0
        pieces: list[str] = []
        for edit in patch["edits"]:
            start, delete = edit["start"], edit["delete"]
            assert type(start) is int and type(delete) is int
            assert cursor <= start <= len(lines)
            assert 0 <= delete <= len(lines) - start
            pieces.extend(lines[cursor:start])
            pieces.append(edit["insert"])
            cursor = start + delete
        pieces.extend(lines[cursor:])
        after = "".join(pieces)
    else:
        raise AssertionError(f"unknown representation: {representation}")
    assert sha(after.encode("utf-8")) == after_ref["sha256"]
    return before, after


baseline_source = subprocess.check_output(
    ["git", "show", BASE + ":agent_runtime/artifact_context.py"], cwd=ROOT
).decode("utf-8")
baseline = types.ModuleType("agent_runtime._independent_localized_baseline")
baseline.__package__ = "agent_runtime"
exec(compile(baseline_source, "<independent-frozen-baseline>", "exec"),
     baseline.__dict__)

measurement_path = OUT / "measurement.json"
measurement = json.loads(measurement_path.read_text())
producer_rows = measurement["paired_samples_ms"]
producer_baseline_median = statistics.median(
    row["baseline"] for row in producer_rows)
producer_candidate_median = statistics.median(
    row["candidate"] for row in producer_rows)
producer_reduction = 1 - producer_candidate_median / producer_baseline_median
assert len(producer_rows) == 7
assert all(math.isfinite(value) and value >= 0
           for row in producer_rows for value in row.values())
assert producer_baseline_median == measurement["baseline_median_ms"]
assert producer_candidate_median == measurement["candidate_median_ms"]
assert producer_reduction == measurement["reduction_fraction"]
assert sha(baseline_source.encode()) == measurement["baseline_code_sha256"]
assert sha((ROOT / "agent_runtime/artifact_context.py").read_bytes()) == \
       measurement["candidate_code_sha256"]

curated = [
    ("", ""), ("", "new"), ("old", ""), ("old", "new"),
    ("a\r\nb\n", "a\r\n新\n"),
    ("head\nbody\ntail\n", "HEAD\nbody\ntail\n"),
    ("head\nbody\ntail\n", "head\nbody\nTAIL\n"),
    ("head\nbody\ntail\n", "head\ninsert\nbody\ntail\n"),
    ("head\nbody\ntail\n", "head\ntail\n"),
    ("🙂\r\n甲\n乙", "🙂\r\n龙\n乙"),
    ("x\n" * 2048, "x\n" * 1024 + "y\n" + "x\n" * 1023),
    ("x\n" * 2049, "x\n" * 1024 + "y\n" + "x\n" * 1024),
    ("x" * 65536, "y" + "x" * 65535),
    ("x" * 65537, "y" + "x" * 65536),
    ("same\n" * 80, "same\n" * 40 + "different\n" + "same\n" * 39),
    ("a\nb\na\nb\n" * 40, "a\nb\na\nQ\n" + "a\nb\na\nb\n" * 39),
]
rng = random.Random(190823)
alphabet = ["", "a\n", "b\n", "same\n", "\r\n", "甲\n", "🙂\r\n"]
random_cases = []
for _ in range(3000):
    old_lines = [rng.choice(alphabet) for _ in range(rng.randrange(0, 129))]
    new_lines = old_lines[:]
    for _ in range(rng.randrange(1, 7)):
        at = rng.randrange(len(new_lines) + 1)
        delete = rng.randrange(0, min(6, len(new_lines) - at) + 1)
        inserted = [rng.choice(alphabet) for _ in range(rng.randrange(0, 6))]
        new_lines[at:at + delete] = inserted
    random_cases.append(("".join(old_lines), "".join(new_lines)))
cases = curated + random_cases

checks = 0
changed_packets = 0
larger_packets = 0
wire_regressions = []
representations: dict[str, int] = {}
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory).resolve()

    def refs(before: str, after: str) -> tuple[dict, dict]:
        result = []
        for name, text in (("before", before), ("after", after)):
            raw = text.encode("utf-8")
            (root / name).write_bytes(raw)
            result.append({"path": name, "sha256": sha(raw)})
        return result[0], result[1]

    for before, after in cases:
        before_ref, after_ref = refs(before, after)
        for counted in (False, True):
            kwargs = {"multi_edit": True, "reuse_identical": True,
                      "max_chars": 500000}
            if counted:
                kwargs["token_counter"] = lambda wire: len(wire.encode("utf-8"))
            old_packet = baseline.compare_artifacts(
                root, before_ref, after_ref, **kwargs)
            new_packet = candidate.compare_artifacts(
                root, before_ref, after_ref, **kwargs)
            assert independent_apply(root, old_packet, before_ref, after_ref) == \
                   (before, after)
            assert independent_apply(root, new_packet, before_ref, after_ref) == \
                   (before, after)
            old_size, new_size = wire_size(old_packet), wire_size(new_packet)
            if new_size > old_size:
                larger_packets += 1
                if len(wire_regressions) < 10:
                    wire_regressions.append({
                        "case_index": cases.index((before, after)),
                        "counted": counted,
                        "before_sha256": sha(before.encode("utf-8")),
                        "after_sha256": sha(after.encode("utf-8")),
                        "before_chars": len(before),
                        "after_chars": len(after),
                        "baseline_representation": old_packet["after"]["representation"],
                        "candidate_representation": new_packet["after"]["representation"],
                        "baseline_wire_bytes": old_size,
                        "candidate_wire_bytes": new_size,
                    })
            changed_packets += old_packet != new_packet
            name = new_packet["after"]["representation"]
            representations[name] = representations.get(name, 0) + 1
            checks += 1

    before = "same recurring status line\n" * 1024 + "Status: old\n" + \
             "same recurring status line\n" * 1023
    after = "same recurring status line\n" * 1024 + "Status: new\n" + \
            "same recurring status line\n" * 1023
    before_ref, after_ref = refs(before, after)
    kwargs = {"multi_edit": True, "max_chars": 500000}
    baseline.compare_artifacts(root, before_ref, after_ref, **kwargs)
    candidate.compare_artifacts(root, before_ref, after_ref, **kwargs)
    timings = []
    for trial in range(7):
        row = {}
        order = [("candidate", candidate.compare_artifacts),
                 ("baseline", baseline.compare_artifacts)]
        if trial % 2:
            order.reverse()
        for name, function in order:
            started = time.perf_counter_ns()
            packet = function(root, before_ref, after_ref, **kwargs)
            row[name] = (time.perf_counter_ns() - started) / 1e6
            assert independent_apply(root, packet, before_ref, after_ref) == \
                   (before, after)
        timings.append(row)

baseline_median = statistics.median(row["baseline"] for row in timings)
candidate_median = statistics.median(row["candidate"] for row in timings)
reduction = 1 - candidate_median / baseline_median
assert checks >= 2000
assert candidate_median <= 0.5 * baseline_median

workload = before + "\0" + after
result = {
    "schema_version": "artifact-localized-independent-check/v1",
    "verifier_actor": "artifact_localized_verifier",
    "baseline": BASE,
    "python": sys.version,
    "platform": platform.platform(),
    "hashes": {
        "candidate_code_sha256": sha(
            (ROOT / "agent_runtime/artifact_context.py").read_bytes()),
        "baseline_code_sha256": sha(baseline_source.encode()),
        "producer_measurement_sha256": sha(measurement_path.read_bytes()),
        "validation_plan_sha256": sha((OUT / "validation_plan.json").read_bytes()),
        "independent_check_sha256": sha(Path(__file__).read_bytes()),
        "workload_sha256": sha(workload.encode()),
    },
    "producer_recalculation": {
        "sample_count": len(producer_rows),
        "baseline_median_ms": producer_baseline_median,
        "candidate_median_ms": producer_candidate_median,
        "reduction_fraction": producer_reduction,
        "matches_recorded": True,
    },
    "semantic_differential": {
        "seed": 190823,
        "curated_cases": len(curated),
        "random_cases": len(random_cases),
        "complete_entry_checks": checks,
        "changed_packets": changed_packets,
        "larger_packets": larger_packets,
        "wire_regressions": wire_regressions,
        "candidate_representations": representations,
    },
    "independent_paired_samples_ms": timings,
    "independent_baseline_median_ms": baseline_median,
    "independent_candidate_median_ms": candidate_median,
    "independent_reduction_fraction": reduction,
    "acceptance_verdict": "fail" if larger_packets else "pass",
    "scope": ("complete compare_artifacts CPU entry on bounded synthetic "
              "localized text changes; no model, token, cash, GPU, or "
              "end-to-end claim"),
}
print(json.dumps(result, ensure_ascii=False, indent=2))
