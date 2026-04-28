"""Explainable baseline risk scoring for loan portfolios."""

from __future__ import annotations

from mifos_agentic.models import LoanAccount, RiskAssessment


def assess_risk(account: LoanAccount) -> RiskAssessment:
    """Score repayment risk from transparent, auditable rules.

    This is deliberately simple for the prototype. It gives mentors and loan
    officers a baseline to critique before replacing or augmenting it with ML.
    """

    contributions: dict[str, int] = {}
    reasons: list[str] = []

    if account.days_overdue >= 60:
        contributions["days_overdue"] = 45
        reasons.append("loan is overdue by 60+ days")
    elif account.days_overdue >= 30:
        contributions["days_overdue"] = 30
        reasons.append("loan is overdue by 30+ days")
    elif account.days_overdue >= 7:
        contributions["days_overdue"] = 12
        reasons.append("loan is overdue by at least a week")

    if account.missed_installments >= 3:
        contributions["missed_installments"] = 30
        reasons.append("three or more installments are missed")
    elif account.missed_installments == 2:
        contributions["missed_installments"] = 20
        reasons.append("two installments are missed")
    elif account.missed_installments == 1:
        contributions["missed_installments"] = 10
        reasons.append("one installment is missed")

    repayment_ratio = _repayment_ratio(account)
    if repayment_ratio < 0.25:
        contributions["repayment_ratio"] = 20
        reasons.append("repayment ratio is below 25%")
    elif repayment_ratio < 0.5:
        contributions["repayment_ratio"] = 12
        reasons.append("repayment ratio is below 50%")

    if account.last_payment_days_ago >= 45:
        contributions["payment_recency"] = 18
        reasons.append("no payment in 45+ days")
    elif account.last_payment_days_ago >= 21:
        contributions["payment_recency"] = 8
        reasons.append("no payment in 21+ days")

    score = min(100, sum(contributions.values()))
    return RiskAssessment(
        loan_id=account.loan_id,
        score=score,
        band=_risk_band(score),
        reasons=reasons or ["loan appears healthy under the current baseline rules"],
        feature_contributions=contributions,
    )


def _repayment_ratio(account: LoanAccount) -> float:
    total_expected = account.total_paid + account.total_due + account.principal_outstanding
    if total_expected <= 0:
        return 1.0
    return account.total_paid / total_expected


def _risk_band(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 25:
        return "medium"
    return "low"
