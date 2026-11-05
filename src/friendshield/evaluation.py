"""Measure advisory review decisions against explicitly labeled offline examples.

An expected_review value is a scenario label, never proof of bot activity.
"""
import csv

from .core import load_requests, score_one


def load_labeled_requests(path):
    """Load and validate normal metadata plus an expected_review column."""
    records = load_requests(path)
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "expected_review" not in reader.fieldnames:
            raise ValueError("missing required CSV column: expected_review")
        labels = []
        for line, row in enumerate(reader, start=2):
            raw = row.get("expected_review")
            if not isinstance(raw, str) or raw.strip().lower() not in {"true", "false", "1", "0"}:
                raise ValueError(f"{path}:{line}: expected_review must be true/false or 1/0")
            labels.append(raw.strip().lower() in {"true", "1"})
    if len(labels) != len(records):
        raise ValueError("labeled record count does not match validated requests")
    return list(zip(records, labels))


def _ratio(numerator, denominator):
    """Return null for undefined rates rather than hiding missing classes as zero."""
    return numerator / denominator if denominator else None


def evaluate_labeled_requests(labeled_records, threshold=60):
    """Evaluate score >= threshold as a positive advisory-review decision.

    This is a retrospective comparison to supplied labels, not a bot classifier
    accuracy guarantee. The original FriendShield scoring rules are unchanged.
    """
    if type(threshold) is not int or not 0 <= threshold <= 100:
        raise ValueError("threshold must be an integer from 0 to 100")
    if not labeled_records:
        raise ValueError("no labeled requests to evaluate")

    matrix = {
        "true_positive": 0,
        "false_positive": 0,
        "true_negative": 0,
        "false_negative": 0,
    }
    decisions = []
    seen = set()
    for record, expected_review in labeled_records:
        if type(expected_review) is not bool:
            raise ValueError("expected_review must be a boolean")
        rid = record["request_id"]
        if not isinstance(rid, str) or not rid or rid in seen:
            raise ValueError("empty or duplicate request_id")
        seen.add(rid)
        result = score_one(record)
        predicted_review = result["score"] >= threshold
        if predicted_review:
            outcome = "true_positive" if expected_review else "false_positive"
        else:
            outcome = "false_negative" if expected_review else "true_negative"
        matrix[outcome] += 1
        decisions.append({
            "request_id": rid,
            "expected_review": expected_review,
            "predicted_review": predicted_review,
            "score": result["score"],
            "score_label": result["label"],
            "outcome": outcome,
            "reasons": result["reasons"],
        })
    tp = matrix["true_positive"]
    fp = matrix["false_positive"]
    tn = matrix["true_negative"]
    fn = matrix["false_negative"]
    return {
        "mode": "offline_labeled_evaluation",
        "sample_count": len(decisions),
        "threshold": threshold,
        "positive_label": "expected_review",
        "prediction_rule": "score >= threshold",
        "confusion_matrix": matrix,
        "metrics": {
            "precision": _ratio(tp, tp + fp),
            "recall": _ratio(tp, tp + fn),
            "false_positive_rate": _ratio(fp, fp + tn),
            "false_negative_rate": _ratio(fn, fn + tp),
            "specificity": _ratio(tn, tn + fp),
            "accuracy": (tp + tn) / len(decisions),
            "f1": _ratio(2 * tp, 2 * tp + fp + fn),
        },
        "decisions": decisions,
        "limitations": (
            "Labels are scenario annotations, not verified bot identities. "
            "Metrics describe only the supplied labeled sample and do not "
            "estimate real-world error rates. Advisory review only; no blocking."
        ),
    }
