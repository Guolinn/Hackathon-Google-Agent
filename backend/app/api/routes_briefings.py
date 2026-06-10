from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.briefing_service import BriefingService

router = APIRouter(tags=["briefings"])


class GenerateBriefingRequest(BaseModel):
    incident_id: str
    plan_id: str | None = None
    audience: str = "mayor"


@router.post("/briefings/generate")
def generate_briefing(payload: GenerateBriefingRequest, repository=Depends(get_repository)) -> dict:
    service = BriefingService(repository)
    data, mode = service.generate(payload.incident_id, payload.audience, payload.plan_id)
    return envelope(data, data_mode_used=mode)
