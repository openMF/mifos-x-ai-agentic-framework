"""CLI for the Portfolio Health Agent prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mifos_agentic.agent import PortfolioHealthAgent
from mifos_agentic.io import load_accounts, write_json
from mifos_agentic.policy import AutonomyPolicy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate Mifos loan portfolio health.")
    parser.add_argument("input", type=Path, help="JSON file containing loan records.")
    parser.add_argument("--out", type=Path, default=Path("out/portfolio_decisions.json"))
    parser.add_argument(
        "--autonomy-level",
        choices=["recommend_only", "bounded_execute"],
        default="recommend_only",
        help="Whether low-risk actions may be executed without approval.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    agent = PortfolioHealthAgent(AutonomyPolicy(autonomy_level=args.autonomy_level))
    decisions = agent.evaluate(load_accounts(args.input))
    write_json(args.out, {"decisions": decisions})
    print(json.dumps({"decision_count": len(decisions), "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
