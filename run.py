#!/usr/bin/env python
"""
Main entry point for Portfolio Health Agent
"""
import argparse
import sys
from src.config import config
from src.api.mifos_client import MifosClient
from src.agent.portfolio_agent import PortfolioHealthAgent
from src.dashboard.app import app
import json


def run_monitoring():
    """Run portfolio monitoring once"""
    print("Starting portfolio monitoring...")
    mifos_client = MifosClient(
        config.MIFOS_API_URL,
        config.MIFOS_USERNAME,
        config.MIFOS_PASSWORD
    )
    agent = PortfolioHealthAgent(mifos_client)

    portfolio = agent.monitor_portfolio()
    print(json.dumps(portfolio, indent=2))

    if portfolio.get("status") == "success":
        print(f"\n✓ Found {portfolio['high_risk_count']} high-risk accounts")
        print(f"✓ Found {portfolio['medium_risk_count']} medium-risk accounts")


def run_actions():
    """Process high-risk accounts and recommend actions"""
    print("Processing high-risk accounts...")
    mifos_client = MifosClient(
        config.MIFOS_API_URL,
        config.MIFOS_USERNAME,
        config.MIFOS_PASSWORD
    )
    agent = PortfolioHealthAgent(mifos_client)

    actions = agent.process_high_risk_accounts()
    print(json.dumps(actions, indent=2))
    print(f"\n✓ Generated {len(actions)} recommended actions")


def run_dashboard():
    """Start the Flask dashboard"""
    print(f"Starting dashboard on http://localhost:{config.FLASK_PORT}")
    print("Press Ctrl+C to stop")
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.DEBUG)


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio Health Agent for Mifos X"
    )
    parser.add_argument(
        "command",
        choices=["monitor", "actions", "dashboard"],
        help="Command to run"
    )
    parser.add_argument(
        "--mifos-url",
        help="Mifos X API URL",
        default=config.MIFOS_API_URL
    )

    args = parser.parse_args()

    if args.command == "monitor":
        run_monitoring()
    elif args.command == "actions":
        run_actions()
    elif args.command == "dashboard":
        run_dashboard()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown signal received")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
