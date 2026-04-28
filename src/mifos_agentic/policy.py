"""Human-in-the-loop autonomy policy."""

from __future__ import annotations

from dataclasses import dataclass

from mifos_agentic.models import AgentAction, LoanAccount, RiskAssessment


@dataclass(frozen=True)
class AutonomyPolicy:
    """Controls how far the agent may go without loan officer approval."""

    autonomy_level: str = "recommend_only"
    max_auto_reminder_risk_score: int = 35
    max_auto_followup_risk_score: int = 55

    def choose_action(self, account: LoanAccount, risk: RiskAssessment) -> AgentAction:
        if risk.band in {"critical", "high"}:
            return AgentAction(
                loan_id=account.loan_id,
                action_type="escalate_to_officer",
                autonomy_level=self.autonomy_level,
                requires_human_approval=False,
                explanation=_explain("Escalating to a loan officer", risk),
                payload={"officer_id": account.officer_id, "priority": risk.band},
            )

        if risk.band == "medium":
            return AgentAction(
                loan_id=account.loan_id,
                action_type="schedule_follow_up",
                autonomy_level=self.autonomy_level,
                requires_human_approval=not self._can_execute(risk.score, self.max_auto_followup_risk_score),
                explanation=_explain("Scheduling a follow-up", risk),
                payload={"client_id": account.client_id, "suggested_channel": "phone"},
            )

        if account.days_overdue > 0:
            return AgentAction(
                loan_id=account.loan_id,
                action_type="send_reminder",
                autonomy_level=self.autonomy_level,
                requires_human_approval=not self._can_execute(risk.score, self.max_auto_reminder_risk_score),
                explanation=_explain("Sending a repayment reminder", risk),
                payload={"client_id": account.client_id, "template": "gentle_repayment_reminder"},
            )

        return AgentAction(
            loan_id=account.loan_id,
            action_type="none",
            autonomy_level=self.autonomy_level,
            requires_human_approval=False,
            explanation=_explain("No action recommended", risk),
        )

    def _can_execute(self, score: int, threshold: int) -> bool:
        return self.autonomy_level == "bounded_execute" and score <= threshold


def _explain(prefix: str, risk: RiskAssessment) -> str:
    reasons = "; ".join(risk.reasons)
    return f"{prefix} because risk is {risk.band} ({risk.score}/100): {reasons}."
