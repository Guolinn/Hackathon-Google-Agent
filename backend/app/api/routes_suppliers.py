from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_repository
from app.api.response import envelope
from app.services.supplier_service import SupplierService

router = APIRouter(tags=["suppliers"])


@router.get("/suppliers/search")
def search_suppliers(
    resource: str = Query(...),
    quantity: int = Query(..., ge=1),
    destination: str = Query(...),
    repository=Depends(get_repository),
) -> dict:
    service = SupplierService(repository)
    data, mode = service.search(resource, quantity, destination)
    return envelope(data, data_mode_used=mode)
