import argparse
import json
import os

from .core import load_requests, score_requests
from .dashboard import save_dashboard
from .evaluation import evaluate_labeled_requests, load_labeled_requests


def main():
    parser = argparse.ArgumentParser(description="Offline friend-request review, evaluation and dashboard")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", help="Unlabeled request metadata CSV")
    mode.add_argument("--evaluate", help="Labeled CSV with expected_review column")
    parser.add_argument("--output", help="Output JSON path (default depends on mode)")
    parser.add_argument("--dashboard", help="Evaluation-only standalone HTML dashboard path")
    parser.add_argument("--threshold", type=int, default=60,
                        help="Evaluation review threshold, integer 0-100 (default: 60)")
    args = parser.parse_args()
    try:
        if args.evaluate:
            labeled = load_labeled_requests(args.evaluate)
            report = evaluate_labeled_requests(labeled, threshold=args.threshold)
            output_path = args.output or "evaluation-report.json"
            if args.dashboard and os.path.abspath(args.dashboard) == os.path.abspath(output_path):
                raise ValueError("JSON report and dashboard must use different paths")
        else:
            if args.threshold != 60 or args.dashboard:
                raise ValueError("--threshold and --dashboard require --evaluate")
            report = score_requests(load_requests(args.input))
            output_path = args.output or "review.json"
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
        if args.evaluate and args.dashboard:
            save_dashboard(labeled, args.dashboard, initial_threshold=args.threshold)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Saved {output_path}")
    if args.evaluate and args.dashboard:
        print(f"Saved {args.dashboard}")


if __name__ == "__main__":
    main()
