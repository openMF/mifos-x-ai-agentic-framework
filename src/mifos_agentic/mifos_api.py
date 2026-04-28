"""Minimal Mifos X API adapter.

The prototype can run fully offline with JSON input. This adapter defines the
integration boundary for live Mifos X data without forcing network access in
tests or local demos.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from mifos_agentic.models import LoanAccount


@dataclass(frozen=True)
class MifosApiClient:
    base_url: str
    tenant_id: str = "default"
    auth_token: str | None = None

    def get_loan(self, loan_id: str) -> dict[str, Any]:
        return self._get_json(f"/loans/{urllib.parse.quote(loan_id)}")

    def to_account(self, loan_payload: dict[str, Any]) -> LoanAccount:
        summary = loan_payload.get("summary", {})
        timeline = loan_payload.get("timeline", {})
        status = loan_payload.get("status", {})
        return LoanAccount(
            loan_id=str(loan_payload.get("id") or loan_payload.get("accountNo")),
            client_id=str(loan_payload.get("clientId") or loan_payload.get("clientName")),
            principal_outstanding=float(summary.get("principalOutstanding") or 0),
            total_due=float(summary.get("totalOverdue") or summary.get("totalDue") or 0),
            total_paid=float(summary.get("totalRepayment") or 0),
            days_overdue=int(summary.get("daysInArrears") or 0),
            missed_installments=int(summary.get("missedRepayments") or 0),
            last_payment_days_ago=int(timeline.get("daysSinceLastRepayment") or 0),
            officer_id=str(loan_payload.get("loanOfficerId") or ""),
            metadata={"status": status.get("value")},
        )

    def _get_json(self, path: str) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + path
        request = urllib.request.Request(url)
        request.add_header("Fineract-Platform-TenantId", self.tenant_id)
        request.add_header("Accept", "application/json")
        if self.auth_token:
            request.add_header("Authorization", f"Bearer {self.auth_token}")
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
