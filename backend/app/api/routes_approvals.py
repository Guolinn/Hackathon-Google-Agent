from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.approval_service import ApprovalService

router = APIRouter(tags=["approvals"])


class ApprovalDecisionRequest(BaseModel):
    approver_name: str
    approver_role: str
    notes: str | None = None


class RequestChangesRequest(ApprovalDecisionRequest):
    requested_changes: str


@router.post("/approvals/{approval_id}/approve")
def approve_request(approval_id: str, payload: ApprovalDecisionRequest, repository=Depends(get_repository)) -> dict:
    service = ApprovalService(repository)
    try:
        data, mode = service.approve(approval_id, payload.approver_name, payload.approver_role, payload.notes)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return envelope(data, data_mode_used=mode)


@router.post("/approvals/{approval_id}/reject")
def reject_request(approval_id: str, payload: ApprovalDecisionRequest, repository=Depends(get_repository)) -> dict:
    service = ApprovalService(repository)
    try:
        data, mode = service.reject(approval_id, payload.approver_name, payload.approver_role, payload.notes)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return envelope(data, data_mode_used=mode)


@router.post("/approvals/{approval_id}/request-changes")
def request_changes(approval_id: str, payload: RequestChangesRequest, repository=Depends(get_repository)) -> dict:
    service = ApprovalService(repository)
    try:
        data, mode = service.request_changes(
            approval_id,
            payload.approver_name,
            payload.approver_role,
            payload.requested_changes,
            payload.notes,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return envelope(data, data_mode_used=mode)
