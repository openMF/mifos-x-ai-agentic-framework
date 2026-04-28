"""Action review and execution primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from mifos_agentic.models import AgentAction


@dataclass
class ReviewQueue:
    """In-memory review queue for officer approval workflows."""

    items: list[dict[str, Any]] = field(default_factory=list)

    def add(self, action: AgentAction) -> dict[str, Any]:
        item = {
            "review_id": f"review-{len(self.items) + 1}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "action": action.to_dict(),
        }
        self.items.append(item)
        return item


class ActionExecutor:
    """Safe action executor that never bypasses required approval."""

    def __init__(self) -> None:
        self.executed: list[dict[str, Any]] = []

    def execute(self, action: AgentAction) -> dict[str, Any]:
        if action.requires_human_approval:
            return {"status": "queued_for_review", "action": action.to_dict()}
        record = {
            "status": "executed",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "action": action.to_dict(),
        }
        self.executed.append(record)
        return record
