"""Portfolio Health Agent orchestration."""

from __future__ import annotations

from mifos_agentic.actions import ActionExecutor, ReviewQueue
from mifos_agentic.models import LoanAccount
from mifos_agentic.policy import AutonomyPolicy
from mifos_agentic.risk import assess_risk


class PortfolioHealthAgent:
    """Deterministic first-pass agent for auditable portfolio monitoring."""

    def __init__(self, policy: AutonomyPolicy | None = None) -> None:
        self.policy = policy or AutonomyPolicy()
        self.review_queue = ReviewQueue()
        self.executor = ActionExecutor()

    def evaluate(self, accounts: list[LoanAccount]) -> list[dict[str, object]]:
        """Evaluate accounts and return risk/action decisions."""

        decisions: list[dict[str, object]] = []
        for account in accounts:
            risk = assess_risk(account)
            action = self.policy.choose_action(account, risk)
            execution = (
                self.review_queue.add(action)
                if action.requires_human_approval
                else self.executor.execute(action)
            )
            decisions.append(
                {
                    "loan": {
                        "loan_id": account.loan_id,
                        "client_id": account.client_id,
                        "officer_id": account.officer_id,
                    },
                    "risk": risk.to_dict(),
                    "action": action.to_dict(),
                    "audit": {
                        "human_review_required": action.requires_human_approval,
                        "decision_basis": "transparent_rules_v0",
                        "execution": execution,
                    },
                }
            )
        return decisions
