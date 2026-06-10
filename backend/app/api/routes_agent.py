from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["agent"])


class AnalyzeIncidentRequest(BaseModel):
    incident_id: str
    use_gemini: bool = True
    check_data_freshness: bool = True


@router.post("/agent/analyze-incident")
def analyze_incident(payload: AnalyzeIncidentRequest, repository=Depends(get_repository)) -> dict:
    service = AnalysisService(repository)
    data, mode = service.analyze_incident(
        payload.incident_id,
        check_data_freshness=payload.check_data_freshness,
    )
    return envelope(data, data_mode_used=mode)
