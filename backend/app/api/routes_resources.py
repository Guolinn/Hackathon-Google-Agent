from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.gap_service import GapService

router = APIRouter(tags=["resources"])


@router.get("/resource-gaps/{incident_id}")
def get_resource_gaps(incident_id: str, repository=Depends(get_repository)) -> dict:
    service = GapService(repository)
    data, mode = service.calculate_resource_gaps(incident_id)
    return envelope(data, data_mode_used=mode)
