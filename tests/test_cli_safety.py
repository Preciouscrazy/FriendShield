"""Targeted CLI regression tests for output safety and synthetic report evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CliSafetyTests(unittest.TestCase):
    def run_cli(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "friendshield", *(str(a) for a in args)],
            cwd=ROOT, env=env, text=True, capture_output=True, check=False, timeout=30,
        )

    def copy_fixture(self, directory, name):
        source = ROOT / "examples" / name
        target = Path(directory) / name
        target.write_bytes(source.read_bytes())
        return target

    def test_golden_synthetic_evaluation_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "evaluation.json"
            result = self.run_cli("--evaluate", ROOT / "examples/labeled_requests.csv",
                                  "--threshold", 60, "--output", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            golden = json.loads((ROOT / "evidence/sample-evaluation.json").read_text(encoding="utf-8"))
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), golden)

    def test_review_json_cannot_overwrite_input_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.copy_fixture(tmp, "requests.csv")
            before = source.read_bytes()
            result = self.run_cli("--input", source, "--output", source)
            self.assertEqual(result.returncode, 2)
            self.assertIn("input CSV", result.stderr)
            self.assertEqual(source.read_bytes(), before)

    def test_evaluation_json_cannot_overwrite_input_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.copy_fixture(tmp, "labeled_requests.csv")
            before = source.read_bytes()
            result = self.run_cli("--evaluate", source, "--output", source)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_bytes(), before)

    def test_dashboard_cannot_overwrite_input_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.copy_fixture(tmp, "labeled_requests.csv")
            output = Path(tmp) / "report.json"
            before = source.read_bytes()
            result = self.run_cli("--evaluate", source, "--output", output,
                                  "--dashboard", source)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_bytes(), before)
            self.assertFalse(output.exists())

    def test_hardlink_to_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.copy_fixture(tmp, "requests.csv")
            alias = Path(tmp) / "alias.json"
            try:
                os.link(source, alias)
            except OSError as exc:
                self.skipTest(f"Hard links unavailable: {exc}")
            before = source.read_bytes()
            result = self.run_cli("--input", source, "--output", alias)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(source.read_bytes(), before)

    def test_hardlinked_json_and_dashboard_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.copy_fixture(tmp, "labeled_requests.csv")
            output, dashboard = Path(tmp) / "report.json", Path(tmp) / "dashboard.html"
            output.write_text("prior output", encoding="utf-8")
            try:
                os.link(output, dashboard)
            except OSError as exc:
                self.skipTest(f"Hard links unavailable: {exc}")
            result = self.run_cli("--evaluate", source, "--output", output,
                                  "--dashboard", dashboard)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(encoding="utf-8"), "prior output")
            self.assertEqual(dashboard.read_text(encoding="utf-8"), "prior output")


if __name__ == "__main__":
    unittest.main()
