import argparse
import json

from .core import load_requests, score_requests
from .evaluation import evaluate_labeled_requests, load_labeled_requests


def main():
    parser = argparse.ArgumentParser(description="Offline explainable friend-request review and evaluation")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", help="Unlabeled request metadata CSV")
    mode.add_argument("--evaluate", help="Labeled CSV with expected_review column")
    parser.add_argument("--output", help="Output JSON path (default depends on mode)")
    parser.add_argument("--threshold", type=int, default=60,
                        help="Evaluation-only review threshold, integer 0-100 (default: 60)")
    args = parser.parse_args()
    try:
        if args.evaluate:
            report = evaluate_labeled_requests(
                load_labeled_requests(args.evaluate), threshold=args.threshold
            )
            output_path = args.output or "evaluation-report.json"
        else:
            if args.threshold != 60:
                raise ValueError("--threshold is only meaningful with --evaluate")
            report = score_requests(load_requests(args.input))
            output_path = args.output or "review.json"
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
