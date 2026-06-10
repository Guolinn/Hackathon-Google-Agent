from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository


class IncidentService:
    def __init__(self, repository: DataRepository):
        self.repository = repository

    def get_current_incident(self) -> tuple[dict[str, Any], str]:
        incidents = self.repository.table("incidents")
        incident = next((item for item in incidents.records if item.get("status") == "active"), None)
        if incident is None:
            incident = incidents.records[0] if incidents.records else {}
        return incident, incidents.mode_used

    def get_incident(self, incident_id: str) -> tuple[dict[str, Any], str]:
        incident, mode = self.repository.first("incidents", incident_id=incident_id)
        if incident is None:
            raise KeyError(f"Incident {incident_id} not found")
        return incident, mode

    def get_context(self, incident_id: str) -> tuple[dict[str, Any], str]:
        incident, incident_mode = self.get_incident(incident_id)
        weather, weather_mode = self.repository.first("weather_conditions", incident_id=incident_id)
        routes = self.repository.table("traffic_routes")
        return {
            "incident": incident,
            "weather": weather or {},
            "traffic_routes": routes.records,
        }, DataRepository.combine_modes(incident_mode, weather_mode, routes.mode_used)
