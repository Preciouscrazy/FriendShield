import csv

REQUIRED = {"request_id", "account_age_days", "requests_last_hour",
            "mutual_friends", "profile_complete", "reported_before"}

def _boolean(value):
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise ValueError("expected true/false or 1/0")

def load_requests(path):
    records = []
    seen = set()
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("missing required CSV columns")
        for line, row in enumerate(reader, start=2):
            try:
                rid = row["request_id"]
                if not rid or rid in seen:
                    raise ValueError("empty or duplicate request_id")
                age = int(row["account_age_days"])
                velocity = int(row["requests_last_hour"])
                mutual = int(row["mutual_friends"])
                if min(age, velocity, mutual) < 0:
                    raise ValueError("negative numeric field")
                complete = _boolean(row["profile_complete"])
                reported = _boolean(row["reported_before"])
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f"{path}:{line}: {exc}") from exc
            seen.add(rid)
            records.append({"request_id": rid, "account_age_days": age,
                            "requests_last_hour": velocity, "mutual_friends": mutual,
                            "profile_complete": complete, "reported_before": reported})
    return records

def score_one(record):
    score = 0
    reasons = []
    def add(points, explanation):
        nonlocal score
        score += points
        reasons.append(explanation)
    if record["account_age_days"] < 7:
        add(25, "new account")
    if record["requests_last_hour"] >= 20:
        add(35, "high recent request volume")
    elif record["requests_last_hour"] >= 8:
        add(15, "elevated recent request volume")
    if not record["profile_complete"]:
        add(15, "incomplete profile")
    if record["reported_before"]:
        add(30, "prior report indicator")
    if record["mutual_friends"] >= 2:
        score -= 10
        reasons.append("mutual connections reduce score")
    score = max(0, min(100, score))
    label = "review" if score >= 60 else "caution" if score >= 30 else "low_signal"
    return {"request_id": record["request_id"], "score": score,
            "label": label, "reasons": reasons}

def score_requests(records):
    items = sorted((score_one(record) for record in records),
                   key=lambda item: (-item["score"], item["request_id"]))
    return {"requests": items, "policy": "Advisory only; human review required. Scores are not proof of bot activity."}
