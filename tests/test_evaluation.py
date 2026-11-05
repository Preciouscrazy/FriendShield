import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from friendshield.evaluation import evaluate_labeled_requests, load_labeled_requests

HEADER = (
    "request_id,account_age_days,requests_last_hour,mutual_friends,"
    "profile_complete,reported_before,expected_review\n"
)


class EvaluationTests(unittest.TestCase):
    def _csv(self, rows, header=HEADER):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "labeled.csv"
        path.write_text(header + rows, encoding="utf-8")
        return path

    @staticmethod
    def _routine(rid="routine"):
        return {
            "request_id": rid, "account_age_days": 100,
            "requests_last_hour": 0, "mutual_friends": 0,
            "profile_complete": True, "reported_before": False,
        }

    def test_sample_confusion_matrix_and_rates(self):
        labeled = load_labeled_requests(ROOT / "examples" / "labeled_requests.csv")
        result = evaluate_labeled_requests(labeled)
        self.assertEqual(result["sample_count"], 12)
        self.assertEqual(result["confusion_matrix"], {
            "true_positive": 4, "false_positive": 2,
            "true_negative": 4, "false_negative": 2,
        })
        metrics = result["metrics"]
        for metric in ("precision", "recall", "accuracy", "f1"):
            self.assertAlmostEqual(metrics[metric], 2 / 3)
        self.assertAlmostEqual(metrics["false_positive_rate"], 1 / 3)
        self.assertAlmostEqual(metrics["false_negative_rate"], 1 / 3)
        self.assertEqual(len(result["decisions"]), 12)

    def test_threshold_tradeoff(self):
        labeled = load_labeled_requests(ROOT / "examples" / "labeled_requests.csv")
        low = evaluate_labeled_requests(labeled, threshold=30)["confusion_matrix"]
        high = evaluate_labeled_requests(labeled, threshold=80)["confusion_matrix"]
        self.assertLess(low["false_negative"], high["false_negative"])
        self.assertGreater(low["false_positive"], high["false_positive"])

    def test_rates_undefined_when_class_absent(self):
        result = evaluate_labeled_requests([(self._routine(), False)])
        self.assertIsNone(result["metrics"]["precision"])
        self.assertIsNone(result["metrics"]["recall"])
        self.assertIsNone(result["metrics"]["false_negative_rate"])
        self.assertEqual(result["metrics"]["false_positive_rate"], 0.0)

    def test_invalid_thresholds_and_empty_dataset(self):
        for value in (-1, 101, 60.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluate_labeled_requests([(self._routine(), False)], value)
        with self.assertRaises(ValueError):
            evaluate_labeled_requests([])

    def test_labels_must_be_booleans(self):
        with self.assertRaises(ValueError):
            evaluate_labeled_requests([(self._routine(), 1)])

    def test_missing_label_column(self):
        csv_path = self._csv(
            "item,10,0,0,true,false\n",
            header=HEADER.replace(",expected_review", "")
        )
        with self.assertRaisesRegex(ValueError, "expected_review"):
            load_labeled_requests(csv_path)

    def test_invalid_label_rejected(self):
        csv_path = self._csv("item,10,0,0,true,false,maybe\n")
        with self.assertRaisesRegex(ValueError, "expected_review"):
            load_labeled_requests(csv_path)

    def test_duplicate_ids_and_invalid_metadata_rejected(self):
        duplicate = self._csv(
            "same,10,0,0,true,false,true\n"
            "same,20,1,0,true,false,false\n"
        )
        with self.assertRaises(ValueError):
            load_labeled_requests(duplicate)
        invalid = self._csv("item,-5,0,0,true,false,true\n")
        with self.assertRaises(ValueError):
            load_labeled_requests(invalid)

    def test_json_is_serializable_with_undefined_rates(self):
        result = evaluate_labeled_requests([(self._routine(), False)])
        document = json.dumps(result, allow_nan=False)
        self.assertIn('"precision": null', document)

    def _run_cli(self, *arguments):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "friendshield", *map(str, arguments)],
            cwd=ROOT, env=environment, capture_output=True, text=True, check=False
        )

    def test_evaluation_cli_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation.json"
            finished = self._run_cli(
                "--evaluate", ROOT / "examples" / "labeled_requests.csv",
                "--threshold", "60", "--output", output,
            )
            self.assertEqual(finished.returncode, 0, finished.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["confusion_matrix"]["false_positive"], 2)

    def test_original_review_cli_still_works(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "review.json"
            finished = self._run_cli(
                "--input", ROOT / "examples" / "requests.csv", "--output", output
            )
            self.assertEqual(finished.returncode, 0, finished.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(report["requests"]), 3)


if __name__ == "__main__":
    unittest.main()
