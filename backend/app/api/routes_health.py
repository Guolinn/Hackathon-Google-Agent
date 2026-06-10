from __future__ import annotations

from fastapi import APIRouter

from app.api.response import envelope
from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return envelope(
        {
            "service": "crisisflow-backend",
            "status": "ok",
            "configured_data_mode": settings.data_mode,
            "gemini_configured": settings.use_gemini,
            "bigquery_configured": settings.use_bigquery,
            "fivetran_configured": settings.use_fivetran,
        },
        data_mode_used="mock",
    )
