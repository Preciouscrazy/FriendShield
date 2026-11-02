import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from friendshield.core import score_one, score_requests

class FriendShieldTests(unittest.TestCase):
    def test_high_signal(self):
        row = {"request_id": "r1", "account_age_days": 1, "requests_last_hour": 30,
               "mutual_friends": 0, "profile_complete": False, "reported_before": True}
        self.assertEqual(score_one(row)["label"], "review")

    def test_low_signal(self):
        row = {"request_id": "r2", "account_age_days": 500, "requests_last_hour": 1,
               "mutual_friends": 3, "profile_complete": True, "reported_before": False}
        self.assertEqual(score_one(row)["score"], 0)

    def test_order(self):
        a = {"request_id": "a", "account_age_days": 500, "requests_last_hour": 0,
             "mutual_friends": 0, "profile_complete": True, "reported_before": False}
        b = dict(a, request_id="b", reported_before=True)
        self.assertEqual(score_requests([a, b])["requests"][0]["request_id"], "b")

if __name__ == "__main__":
    unittest.main()
