from __future__ import annotations

from typing import Any


class RankingService:
    ROUTE_SCORE = {"low": 100, "medium": 70, "high": 35, "blocked": 0}
    CONTRACT_SCORE = {
        "pre_approved": 100,
        "hospital_reserve": 95,
        "existing_vendor": 80,
        "portal_only": 60,
        "emergency_contact_only": 40,
    }
    INTEGRATION_SCORE = {
        "api": 100,
        "database": 95,
        "portal": 75,
        "email fallback": 50,
        "email_sms": 50,
        "unknown": 25,
    }

    def score_candidate(self, candidate: dict[str, Any], quantity_needed: int) -> float:
        inventory_score = self._inventory_fit(candidate.get("available", 0), quantity_needed)
        eta_score = self._eta(candidate.get("eta_min", 999))
        route_score = self.ROUTE_SCORE.get(str(candidate.get("route_risk", "unknown")).lower(), 25)
        contract_score = self.CONTRACT_SCORE.get(str(candidate.get("contract_status", "")).lower(), 50)
        integration_score = self.INTEGRATION_SCORE.get(str(candidate.get("integration_type", "")).lower(), 40)
        return round(
            inventory_score * 0.35
            + eta_score * 0.35
            + route_score * 0.15
            + contract_score * 0.10
            + integration_score * 0.05,
            1,
        )

    @staticmethod
    def label_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        labels = ["Best", "Backup", "Backup"]
        for index, candidate in enumerate(candidates):
            candidate["recommendation"] = labels[index] if index < len(labels) else "Option"
        return candidates

    @staticmethod
    def _inventory_fit(available: int, quantity_needed: int) -> int:
        if available >= quantity_needed:
            return 100
        if available >= quantity_needed * 0.5:
            return 70
        if available > 0:
            return 40
        return 0

    @staticmethod
    def _eta(eta_min: int) -> int:
        if eta_min <= 45:
            return 100
        if eta_min <= 90:
            return 75
        if eta_min <= 150:
            return 50
        return 25
