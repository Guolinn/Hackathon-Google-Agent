from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository
from app.services.normalization import normalize_resource
from app.services.ranking_service import RankingService
from app.services.routing_service import RoutingService


class SupplierService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.routing = RoutingService(repository)
        self.ranking = RankingService()

    def search(self, resource: str, quantity: int, destination: str) -> tuple[dict[str, Any], str]:
        resource_name = normalize_resource(resource)
        suppliers = self.repository.table("suppliers")
        inventory = self.repository.table("supplier_inventory")
        supplier_by_id = {item["supplier_id"]: item for item in suppliers.records}
        modes = [suppliers.mode_used, inventory.mode_used]

        candidates = []
        for item in inventory.records:
            if normalize_resource(item.get("item_name", "")) != resource_name:
                continue
            supplier = supplier_by_id.get(item["supplier_id"])
            if not supplier:
                continue
            route, route_mode = self.routing.route(supplier["supplier_id"], destination)
            modes.append(route_mode)
            route = route or {}
            candidate = {
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["name"],
                "supplier_type": supplier["type"],
                "available": item["quantity_available"],
                "unit": item.get("unit"),
                "eta_min": route.get("current_eta_min", supplier.get("emergency_sla_min", 999)),
                "route": route.get("route_name", "Route pending operations confirmation"),
                "route_risk": route.get("route_risk", "Unknown"),
                "contract_status": supplier.get("contract_status", "unknown"),
                "integration_type": supplier.get("integration_type", "unknown"),
                "earliest_pickup_min": item.get("earliest_pickup_min"),
                "status": supplier.get("status"),
                "primary_contact": supplier.get("primary_contact"),
            }
            candidate["score"] = self.ranking.score_candidate(candidate, quantity)
            candidates.append(candidate)

        candidates.sort(key=lambda item: item["score"], reverse=True)
        candidates = self.ranking.label_candidates(candidates)
        return {
            "resource": resource_name,
            "quantity_needed": quantity,
            "destination": destination,
            "candidates": candidates,
        }, DataRepository.combine_modes(*modes)
