from __future__ import annotations

from typing import Any

from app.services.data_repository import DataRepository


class HospitalService:
    def __init__(self, repository: DataRepository):
        self.repository = repository

    def get_hospital(self, hospital_id: str) -> tuple[dict[str, Any], str]:
        hospital, mode = self.repository.first("hospitals", hospital_id=hospital_id)
        if hospital is None:
            raise KeyError(f"Hospital {hospital_id} not found")
        return hospital, mode

    def get_capacity(self, hospital_id: str) -> tuple[dict[str, Any], str]:
        capacity, mode = self.repository.first("hospital_capacity", hospital_id=hospital_id)
        if capacity is None:
            raise KeyError(f"Capacity for hospital {hospital_id} not found")
        return capacity, mode

    def get_inventory(self, hospital_id: str) -> tuple[list[dict[str, Any]], str]:
        inventory = self.repository.table("hospital_inventory")
        return [item for item in inventory.records if item.get("hospital_id") == hospital_id], inventory.mode_used

    def get_staffing(self, hospital_id: str) -> tuple[list[dict[str, Any]], str]:
        staffing = self.repository.table("hospital_staffing")
        return [item for item in staffing.records if item.get("hospital_id") == hospital_id], staffing.mode_used

    def get_hospital_statuses(self) -> tuple[list[dict[str, Any]], str]:
        hospitals = self.repository.table("hospitals")
        capacities = self.repository.table("hospital_capacity")
        capacity_by_hospital = {item["hospital_id"]: item for item in capacities.records}
        statuses = []
        for hospital in hospitals.records:
            capacity = capacity_by_hospital.get(hospital["hospital_id"], {})
            er_available = capacity.get("er_capacity_available", 0)
            er_total = capacity.get("er_capacity_total", 1)
            pressure = "High" if capacity.get("current_er_load_percent", 0) >= 80 else "Medium"
            if capacity.get("current_er_load_percent", 0) < 60:
                pressure = "Low"
            statuses.append(
                {
                    "hospital_id": hospital["hospital_id"],
                    "name": hospital["name"],
                    "city": hospital["city"],
                    "er_status": "Critical" if pressure == "High" else "Stable",
                    "er_capacity_available": er_available,
                    "er_capacity_total": er_total,
                    "icu_beds_available": capacity.get("icu_beds_available", 0),
                    "icu_beds_total": capacity.get("icu_beds_total", 0),
                    "burn_beds_available": capacity.get("burn_beds_available", 0),
                    "burn_beds_total": capacity.get("burn_beds_total", 0),
                    "pressure": pressure,
                }
            )
        return statuses, DataRepository.combine_modes(hospitals.mode_used, capacities.mode_used)
