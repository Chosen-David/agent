"""Structural output-ladder tests; no semantic or visual acceptance claim."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.output_ladder import LEVELS, ROLE_REQUIREMENTS, validate_output_ladder


ROOT = Path(__file__).resolve().parents[1]


class OutputLadderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="output-ladder-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root / "artifacts"
        self.artifacts.mkdir()
        self.request_path = self.root / "request.json"
        self.manifest_path = self.root / "manifest.json"
        self.request = {
            "schema_version": "output-ladder-request/v1",
            "request_id": "REQ-1",
            "input_version": "input-sha256:fixture",
            "audience": "research engineer",
            "language": "zh-CN",
            "claims": [{"id": "C1", "text": "The bounded fixture exists.",
                        "evidence_refs": ["source:fixture"]}],
            "requested_level": "controlled_text",
            "allow_downgrade": False,
            "require_contiguous": False,
            "required_checks": {level: [] for level in LEVELS},
            "capability_receipt_sha256": None,
        }

    def write_request(self, value=None, *, raw=None):
        if raw is None:
            raw = json.dumps(value or self.request, sort_keys=True).encode()
        self.request_path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def artifact(self, aid, level, role, body=None, path=None):
        name = path or f"{aid}.txt"
        payload = (body or f"{aid}:{level}:{role}\n").encode()
        target = self.artifacts / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return {"id": aid, "level": level, "role": role, "path": name,
                "declared_sha256": hashlib.sha256(payload).hexdigest()}

    def manifest(self, delivered=("controlled_text",), *, request_sha=None):
        request_sha = request_sha or self.write_request()
        artifacts = []
        for level in delivered:
            for role in sorted(ROLE_REQUIREMENTS[level]):
                artifacts.append(self.artifact(f"A-{level}-{role}", level, role))
        checks = []
        for level in delivered:
            evidence = [a["id"] for a in artifacts if a["level"] == level]
            for check_id in self.request["required_checks"][level]:
                checks.append({"check_id": f"producer-{level}-{check_id}", "level": level,
                               "request_check_id": check_id, "status": "pass",
                               "evidence_artifact_ids": evidence,
                               "producer_observer": "producer-self-report"})
        return {
            "schema_version": "output-ladder-manifest/v1",
            "request_id": self.request["request_id"],
            "request_sha256": request_sha,
            "producer": "fixture-producer",
            "delivered_levels": list(delivered),
            "claims_by_level": {level: ["C1"] for level in delivered},
            "artifacts": artifacts,
            "checks": checks,
            "limitations": ["fixture only"],
            "recovery": ["run independent review"],
        }

    def validate(self, manifest):
        self.manifest_path.write_text(json.dumps(manifest, sort_keys=True))
        return validate_output_ladder(self.request_path, self.manifest_path, self.artifacts)

    def test_text_baseline_is_ready_only_for_independent_review(self):
        self.request["required_checks"]["controlled_text"] = ["factual"]
        result = self.validate(self.manifest())
        self.assertEqual(result["state"], "ready-for-independent-review")
        self.assertTrue(result["independent_review_required"])
        self.assertNotIn("accepted", result)

    def test_noncontiguous_web_is_allowed_but_contiguous_request_rejects_it(self):
        self.request["requested_level"] = "interactive_web"
        manifest = self.manifest(("controlled_text", "interactive_web"))
        self.assertEqual(self.validate(manifest)["state"], "ready-for-independent-review")
        self.request["require_contiguous"] = True
        request_sha = self.write_request()
        manifest["request_sha256"] = request_sha
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_downgrade_has_deterministic_pending_or_invalid_state(self):
        self.request["requested_level"] = "explainer_video"
        self.request["allow_downgrade"] = True
        manifest = self.manifest()
        self.assertEqual(self.validate(manifest)["state"], "pending")
        self.request["allow_downgrade"] = False
        manifest["request_sha256"] = self.write_request()
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_request_byte_change_invalidates_old_manifest(self):
        manifest = self.manifest()
        self.request["audience"] = "different audience"
        self.write_request()
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_exact_claim_set_and_required_checks_are_enforced(self):
        self.request["claims"].append({"id": "C2", "text": "Second claim",
                                      "evidence_refs": ["source:fixture"]})
        self.request["required_checks"]["controlled_text"] = ["factual"]
        manifest = self.manifest()
        manifest["claims_by_level"]["controlled_text"] = ["C1"]
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        manifest["claims_by_level"]["controlled_text"] = ["C1", "C2"]
        manifest["checks"] = []
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_failed_or_not_run_check_stays_pending(self):
        self.request["required_checks"]["controlled_text"] = ["factual"]
        for status in ("fail", "not_run"):
            with self.subTest(status=status):
                manifest = self.manifest()
                manifest["checks"][0]["status"] = status
                self.assertEqual(self.validate(manifest)["state"], "pending")

    def test_producer_observer_never_upgrades_trust(self):
        self.request["required_checks"]["controlled_text"] = ["factual"]
        manifest = self.manifest()
        manifest["checks"][0]["producer_observer"] = "independent-reviewer"
        result = self.validate(manifest)
        self.assertEqual(result["state"], "ready-for-independent-review")
        self.assertTrue(result["independent_review_required"])

    def test_check_ids_are_unique_and_evidence_stays_in_its_level(self):
        self.request["requested_level"] = "diagram"
        self.request["required_checks"]["controlled_text"] = ["text-factual"]
        self.request["required_checks"]["diagram"] = ["diagram-factual"]
        manifest = self.manifest(("controlled_text", "diagram"))
        manifest["checks"][1]["check_id"] = manifest["checks"][0]["check_id"]
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        manifest = self.manifest(("controlled_text", "diagram"))
        text_id = next(a["id"] for a in manifest["artifacts"]
                       if a["level"] == "controlled_text")
        manifest["checks"][1]["evidence_artifact_ids"] = [text_id]
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_unknown_fields_duplicate_json_keys_and_duplicate_paths_rejected(self):
        manifest = self.manifest()
        manifest["extra"] = True
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        manifest = self.manifest()
        manifest["artifacts"].append({**manifest["artifacts"][0], "id": "A-other"})
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        manifest = self.manifest()
        self.manifest_path.write_text(json.dumps(manifest, sort_keys=True))
        raw = self.request_path.read_text()
        self.write_request(raw=(raw[:-1] + ',"request_id":"REQ-2"}').encode())
        result = validate_output_ladder(self.request_path, self.manifest_path, self.artifacts)
        self.assertEqual(result["state"], "invalid")

    def test_identifier_bounds_and_wrong_types_fail_closed_under_optimized_python(self):
        self.request["request_id"] = "x" * 129
        manifest = self.manifest()
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        self.request["request_id"] = "REQ-1"
        self.request["allow_downgrade"] = 1
        manifest["request_id"] = "REQ-1"
        manifest["request_sha256"] = self.write_request()
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_symlink_directory_and_fifo_artifacts_fail_without_blocking(self):
        bad_kinds = ["symlink", "directory"] + (["fifo"] if hasattr(os, "mkfifo") else [])
        for kind in bad_kinds:
            with self.subTest(kind=kind):
                manifest = self.manifest()
                artifact = manifest["artifacts"][0]
                path = self.artifacts / f"bad-{kind}"
                artifact["path"] = path.name
                if kind == "symlink":
                    outside = self.root / "outside.txt"
                    outside.write_text("outside")
                    path.symlink_to(outside)
                elif kind == "directory":
                    path.mkdir()
                else:
                    os.mkfifo(path)
                self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_symlink_in_artifact_root_ancestry_is_rejected(self):
        manifest = self.manifest()
        self.manifest_path.write_text(json.dumps(manifest, sort_keys=True))
        alias = self.root / "root-alias"
        alias.symlink_to(self.root, target_is_directory=True)
        result = validate_output_ladder(self.request_path, self.manifest_path,
                                        alias / "artifacts")
        self.assertEqual(result["state"], "invalid")

    def test_artifact_hash_and_lexical_path_are_bound(self):
        manifest = self.manifest()
        artifact = manifest["artifacts"][0]
        (self.artifacts / artifact["path"]).write_text("changed")
        self.assertEqual(self.validate(manifest)["state"], "invalid")
        manifest = self.manifest()
        manifest["artifacts"][0]["path"] = "nested/../escape.txt"
        self.assertEqual(self.validate(manifest)["state"], "invalid")

    def test_cli_exit_codes_are_stable(self):
        script = ROOT / "scripts/output_ladder.py"
        cases = [("ready-for-independent-review", 0), ("pending", 2), ("invalid", 3)]
        for state, code in cases:
            with self.subTest(state=state):
                self.request["requested_level"] = ("controlled_text" if state == "ready-for-independent-review"
                                                   else "diagram")
                self.request["allow_downgrade"] = state != "invalid"
                manifest = self.manifest()
                if state == "invalid":
                    manifest["request_sha256"] = "0" * 64
                self.manifest_path.write_text(json.dumps(manifest))
                result = subprocess.run([sys.executable, str(script), "--request", str(self.request_path),
                                         "--manifest", str(self.manifest_path), "--artifacts", str(self.artifacts)],
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["state"], state)


if __name__ == "__main__":
    unittest.main()
