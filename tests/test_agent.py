from mifos_agentic.agent import PortfolioHealthAgent
from mifos_agentic.models import LoanAccount
from mifos_agentic.policy import AutonomyPolicy
from mifos_agentic.risk import assess_risk


def test_risk_scoring_flags_critical_account():
    account = LoanAccount(
        loan_id="loan-1",
        client_id="client-1",
        principal_outstanding=10000,
        total_due=5000,
        total_paid=500,
        days_overdue=75,
        missed_installments=4,
        last_payment_days_ago=60,
    )

    risk = assess_risk(account)

    assert risk.band == "critical"
    assert risk.score == 100
    assert "days_overdue" in risk.feature_contributions


def test_agent_escalates_high_risk_accounts():
    agent = PortfolioHealthAgent()
    decisions = agent.evaluate(
        [
            LoanAccount(
                loan_id="loan-1",
                client_id="client-1",
                principal_outstanding=10000,
                total_due=5000,
                total_paid=500,
                days_overdue=75,
                missed_installments=4,
                last_payment_days_ago=60,
                officer_id="officer-1",
            )
        ]
    )

    assert decisions[0]["risk"]["band"] == "critical"
    assert decisions[0]["action"]["action_type"] == "escalate_to_officer"
    assert decisions[0]["audit"]["human_review_required"] is False


def test_bounded_execute_allows_low_risk_reminder_without_approval():
    agent = PortfolioHealthAgent(AutonomyPolicy(autonomy_level="bounded_execute"))
    decisions = agent.evaluate(
        [
            LoanAccount(
                loan_id="loan-2",
                client_id="client-2",
                principal_outstanding=10000,
                total_due=100,
                total_paid=5000,
                days_overdue=3,
                missed_installments=0,
                last_payment_days_ago=9,
            )
        ]
    )

    assert decisions[0]["action"]["action_type"] == "send_reminder"
    assert decisions[0]["action"]["requires_human_approval"] is False
