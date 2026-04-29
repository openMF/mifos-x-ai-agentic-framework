import pytest
from src.risk_scorer.risk_assessment import RiskAssessmentEngine


@pytest.fixture
def risk_engine():
    return RiskAssessmentEngine()


def create_mock_account(arrears_days=0, repaid=100, expected=100):
    """Create a mock account for testing"""
    return {
        "id": 1,
        "status": {
            "value": "Active (in arrears)" if arrears_days > 0 else "Active"
        },
        "daysInArrears": arrears_days,
        "disbursementDate": "2023-01-01",
        "principalDisbursed": 1000,
        "principalRepaid": 900 if arrears_days > 0 else expected,
        "summary": {
            "totalRepaid": repaid,
            "totalExpectedRepayment": expected
        }
    }


def test_low_risk_account(risk_engine):
    """Test low-risk account scoring"""
    account = create_mock_account(arrears_days=0, repaid=100, expected=100)
    score, level, factors = risk_engine.calculate_risk_score(account)
    assert 0 <= score <= 1
    assert level == "LOW"


def test_high_risk_account(risk_engine):
    """Test high-risk account scoring"""
    account = create_mock_account(arrears_days=120, repaid=50, expected=100)
    score, level, factors = risk_engine.calculate_risk_score(account)
    assert level == "HIGH"
    assert score > 0.7


def test_medium_risk_account(risk_engine):
    """Test medium-risk account scoring"""
    account = create_mock_account(arrears_days=45, repaid=70, expected=100)
    score, level, factors = risk_engine.calculate_risk_score(account)
    assert level == "MEDIUM"
    assert 0.4 <= score < 0.7


def test_risk_factors_included(risk_engine):
    """Test that all risk factors are calculated"""
    account = create_mock_account()
    score, level, factors = risk_engine.calculate_risk_score(account)

    assert "arrears_days" in factors
    assert "repayment_rate" in factors
    assert "account_age" in factors
    assert "loan_ratio" in factors
    assert "missed_payments" in factors


def test_arrears_normalization(risk_engine):
    """Test arrears normalization"""
    assert risk_engine._normalize_arrears(0) == 0
    assert risk_engine._normalize_arrears(180) == 1.0
    assert 0 < risk_engine._normalize_arrears(90) < 1


def test_account_age_normalization(risk_engine):
    """Test newer accounts are riskier"""
    new_account = risk_engine._normalize_account_age(3)
    old_account = risk_engine._normalize_account_age(24)
    assert new_account > old_account


if __name__ == "__main__":
    pytest.main([__file__])
