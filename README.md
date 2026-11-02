# FriendShield

An offline, privacy-conscious suspicious friend-request triage prototype for games.

FriendShield ranks synthetic or user-authorized friend-request metadata using explainable rules and produces a review queue. It **does not** connect to Riot accounts, auto-reject requests, scrape friend lists, bypass platform protections, or identify actual bots with certainty.

## Quick start

Python 3.10+; standard library only.

```bash
python -m friendshield --input examples/requests.csv --output review.json
python -m unittest discover -s tests -v
```

CSV columns: `request_id,account_age_days,requests_last_hour,mutual_friends,profile_complete,reported_before`. `profile_complete` and `reported_before` accept `true`/`false` or `1`/`0`. No usernames, messages, or other personal identifiers are required.

## How it works

Rules score young accounts, unusually high request velocity, missing profile fields, and prior reports. Mutual friends slightly reduce the score. Results are labeled `review`, `caution`, or `low_signal` and include reasons. **Never use the score as proof of misconduct**. Human review is required before any action. Rule thresholds are illustrative and must be validated for false positives before deployment.

## Security and privacy

Process local CSV files only. No network calls, API credentials, automatic blocking, or retention service. Avoid collecting sensitive personal data. Only use data you have permission to process. Not affiliated with or endorsed by Riot Games.

## Development

Run `python -m unittest discover -s tests -v`. License: MIT.
