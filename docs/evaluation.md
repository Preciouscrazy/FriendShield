# FriendShield — Synthetic Evaluation Protocol

## Purpose

Compare FriendShield's **offline advisory-review decision** to scenario labels in an example CSV. This evaluates the behavior of a fixed rules-based score, not its ability to identify real bot accounts. No game APIs, private accounts, or automated blocking are involved.

## Reproduce

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m friendshield --evaluate examples/labeled_requests.csv --threshold 60 --output evaluation-report.json
```

The review-only command remains supported:

```bash
python -m friendshield --input examples/requests.csv --output review.json
```

## Label meaning and threshold

`expected_review=true` means the *synthetic scenario* was annotated as deserving a human review, **not** that a real account was verified malicious. The positive decision is `score >= threshold`; default 60 corresponds to the original `review` label. At 60, the `caution` category does not count as a positive decision. Different thresholds are evaluation parameters; changing them does not alter FriendShield's scoring rules.

## Confusion matrix

| | Annotated review | Annotated routine |
|---|---:|---:|
| Predicted review | True positive (TP) | False positive (FP) |
| Predicted routine | False negative (FN) | True negative (TN) |

Metrics are calculated with standard definitions:

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- False-positive rate = FP / (FP + TN)
- False-negative rate = FN / (FN + TP)
- Specificity = TN / (TN + FP)
- Accuracy = (TP + TN) / all examples
- F1 = 2TP / (2TP + FP + FN)

Undefined denominators yield JSON `null`. Avoid comparing metrics across differently labeled or selected populations as though the samples were comparable.

## Reproducible sample result

The 12 explicitly fabricated example requests contain 6 annotated review and 6 annotated routine cases. With threshold 60:

| TP | FP | TN | FN | Precision | Recall | FPR | FNR | Accuracy | F1 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 2 | 4 | 2 | 66.7% | 66.7% | 33.3% | 33.3% | 66.7% | 66.7% |

Compare thresholds such as 30, 60, and 80. Lower thresholds typically increase recall while producing more false positives in this fixture, illustrating the tradeoff.

## Boundaries and further validation

The fixture deliberately includes false positives and false negatives. It is a small, constructed demonstration, **not a representative random sample** of friend requests. The labels are assumptions, not verified ground truth. The output should never be characterized as a measured bot detection rate or evidence of misconduct.

Before any use beyond an educational prototype, design consent-based annotation with clear labeling guidelines, evaluate inter-rater reliability, reserve a separate holdout dataset, report class prevalence and confidence intervals, test across relevant non-sensitive slices and time periods, quantify cost of false positives, protect data, and obtain permission for any integration. The tool never blocks or reports accounts.
