from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.dashboard_service import DashboardService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def get_dashboard(repository=Depends(get_repository)) -> dict:
    service = DashboardService(repository)
    data, mode = service.get_dashboard()
    return envelope(data, data_mode_used=mode)
