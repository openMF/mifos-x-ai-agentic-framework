from typing import Dict, Any, Tuple
from datetime import datetime
from src.config import config

class RiskAssessmentEngine:
    def __init__(self):
        self.high_threshold = config.RISK_THRESHOLD_HIGH
        self.medium_threshold = config.RISK_THRESHOLD_MEDIUM

    def calculate_risk_score(self, account: Dict[str, Any]) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calculate risk score for a loan account (0-1 scale)
        Returns: (score, risk_level, factors)
        """
        factors = {}
        weights = {
            "arrears_days": 0.50,
            "repayment_rate": 0.25,
            "account_age": 0.10,
            "loan_amount_ratio": 0.10,
            "missed_payments": 0.05
        }

        # Parse account data
        arrears_days = self._calculate_arrears_days(account)
        repayment_rate = self._calculate_repayment_rate(account)
        account_age = self._calculate_account_age(account)
        loan_ratio = self._calculate_loan_amount_ratio(account)
        missed_payments = self._count_missed_payments(account)

        factors["arrears_days"] = arrears_days
        factors["repayment_rate"] = repayment_rate
        factors["account_age"] = account_age
        factors["loan_ratio"] = loan_ratio
        factors["missed_payments"] = missed_payments

        # Calculate weighted risk score
        score = (
            weights["arrears_days"] * self._normalize_arrears(arrears_days) +
            weights["repayment_rate"] * (1 - repayment_rate) +
            weights["account_age"] * self._normalize_account_age(account_age) +
            weights["loan_amount_ratio"] * self._normalize_loan_ratio(loan_ratio) +
            weights["missed_payments"] * self._normalize_missed_payments(missed_payments)
        )

        score = max(0, min(1, score))
        risk_level = self._classify_risk(score)

        return score, risk_level, factors

    def _calculate_arrears_days(self, account: Dict[str, Any]) -> int:
        """Calculate days overdue"""
        if "status" in account and account["status"]["value"] == "Active (in arrears)":
            arrears_days = account.get("daysInArrears", 0)
            return arrears_days
        return 0

    def _calculate_repayment_rate(self, account: Dict[str, Any]) -> float:
        """Calculate on-time repayment rate (0-1)"""
        summary = account.get("summary", {})
        total_repaid = summary.get("totalRepaid", 0)
        total_expected = summary.get("totalExpectedRepayment", 1)
        if total_expected == 0:
            return 1.0
        return min(1.0, total_repaid / total_expected)

    def _calculate_account_age(self, account: Dict[str, Any]) -> int:
        """Calculate account age in months"""
        disbursal_date = account.get("disbursementDate")
        if not disbursal_date:
            return 0
        try:
            disbursal = datetime.strptime(disbursal_date, "%Y-%m-%d")
            return (datetime.now() - disbursal).days // 30
        except:
            return 0

    def _calculate_loan_amount_ratio(self, account: Dict[str, Any]) -> float:
        """Calculate ratio of principal remaining to original amount"""
        principal_outstanding = account.get("principalDisbursed", 0) - account.get("principalRepaid", 0)
        principal_disbursed = account.get("principalDisbursed", 1)
        if principal_disbursed == 0:
            return 0
        return principal_outstanding / principal_disbursed

    def _count_missed_payments(self, account: Dict[str, Any]) -> int:
        """Count number of missed payment events"""
        summary = account.get("summary", {})
        return summary.get("totalExpectedRepayment", 0) - summary.get("totalRepaid", 0)

    def _normalize_arrears(self, days: int) -> float:
        """Normalize arrears days to 0-1 scale"""
        if days == 0:
            return 0
        if days >= 120:
            return 1.0
        if days >= 60:
            return 0.85
        if days >= 30:
            return 0.6
        if days >= 15:
            return 0.3
        return days / 50

    def _normalize_account_age(self, months: int) -> float:
        """Newer accounts are riskier"""
        if months < 6:
            return 0.8
        if months < 12:
            return 0.5
        return 0.2

    def _normalize_loan_ratio(self, ratio: float) -> float:
        """Higher outstanding = higher risk"""
        return min(1.0, ratio)

    def _normalize_missed_payments(self, missed: int) -> float:
        """Normalize missed payments"""
        if missed == 0:
            return 0
        if missed > 10:
            return 1.0
        return min(1.0, missed / 10)

    def _classify_risk(self, score: float) -> str:
        """Classify risk level based on score"""
        if score >= self.high_threshold:
            return "HIGH"
        elif score >= self.medium_threshold:
            return "MEDIUM"
        return "LOW"
