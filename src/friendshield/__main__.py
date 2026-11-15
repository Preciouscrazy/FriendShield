import argparse
import json
from pathlib import Path

from .core import load_requests, score_requests
from .dashboard import save_dashboard
from .evaluation import evaluate_labeled_requests, load_labeled_requests


def _same_file(left, right):
    """Reject both matching paths and existing hard-link aliases."""
    source, target = Path(left), Path(right)
    return source.resolve() == target.resolve() or (
        source.exists() and target.exists() and source.samefile(target)
    )


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
        input_path = args.evaluate or args.input
        output_path = args.output or ("evaluation-report.json" if args.evaluate else "review.json")
        if _same_file(input_path, output_path):
            raise ValueError("JSON report must not overwrite input CSV")
        if args.dashboard:
            if _same_file(input_path, args.dashboard):
                raise ValueError("dashboard must not overwrite input CSV")
            if _same_file(output_path, args.dashboard):
                raise ValueError("JSON report and dashboard must use different paths")
        if args.evaluate:
            labeled = load_labeled_requests(args.evaluate)
            report = evaluate_labeled_requests(labeled, threshold=args.threshold)
        else:
            if args.threshold != 60 or args.dashboard:
                raise ValueError("--threshold and --dashboard require --evaluate")
            report = score_requests(load_requests(args.input))
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
