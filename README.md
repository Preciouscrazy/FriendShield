# FriendShield

An **offline, privacy-conscious friend-request review and evaluation prototype** for games.

FriendShield scores synthetic or user-authorized request metadata using explainable rules, and optionally evaluates review decisions against **explicitly labeled examples**. It does **not** access Riot accounts, block requests, scrape friend lists, call game APIs, or reliably identify bots. Not affiliated with Riot Games.

## Quick start

Requires Python 3.10+; standard library only at runtime.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m friendshield --input examples/requests.csv --output review.json
python -m friendshield --evaluate examples/labeled_requests.csv --threshold 60 --output evaluation-report.json
```

Review input columns: `request_id,account_age_days,requests_last_hour,mutual_friends,profile_complete,reported_before`. Boolean columns accept `true/false` or `1/0`. Evaluation CSV adds `expected_review`, which is a **hypothetical advisory-review label**, not a bot/non-bot label. No usernames or message bodies are needed.

## Evaluation

`--evaluate` measures the existing rules' predictions (`score >= --threshold`) against supplied labels. Default threshold is 60, matching the `review` score band. `caution` remains a separate descriptive score label, not a positive prediction at threshold 60.

The report contains a confusion matrix, precision, recall, specificity, accuracy, F1, false-positive rate, false-negative rate, and auditable per-request decisions. Rates with zero denominators are JSON `null`, not fabricated zeros.

**Synthetic fixture at threshold 60** (12 fabricated requests; 6 labeled for review): TP 4, FP 2, TN 4, FN 2. Precision and recall are both 66.7%; FPR and FNR are both 33.3%. These are test-fixture measurements, **not real-world performance estimates**. See [evaluation guide](docs/evaluation.md).

## Scoring and safety

Rules consider account age, request volume, profile completeness, prior-report indicator, and mutual connections. `review`, `caution`, and `low_signal` are advisory categories only. Human review is required before any action. Poor quality or imbalanced labels can mislead metrics; real-world deployment requires permission, careful validation, privacy protections, and false-positive impact analysis.

## Development

GitHub Actions tests Python 3.10, 3.11, and 3.12, and checks a generated JSON evaluation report. MIT licensed.
