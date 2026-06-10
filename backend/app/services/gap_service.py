from __future__ import annotations

import math
from typing import Any

from app.services.data_repository import DataRepository
from app.services.hospital_service import HospitalService
from app.services.incident_service import IncidentService
from app.services.normalization import normalize_resource
from app.services.surge_service import SurgeService


TIME_TO_SHORTAGE = {
    "Burn kits": 2.1,
    "Albuterol doses": 1.8,
    "Oxygen cylinders": 2.6,
    "ICU beds": 3.0,
    "ER nurses": 2.4,
}


class GapService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.incidents = IncidentService(repository)
        self.hospitals = HospitalService(repository)
        self.surge = SurgeService()

    def calculate_resource_gaps(
        self,
        incident_id: str,
        target_hospital_id: str | None = None,
    ) -> tuple[dict[str, Any], str]:
        context, context_mode = self.incidents.get_context(incident_id)
        incident = context["incident"]
        target_hospital_id = target_hospital_id or incident.get("target_hospital_id", "HOSP-SFGH")
        patient_surge = self.surge.estimate_patient_surge(incident, context.get("weather"))

        hospital, hospital_mode = self.hospitals.get_hospital(target_hospital_id)
        capacity, capacity_mode = self.hospitals.get_capacity(target_hospital_id)
        inventory, inventory_mode = self.hospitals.get_inventory(target_hospital_id)
        staffing, staffing_mode = self.hospitals.get_staffing(target_hospital_id)

        inv_by_resource = {normalize_resource(item["item_name"]): item for item in inventory}
        staff_by_role = {item["role"].lower(): item for item in staffing}

        needed = {
            "Burn kits": patient_surge["burns"] * 12,
            "Albuterol doses": int(patient_surge["smoke_inhalation"] * 3.75),
            "Oxygen cylinders": patient_surge["oxygen_support_cases"] * 3,
            "ICU beds": patient_surge["icu_risk"],
            "ER nurses": math.ceil(patient_surge["total"] / 6.5),
        }
        available = {
            "Burn kits": inv_by_resource.get("Burn kits", {}).get("quantity_available", 0),
            "Albuterol doses": inv_by_resource.get("Albuterol doses", {}).get("quantity_available", 0),
            "Oxygen cylinders": inv_by_resource.get("Oxygen cylinders", {}).get("quantity_available", 0),
            "ICU beds": capacity.get("icu_beds_available", 0),
            "ER nurses": staff_by_role.get("er nurse", {}).get("staff_available", 0),
        }

        gaps = []
        for resource, need in needed.items():
            have = int(available.get(resource, 0))
            gap = max(int(need) - have, 0)
            shortage_time = TIME_TO_SHORTAGE[resource]
            severity = self._severity(gap, shortage_time)
            gaps.append(
                {
                    "resource": resource,
                    "needed": int(need),
                    "available": have,
                    "gap": gap,
                    "time_to_shortage_hours": shortage_time,
                    "severity": severity,
                }
            )

        return {
            "incident_id": incident_id,
            "target_hospital_id": hospital["hospital_id"],
            "target_hospital": hospital["name"],
            "patient_surge": patient_surge,
            "gaps": gaps,
            "agent_conclusion": (
                "SF General will exceed burn and respiratory treatment capacity before the second patient wave. "
                "Immediate supply transfer and patient diversion are recommended for human approval."
            ),
        }, DataRepository.combine_modes(context_mode, hospital_mode, capacity_mode, inventory_mode, staffing_mode)

    @staticmethod
    def _severity(gap: int, time_to_shortage_hours: float) -> str:
        if gap <= 0:
            return "Stable"
        if time_to_shortage_hours <= 2.25:
            return "Critical"
        if time_to_shortage_hours <= 3.0:
            return "High"
        return "Medium"
