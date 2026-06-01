from __future__ import annotations

import argparse
import json

from .substrate import build_review_packet

DEFAULT_QUERY = (
    "Review semantic research ideas for a sandbox paper trial with strategy boundaries "
    "and human approval."
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the harness-agnostic memory substrate demo")
    parser.add_argument("--role", default="quant_strategy_reviewer")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    args = parser.parse_args()
    print(json.dumps(build_review_packet(args.role, args.query), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
