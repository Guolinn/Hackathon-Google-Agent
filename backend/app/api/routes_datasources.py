from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.config import get_settings
from app.services.datasource_service import DatasourceService

router = APIRouter(tags=["data-sources"])


@router.get("/data-sources")
def get_data_sources(repository=Depends(get_repository)) -> dict:
    service = DatasourceService(repository, get_settings())
    data, mode = service.get_data_sources()
    return envelope(data, data_mode_used=mode)
