from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.dispatch_plan_service import DispatchPlanService
from app.services.dispatch_service import DispatchService

router = APIRouter(tags=["dispatch"])


class GenerateDispatchPlanRequest(BaseModel):
    incident_id: str
    target_hospital_id: str = "HOSP-SFGH"
    include_briefing: bool = False
    include_ai_explanations: bool = False


class SendDispatchRequest(BaseModel):
    approval_id: str
    channel_override: str | None = None


@router.post("/dispatch-plans/generate")
def generate_dispatch_plan(payload: GenerateDispatchPlanRequest, repository=Depends(get_repository)) -> dict:
    service = DispatchPlanService(repository)
    data, mode = service.generate_plan(
        payload.incident_id,
        payload.target_hospital_id,
        include_ai_explanations=payload.include_ai_explanations,
        include_briefing=payload.include_briefing,
    )
    return envelope(data, data_mode_used=mode)


@router.post("/dispatch-requests/send")
def send_dispatch_request(payload: SendDispatchRequest, repository=Depends(get_repository)) -> dict:
    service = DispatchService(repository)
    try:
        data, mode = service.send_dispatch_request(payload.approval_id, payload.channel_override)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return envelope(data, data_mode_used=mode)


@router.get("/dispatch-requests/{dispatch_request_id}")
def get_dispatch_request(dispatch_request_id: str, repository=Depends(get_repository)) -> dict:
    service = DispatchService(repository)
    try:
        data, mode = service.get_dispatch_request(dispatch_request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return envelope(data, data_mode_used=mode)
