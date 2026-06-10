from __future__ import annotations

import math
from typing import Any


class SurgeService:
    def estimate_patient_surge(self, incident: dict[str, Any], weather: dict[str, Any] | None = None) -> dict[str, Any]:
        if incident.get("patient_surge"):
            return dict(incident["patient_surge"])

        total = int(incident.get("projected_patients") or math.ceil(incident.get("population_at_risk", 0) * 0.0043))
        burns = round(total * 0.19)
        smoke = round(total * 0.44)
        trauma = round(total * 0.16)
        icu = round(total * 0.07)
        observation = max(total - burns - smoke - trauma - icu, 0)
        return {
            "total": total,
            "burns": burns,
            "smoke_inhalation": smoke,
            "trauma": trauma,
            "icu_risk": icu,
            "observation": observation,
            "oxygen_support_cases": round(smoke * 0.375),
            "peak_arrival_hours": incident.get("peak_arrival_hours", 2.5),
        }
