from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository


class RoutingService:
    def __init__(self, repository: DataRepository):
        self.repository = repository

    def route(self, origin_id: str, destination_id: str) -> tuple[dict[str, Any] | None, str]:
        routes = self.repository.table("traffic_routes")
        route = next(
            (
                item
                for item in routes.records
                if item.get("origin_id") == origin_id and item.get("destination_id") == destination_id
            ),
            None,
        )
        return route, routes.mode_used
