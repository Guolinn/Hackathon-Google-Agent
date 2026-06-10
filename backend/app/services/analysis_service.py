from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.services.data_repository import DataRepository
from app.services.datasource_service import DatasourceService
from app.services.gap_service import GapService
from app.services.incident_service import IncidentService
from app.services.surge_service import SurgeService


class AnalysisService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.incidents = IncidentService(repository)
        self.gaps = GapService(repository)
        self.surge = SurgeService()

    def analyze_incident(self, incident_id: str, check_data_freshness: bool = True) -> tuple[dict[str, Any], str]:
        context, context_mode = self.incidents.get_context(incident_id)
        patient_surge = self.surge.estimate_patient_surge(context["incident"], context.get("weather"))
        gap_data, gap_mode = self.gaps.calculate_resource_gaps(incident_id)
        datasource_data = {"sources": []}
        datasource_mode = "mock"
        if check_data_freshness:
            datasource_data, datasource_mode = DatasourceService(self.repository, get_settings()).get_data_sources()

        return {
            "incident_id": incident_id,
            "classification": context["incident"]["severity"],
            "patient_surge": patient_surge,
            "critical_gaps": [gap for gap in gap_data["gaps"] if gap["severity"] == "Critical"],
            "data_freshness": datasource_data["sources"],
            "agent_summary": (
                "Projected patient surge exceeds SF General burn and respiratory capacity within 2.5 hours. "
                "CrisisFlow recommends immediate supply transfer planning, with all actions held for human approval."
            ),
            "data_used": [
                "incident feed",
                "weather_conditions",
                "hospital_capacity",
                "hospital_inventory",
                "hospital_staffing",
                "supplier_inventory",
                "traffic_routes",
            ],
        }, DataRepository.combine_modes(context_mode, gap_mode, datasource_mode)
