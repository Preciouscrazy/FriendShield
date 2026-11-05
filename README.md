# FriendShield

An **offline, privacy-conscious friend-request review, evaluation, and visualization prototype** for games.

FriendShield assigns explainable advisory-review scores to synthetic or user-authorized metadata. It does **not** access Riot Games accounts, identify actual bots with certainty, auto-block requests, scrape lists, or use game APIs. Independent educational project; not affiliated with Riot Games.

## Quick start

Python 3.10+; standard library only.

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m friendshield --input examples/requests.csv --output review.json
python -m friendshield --evaluate examples/labeled_requests.csv --threshold 60 --output evaluation-report.json --dashboard evaluation-dashboard.html
```

Open **evaluation-dashboard.html** in any modern web browser. It is self-contained and works offline.

## Interactive dashboard

Move the threshold slider from 0–100 to compare **precision, recall, false-positive rate, F1**, and the confusion matrix. The curve chart and side-by-side threshold table are computed from the same labeled input used for the JSON evaluation. The default threshold of 60 matches FriendShield's existing “review” category. Undefined rates display **N/A**, not zero.

The included 12 synthetic scenarios (6 labeled review, 6 routine) give TP=4, FP=2, TN=4, FN=2 at threshold 60. Precision and recall are each **66.7%**; false-positive and false-negative rates are each **33.3%**. **These are fixture-specific outcomes, not measured bot detection rates**. The dashboard contains no external scripts, CDNs, or network requests.

See [evaluation methodology](docs/evaluation.md) and [dashboard guide](docs/dashboard.md) for labels, reproducibility, and limitations.

## Security and limitations

All input is local CSV. Metadata columns: `request_id,account_age_days,requests_last_hour,mutual_friends,profile_complete,reported_before`. Evaluation inputs add `expected_review`, a **hypothetical human-review annotation**, never a verified misconduct or bot label. Only process data you are authorized to use, avoid personal identifiers, and require human judgment before any action.

GitHub Actions runs tests on Python 3.10–3.12 and checks both JSON and standalone HTML dashboard generation. MIT licensed.
