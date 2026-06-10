from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository
from app.services.state_store import get_store
from app.services.time_utils import utc_now_iso


class DispatchService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.store = get_store()

    def send_dispatch_request(
        self,
        approval_id: str,
        channel_override: str | None = None,
    ) -> tuple[dict[str, Any], str]:
        approval = self.store.approvals.get(approval_id)
        if approval is None:
            raise KeyError(f"Approval {approval_id} not found")
        if approval.get("status") != "approved":
            raise ValueError(f"Approval {approval_id} must be approved before dispatch")

        recommendation = approval["recommendation"]
        dispatch_request_id = f"EDR-{approval['incident_id'].split('INC-')[-1]}-{recommendation['action_id'].split('-')[-1]}"
        contact_method = channel_override or self._contact_method(recommendation)
        message = self._message(approval, recommendation)
        request = {
            "dispatch_request_id": dispatch_request_id,
            "approval_id": approval_id,
            "incident_id": approval["incident_id"],
            "plan_id": approval["plan_id"],
            "status": "accepted",
            "state_history": [
                {"state": "sent", "at": utc_now_iso()},
                {"state": "supplier_pending", "at": utc_now_iso()},
                {"state": "accepted", "at": utc_now_iso()},
            ],
            "supplier": recommendation.get("origin"),
            "destination": recommendation.get("destination"),
            "resource": recommendation.get("resource"),
            "quantity": recommendation.get("quantity"),
            "eta_min": recommendation.get("eta_min"),
            "contact_method": contact_method,
            "backup_method": "Email + SMS",
            "message": message,
            "supplier_confirmation": {
                "status": "accepted",
                "confirmed_quantity": recommendation.get("quantity"),
                "confirmed_eta_min": recommendation.get("eta_min"),
                "note": "Demo confirmation auto-accepted by simulated supplier endpoint.",
            },
        }
        self.store.dispatch_requests[dispatch_request_id] = request
        return request, "mock"

    def get_dispatch_request(self, dispatch_request_id: str) -> tuple[dict[str, Any], str]:
        request = self.store.dispatch_requests.get(dispatch_request_id)
        if request is None:
            raise KeyError(f"Dispatch request {dispatch_request_id} not found")
        return request, "mock"

    @staticmethod
    def _contact_method(recommendation: dict[str, Any]) -> str:
        if recommendation["type"] in {"patient_diversion", "logistics_standby"}:
            return "CrisisFlow Portal"
        if recommendation.get("origin") == "NorCal Oxygen":
            return "Email + SMS fallback"
        return "API"

    @staticmethod
    def _message(approval: dict[str, Any], recommendation: dict[str, Any]) -> str:
        return (
            f"Emergency Dispatch Request: Please release {recommendation.get('quantity')} "
            f"{recommendation.get('resource')} to {recommendation.get('destination')} under emergency authorization "
            f"{approval['approval_id']} for {approval['incident_id']}. Confirm availability and pickup readiness within 10 minutes."
        )
