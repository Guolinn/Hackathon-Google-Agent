from __future__ import annotations

from typing import Any

from app.agent.crisisflow_agent import CrisisFlowAgent
from app.agent.prompts import briefing_prompt
from app.config import get_settings
from app.services.data_repository import DataRepository
from app.services.gap_service import GapService
from app.services.incident_service import IncidentService
from app.services.state_store import get_store


class BriefingService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.incidents = IncidentService(repository)
        self.gaps = GapService(repository)
        self.store = get_store()
        self.agent = CrisisFlowAgent(get_settings())

    def generate(
        self,
        incident_id: str,
        audience: str,
        plan_id: str | None = None,
        *,
        plan_override: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], str]:
        context, context_mode = self.incidents.get_context(incident_id)
        gap_data, gap_mode = self.gaps.calculate_resource_gaps(incident_id)
        plan = plan_override or (self.store.plans.get(plan_id or "") if plan_id else None)
        payload = {
            "incident": context["incident"],
            "weather": context.get("weather"),
            "resource_gaps": gap_data["gaps"],
            "patient_surge": gap_data["patient_surge"],
            "dispatch_plan": plan,
        }

        prompt = briefing_prompt(audience, payload)
        generated = self.agent.generate_text(prompt)
        if generated:
            body = generated.strip()
            generated_by = "Gemini"
        else:
            body = self._fallback(audience, payload)
            generated_by = "fallback_template"

        return {
            "audience": audience,
            "title": self._title(audience),
            "body": body,
            "generated_by": generated_by,
            "requires_review": True,
            "data_used": [
                "incident",
                "weather_conditions",
                "patient_surge",
                "resource_gaps",
                "dispatch_plan",
            ],
        }, DataRepository.combine_modes(context_mode, gap_mode)

    @staticmethod
    def _title(audience: str) -> str:
        return {
            "mayor": "Marin Wildfire Medical Surge Briefing",
            "eoc": "EOC Operational Summary",
            "supplier": "Emergency Supplier Dispatch Alert",
            "public": "Public Smoke and Medical Resource Advisory",
        }.get(audience.lower(), "CrisisFlow Emergency Briefing")

    @staticmethod
    def _fallback(audience: str, payload: dict[str, Any]) -> str:
        patient_total = payload["patient_surge"]["total"]
        gaps = payload["resource_gaps"]
        critical = ", ".join(f"{gap['resource']} ({gap['gap']} gap)" for gap in gaps if gap["gap"] > 0)
        base = (
            f"A {patient_total}-patient surge is projected over the next 2.5 hours. "
            f"Critical resource gaps include {critical}. "
            "CrisisFlow recommends regional supply transfer, patient diversion, and logistics standby. "
            "All high-risk actions require EOC or Health Department approval before dispatch."
        )
        if audience.lower() == "public":
            return (
                "Smoke conditions are worsening across parts of San Francisco. Residents in affected areas should "
                "limit outdoor activity, follow evacuation instructions, and keep emergency routes clear. "
                "Additional medical resources are being coordinated across regional hospitals and suppliers."
            )
        if audience.lower() == "supplier":
            return (
                "Emergency supplier coordination is requested under the active Marin wildfire incident. "
                "Please confirm available stock, pickup readiness, and ETA for approved dispatch requests within 10 minutes."
            )
        return base
