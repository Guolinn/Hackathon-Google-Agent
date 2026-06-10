from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository
from app.services.state_store import get_store
from app.services.time_utils import utc_now_iso


class ApprovalService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.store = get_store()

    def create_approval(self, approval: dict[str, Any]) -> dict[str, Any]:
        self.store.approvals[approval["approval_id"]] = approval
        return approval

    def approve(
        self,
        approval_id: str,
        approver_name: str,
        approver_role: str,
        notes: str | None = None,
    ) -> tuple[dict[str, Any], str]:
        approval = self._get(approval_id)
        approval.update(
            {
                "status": "approved",
                "approved_at": utc_now_iso(),
                "approver_name": approver_name,
                "approver_role": approver_role,
                "notes": notes,
                "next_action": "dispatch_request_ready",
            }
        )
        return approval, self.repository.table("approval_requests").mode_used

    def reject(
        self,
        approval_id: str,
        approver_name: str,
        approver_role: str,
        notes: str | None = None,
    ) -> tuple[dict[str, Any], str]:
        approval = self._get(approval_id)
        approval.update(
            {
                "status": "rejected",
                "rejected_at": utc_now_iso(),
                "approver_name": approver_name,
                "approver_role": approver_role,
                "notes": notes,
                "next_action": "backup_required",
            }
        )
        return approval, "mock"

    def request_changes(
        self,
        approval_id: str,
        approver_name: str,
        approver_role: str,
        requested_changes: str,
        notes: str | None = None,
    ) -> tuple[dict[str, Any], str]:
        approval = self._get(approval_id)
        approval.update(
            {
                "status": "changes_requested",
                "reviewed_at": utc_now_iso(),
                "approver_name": approver_name,
                "approver_role": approver_role,
                "requested_changes": requested_changes,
                "notes": notes,
                "next_action": "revise_dispatch_plan",
            }
        )
        return approval, "mock"

    def _get(self, approval_id: str) -> dict[str, Any]:
        approval = self.store.approvals.get(approval_id)
        if approval is None:
            raise KeyError(f"Approval {approval_id} not found. Generate a dispatch plan first.")
        return approval
