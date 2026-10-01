import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "discover_backends.py"
spec = importlib.util.spec_from_file_location("discover_backends", SCRIPT)
discover = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discover)


class DiscoverBackendsTests(unittest.TestCase):
    def test_reports_python_distribution_version_without_importing_backend(self):
        entry = {
            "id": "demo",
            "adoption": "optional_runtime",
            "category": "test",
            "repo": "https://github.com/example/demo",
            "detect": {
                "python_modules": ["demo_mod"],
                "python_distributions": ["demo-dist"],
                "commands": [],
            },
        }
        with (
            patch.object(discover.importlib.util, "find_spec", return_value=object()),
            patch.object(discover.importlib.metadata, "packages_distributions", return_value={"demo_mod": ["auto-dist"]}),
            patch.object(discover.importlib.metadata, "version", side_effect=lambda name: {"demo-dist": "1.2.3", "auto-dist": "9.9.9"}[name]),
        ):
            result = discover.probe_backend(entry)
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["detected_version"], "1.2.3")
        self.assertEqual(result["version_source"], "python_distribution:demo-dist")
        self.assertEqual(result["python_versions"]["auto-dist"], "9.9.9")

    def test_command_only_detection_does_not_execute_command_for_version(self):
        entry = {
            "id": "cli",
            "adoption": "borrow_pattern",
            "category": "test",
            "repo": "https://github.com/example/cli",
            "detect": {"python_modules": [], "commands": ["demo-cli"]},
        }
        with (
            patch.object(discover.shutil, "which", return_value="/usr/bin/demo-cli"),
            patch.object(discover.importlib.metadata, "packages_distributions", return_value={}),
        ):
            result = discover.probe_backend(entry)
        self.assertEqual(result["status"], "available")
        self.assertIsNone(result["detected_version"])
        self.assertIsNone(result["version_source"])

    def test_metadata_errors_are_bounded(self):
        entry = {
            "id": "demo",
            "adoption": "optional_runtime",
            "category": "test",
            "repo": "https://github.com/example/demo",
            "detect": {
                "python_modules": ["demo_mod"],
                "python_distributions": ["demo-dist"],
                "commands": [],
            },
        }
        with (
            patch.object(discover.importlib.util, "find_spec", return_value=object()),
            patch.object(discover.importlib.metadata, "packages_distributions", side_effect=RuntimeError("broken metadata")),
            patch.object(discover.importlib.metadata, "version", side_effect=RuntimeError("broken version")),
        ):
            result = discover.probe_backend(entry)
        self.assertEqual(result["status"], "available")
        self.assertIsNone(result["detected_version"])
        self.assertEqual(result["python_versions"], {})


if __name__ == "__main__":
    unittest.main()
