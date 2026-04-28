"""Domain models for the Portfolio Health Agent prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

RiskBand = Literal["low", "medium", "high", "critical"]
ActionType = Literal["none", "send_reminder", "schedule_follow_up", "escalate_to_officer"]


@dataclass(frozen=True)
class LoanAccount:
    """Minimal loan facts needed for explainable risk scoring."""

    loan_id: str
    client_id: str
    principal_outstanding: float
    total_due: float
    total_paid: float
    days_overdue: int
    missed_installments: int
    last_payment_days_ago: int
    officer_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RiskAssessment:
    """Risk score plus traceable feature contributions."""

    loan_id: str
    score: int
    band: RiskBand
    reasons: list[str]
    feature_contributions: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "loan_id": self.loan_id,
            "score": self.score,
            "band": self.band,
            "reasons": self.reasons,
            "feature_contributions": self.feature_contributions,
        }


@dataclass(frozen=True)
class AgentAction:
    """Policy-bound action proposed by the agent."""

    loan_id: str
    action_type: ActionType
    autonomy_level: str
    requires_human_approval: bool
    explanation: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "loan_id": self.loan_id,
            "action_type": self.action_type,
            "autonomy_level": self.autonomy_level,
            "requires_human_approval": self.requires_human_approval,
            "explanation": self.explanation,
            "payload": self.payload,
        }
