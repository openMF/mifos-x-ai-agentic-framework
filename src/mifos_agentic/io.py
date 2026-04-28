"""Input/output helpers for local portfolio samples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mifos_agentic.models import LoanAccount


def load_accounts(path: Path) -> list[LoanAccount]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        records = payload.get("loans", [])
    else:
        records = payload
    if not isinstance(records, list):
        raise ValueError("Expected a list of loan account records.")
    return [_loan_from_record(record) for record in records]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _loan_from_record(record: dict[str, Any]) -> LoanAccount:
    return LoanAccount(
        loan_id=str(record["loan_id"]),
        client_id=str(record["client_id"]),
        principal_outstanding=float(record.get("principal_outstanding", 0)),
        total_due=float(record.get("total_due", 0)),
        total_paid=float(record.get("total_paid", 0)),
        days_overdue=int(record.get("days_overdue", 0)),
        missed_installments=int(record.get("missed_installments", 0)),
        last_payment_days_ago=int(record.get("last_payment_days_ago", 0)),
        officer_id=record.get("officer_id"),
        metadata={key: value for key, value in record.items() if key not in _KNOWN_FIELDS},
    )


_KNOWN_FIELDS = {
    "loan_id",
    "client_id",
    "principal_outstanding",
    "total_due",
    "total_paid",
    "days_overdue",
    "missed_installments",
    "last_payment_days_ago",
    "officer_id",
}
