import argparse
import json
from .core import load_requests, score_requests

def main():
    parser = argparse.ArgumentParser(description="Generate an offline friend-request review queue")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="review.json")
    args = parser.parse_args()
    try:
        report = score_requests(load_requests(args.input))
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Saved {args.output}")

if __name__ == "__main__":
    main()
