"""Check that deterministic gates reject known faults, without changing the checkout."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

checker = Path(__file__).with_name("compile_structure.py")
root = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])
original = (root / "agent_runtime/core.py").read_bytes()
cases = [("baseline", original, 0, None),
         ("legaltext", original + b"\n_BOUNDARY_TEXT = 'import scripts.project_test'\n", 0, None),
         ("syntax", original + b"\ndef broken(:\n", 1, "compile failure:"),
         ("dependency", original + b"\nimport scripts.project_test\n", 1, "core must not import CLI scripts")]
observations = []
with tempfile.TemporaryDirectory(prefix="mutation-") as tmp:
    fixture = Path(tmp)
    (fixture / "agent_runtime").mkdir()
    for name, content, expected, diagnostic in cases:
        (fixture / "agent_runtime/core.py").write_bytes(content)
        result = subprocess.run([sys.executable, "-B", str(checker)],
            env={**os.environ, "AGENT_TEST_PROJECT_ROOT": str(fixture)},
            capture_output=True, text=True, timeout=10)
        verified = (result.returncode == expected and not result.stderr.strip() and
                    (diagnostic is None or diagnostic in result.stdout))
        observations.append({"mutation": name, "expected_exit": expected, "actual_exit": result.returncode,
                             "expected_diagnostic": diagnostic, "verified": verified,
                             "stdout": result.stdout, "stderr": result.stderr})
print(json.dumps(observations, indent=2))
raise SystemExit(0 if all(item["verified"] for item in observations) else 1)
