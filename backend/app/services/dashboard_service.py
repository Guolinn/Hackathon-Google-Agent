from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.services.data_repository import DataRepository
from app.services.datasource_service import DatasourceService
from app.services.gap_service import GapService
from app.services.hospital_service import HospitalService
from app.services.incident_service import IncidentService


class DashboardService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.incidents = IncidentService(repository)
        self.hospitals = HospitalService(repository)
        self.gaps = GapService(repository)

    def get_dashboard(self) -> tuple[dict[str, Any], str]:
        incident, incident_mode = self.incidents.get_current_incident()
        gap_data, gap_mode = self.gaps.calculate_resource_gaps(incident["incident_id"])
        hospital_statuses, hospital_mode = self.hospitals.get_hospital_statuses()
        datasource_data, datasource_mode = DatasourceService(self.repository, get_settings()).get_data_sources()

        critical_or_high = [gap for gap in gap_data["gaps"] if gap["severity"] in {"Critical", "High"}]
        return {
            "incident": {
                "incident_id": incident["incident_id"],
                "type": incident["type"],
                "location_name": incident["location_name"],
                "severity": incident["severity"],
                "population_at_risk": incident["population_at_risk"],
                "status": incident["status"],
                "wind_direction": "South-East toward SF",
            },
            "summary": {
                "projected_patients": gap_data["patient_surge"]["total"],
                "hospital_pressure": "High",
                "resource_gaps": len(critical_or_high),
                "approval_required": 4,
                "target_hospital": gap_data["target_hospital"],
            },
            "agent_activity": [
                "Incident received",
                "Weather and wind data checked",
                "Hospital capacity checked",
                "Medical inventory checked",
                "Supplier network queried",
                "ETA options ranked",
            ],
            "risk_cards": [
                "SF General burn kits shortage expected in 2.1h",
                "Highway 101 congestion may delay ambulance routes by 38m",
                "Respiratory medication demand exceeds local inventory by 120 doses",
            ],
            "hospitals": hospital_statuses,
            "resource_gaps": gap_data["gaps"],
            "data_sources": datasource_data["sources"],
        }, DataRepository.combine_modes(incident_mode, gap_mode, hospital_mode, datasource_mode)
