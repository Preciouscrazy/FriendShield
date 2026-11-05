import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from friendshield.dashboard import build_dashboard_data, render_dashboard, save_dashboard
from friendshield.evaluation import evaluate_labeled_requests, load_labeled_requests


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labeled = load_labeled_requests(ROOT / "examples" / "labeled_requests.csv")

    def test_101_thresholds_and_labeled_counts(self):
        data = build_dashboard_data(self.labeled)
        self.assertEqual([r["threshold"] for r in data["thresholds"]], list(range(101)))
        self.assertEqual((data["sample_count"], data["positive_count"], data["routine_count"]), (12, 6, 6))

    def test_default_matches_existing_evaluation(self):
        row = build_dashboard_data(self.labeled)["thresholds"][60]
        report = evaluate_labeled_requests(self.labeled, threshold=60)
        self.assertEqual(row["metrics"], report["metrics"])
        self.assertEqual(row["confusion_matrix"], report["confusion_matrix"])

    def test_edge_thresholds_and_missing_precision(self):
        data = build_dashboard_data(self.labeled)
        self.assertEqual(data["thresholds"][0]["confusion_matrix"]["false_negative"], 0)
        self.assertEqual(data["thresholds"][100]["confusion_matrix"]["false_positive"], 0)
        only_routine = [(self.labeled[7][0], False)]
        self.assertIsNone(build_dashboard_data(only_routine)["thresholds"][100]["metrics"]["precision"])

    def test_html_is_offline_and_has_slider(self):
        html = render_dashboard(self.labeled, initial_threshold=47)
        self.assertIn('id="threshold"', html)
        self.assertIn('value="47"', html)
        self.assertIn('id="chart"', html)
        self.assertIn('False positives', html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("https://", html)
        match = re.search(r'<script id="evaluation-data" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(match)
        payload = json.loads(match.group(1))
        self.assertEqual(payload["thresholds"][60]["confusion_matrix"]["true_positive"], 4)

    def test_invalid_threshold_and_empty_sample(self):
        for threshold in (-1, 101, True, 5.5, "60"):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                render_dashboard(self.labeled, initial_threshold=threshold)
        with self.assertRaises(ValueError):
            build_dashboard_data([])

    def test_write_utf8_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "dashboard.html"
            self.assertEqual(save_dashboard(self.labeled, path), path)
            self.assertIn("Evaluation Lab", path.read_text(encoding="utf-8"))

    def cli(self, *args):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.run([sys.executable, "-m", "friendshield", *map(str, args)],
                              cwd=ROOT, env=env, text=True, capture_output=True, check=False)

    def test_cli_produces_html_and_json(self):
        with tempfile.TemporaryDirectory() as folder:
            json_path = Path(folder) / "report.json"
            html_path = Path(folder) / "report.html"
            result = self.cli("--evaluate", ROOT / "examples" / "labeled_requests.csv",
                              "--threshold", 70, "--output", json_path, "--dashboard", html_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(json_path.read_text())["threshold"], 70)
            self.assertIn('value="70"', html_path.read_text(encoding="utf-8"))

    def test_cli_rejects_dashboard_without_evaluation(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.cli("--input", ROOT / "examples" / "requests.csv",
                              "--dashboard", Path(folder) / "wrong.html")
            self.assertEqual(result.returncode, 2)
            self.assertIn("require --evaluate", result.stderr)

    def test_cli_rejects_identical_html_and_json_path(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "same.html"
            result = self.cli("--evaluate", ROOT / "examples" / "labeled_requests.csv",
                              "--output", output, "--dashboard", output)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
