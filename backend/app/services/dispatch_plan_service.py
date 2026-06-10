from __future__ import annotations

from typing import Any

from app.services.approval_service import ApprovalService
from app.services.briefing_service import BriefingService
from app.services.data_repository import DataRepository
from app.services.gap_service import GapService
from app.services.state_store import get_store
from app.services.supplier_service import SupplierService
from app.services.time_utils import utc_now_iso


class DispatchPlanService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
        self.gaps = GapService(repository)
        self.suppliers = SupplierService(repository)
        self.approvals = ApprovalService(repository)
        self.store = get_store()

    def generate_plan(
        self,
        incident_id: str,
        target_hospital_id: str,
        *,
        include_ai_explanations: bool = False,
        include_briefing: bool = False,
    ) -> tuple[dict[str, Any], str]:
        gap_data, gap_mode = self.gaps.calculate_resource_gaps(incident_id, target_hospital_id)
        plan_id = f"PLAN-{incident_id.split('INC-')[-1]}"
        recommendations, supplier_modes = self._build_recommendations(gap_data, target_hospital_id)
        approval_requests = self._create_approvals(incident_id, plan_id, recommendations)

        plan = {
            "plan_id": plan_id,
            "incident_id": incident_id,
            "objective": "Cover critical shortages before second patient wave",
            "estimated_time_to_stabilize_hours": 2.5,
            "risk_reduction": "High",
            "approval_required": True,
            "recommendations": recommendations,
            "approval_requests": approval_requests,
            "created_at": utc_now_iso(),
        }
        if include_briefing:
            briefing, _ = BriefingService(self.repository).generate(incident_id, "eoc", plan_id, plan_override=plan)
            plan["briefing"] = briefing
        self.store.plans[plan_id] = plan
        return plan, DataRepository.combine_modes(gap_mode, *supplier_modes)

    def _build_recommendations(self, gap_data: dict[str, Any], target_hospital_id: str) -> tuple[list[dict[str, Any]], list[str]]:
        modes = []
        gaps = {gap["resource"]: gap for gap in gap_data["gaps"]}
        recommendations = []

        supplier_plan = [
            ("Burn kits", "ACT-001", 300, "Health Department"),
            ("Albuterol doses", "ACT-002", 150, "Hospital Coordination"),
            ("Oxygen cylinders", "ACT-003", 40, "Health Department"),
        ]
        for resource, action_id, quantity, approver in supplier_plan:
            search, mode = self.suppliers.search(resource, max(gaps[resource]["gap"], 1), target_hospital_id)
            modes.append(mode)
            best = search["candidates"][0]
            recommendations.append(
                {
                    "action_id": action_id,
                    "type": "supply_transfer",
                    "title": f"Transfer {quantity} {resource.lower()} from {best['supplier_name']} to SF General",
                    "resource": resource,
                    "quantity": quantity,
                    "origin": best["supplier_name"],
                    "origin_id": best["supplier_id"],
                    "destination": "SF General",
                    "destination_id": target_hospital_id,
                    "eta_min": best["eta_min"],
                    "route": best["route"],
                    "route_risk": best["route_risk"],
                    "why": self._why(resource, gaps[resource]["gap"]),
                    "risk_if_delayed": self._risk_if_delayed(resource),
                    "approval_required": approver,
                    "confidence": "High" if best["score"] >= 80 else "Medium",
                    "score": best["score"],
                    "data_used": ["resource_gaps", "supplier_inventory", "traffic_routes", "contract_status"],
                    "alternatives": search["candidates"][1:3],
                }
            )

        recommendations.append(
            {
                "action_id": "ACT-004",
                "type": "patient_diversion",
                "title": "Divert 45 low-acuity patients to UCSF and CPMC",
                "resource": "ER capacity",
                "quantity": 45,
                "origin": "SF General intake queue",
                "destination": "UCSF Medical Center and CPMC Van Ness",
                "eta_min": 0,
                "why": "SF General is projected to receive 105 patients while current ER load is 86%.",
                "risk_if_delayed": "SF General ER wait times and ambulance offload delays will increase during the second patient wave.",
                "approval_required": "EOC and hospital coordination",
                "confidence": "High",
                "data_used": ["patient_surge", "hospital_capacity"],
            }
        )
        recommendations.append(
            {
                "action_id": "ACT-005",
                "type": "logistics_standby",
                "title": "Place BayMed Logistics on standby for supplier pickup",
                "resource": "Medical transport",
                "quantity": 3,
                "origin": "BayMed Logistics",
                "destination": "MedSupply Oakland and SF General",
                "eta_min": 30,
                "why": "Highway 101 congestion may delay standard supplier delivery routes.",
                "risk_if_delayed": "Approved supplies may be ready before a reliable pickup vehicle is assigned.",
                "approval_required": "EOC logistics lead",
                "confidence": "Medium",
                "data_used": ["traffic_routes", "transport_options"],
            }
        )
        return recommendations, modes

    def _create_approvals(
        self,
        incident_id: str,
        plan_id: str,
        recommendations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        approvals = []
        for index, recommendation in enumerate(recommendations, start=1):
            approval = {
                "approval_id": f"APR-{index:03d}",
                "incident_id": incident_id,
                "plan_id": plan_id,
                "action_id": recommendation["action_id"],
                "action_type": recommendation["type"],
                "action_summary": recommendation["title"],
                "required_approver": recommendation["approval_required"],
                "risk_level": "High" if index in {1, 3, 4} else "Medium",
                "status": "pending",
                "created_at": utc_now_iso(),
                "recommendation": recommendation,
            }
            self.approvals.create_approval(approval)
            approvals.append({key: approval[key] for key in approval if key != "recommendation"})
        return approvals

    @staticmethod
    def _why(resource: str, gap: int) -> str:
        return {
            "Burn kits": f"SF General has a {gap}-unit burn kit gap and will exhaust burn care supplies before the second wave.",
            "Albuterol doses": f"Respiratory medication demand exceeds local inventory by {gap} doses.",
            "Oxygen cylinders": f"Oxygen cylinder demand exceeds local inventory by {gap} cylinders.",
        }[resource]

    @staticmethod
    def _risk_if_delayed(resource: str) -> str:
        return {
            "Burn kits": "Burn care shortage before second patient wave.",
            "Albuterol doses": "Increased respiratory treatment wait times during smoke inhalation surge.",
            "Oxygen cylinders": "Oxygen shortage during severe respiratory and ICU surge.",
        }[resource]
