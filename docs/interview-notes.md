# FriendShield interview notes

## Explain the project

FriendShield is an offline prototype that scores synthetic friend-request metadata and creates an advisory review report. Its evaluation mode compares scores against hypothetical human-review annotations and generates a standalone threshold dashboard.

## Explain one design choice

The score includes explanations, and the tool presents results for human review. It does not automatically block requests. This makes the rule-based behavior inspectable while keeping decisions with a person.

## Explain a limitation

At threshold 60, the small 12-row synthetic fixture has two false positives and two false negatives. Its labels are constructed review scenarios, not verified bot identities, so these rates are fixture-specific and do not measure real-world detection.

## A next improvement

Evaluate on a larger, representative, permissioned dataset with carefully reviewed labels. Track the cost of false positives and false negatives before considering changes to the threshold or scoring rules.

## Evidence to open

- `evidence/sample-evaluation.json`
- `evidence/sample-dashboard.html`
- `docs/evaluation.md`
