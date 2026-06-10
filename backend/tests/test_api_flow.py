from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_demo_flow_analyze_plan_approve_send_briefing():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["success"] is True

    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200
    assert dashboard.json()["data"]["incident"]["incident_id"] == "INC-2026-0529-MARIN-014"

    analysis = client.post(
        "/api/agent/analyze-incident",
        json={"incident_id": "INC-2026-0529-MARIN-014", "use_gemini": False, "check_data_freshness": True},
    )
    assert analysis.status_code == 200
    assert analysis.json()["data"]["patient_surge"]["total"] == 180

    plan = client.post(
        "/api/dispatch-plans/generate",
        json={"incident_id": "INC-2026-0529-MARIN-014", "target_hospital_id": "HOSP-SFGH"},
    )
    assert plan.status_code == 200
    plan_data = plan.json()["data"]
    assert len(plan_data["recommendations"]) == 5
    approval_id = plan_data["approval_requests"][0]["approval_id"]

    approval = client.post(
        f"/api/approvals/{approval_id}/approve",
        json={
            "approver_name": "EOC Commander",
            "approver_role": "Emergency Operations Center",
            "notes": "Approved for demo test.",
        },
    )
    assert approval.status_code == 200
    assert approval.json()["data"]["status"] == "approved"

    dispatch = client.post("/api/dispatch-requests/send", json={"approval_id": approval_id})
    assert dispatch.status_code == 200
    assert dispatch.json()["data"]["status"] == "accepted"

    briefing = client.post(
        "/api/briefings/generate",
        json={"incident_id": "INC-2026-0529-MARIN-014", "plan_id": plan_data["plan_id"], "audience": "mayor"},
    )
    assert briefing.status_code == 200
    assert briefing.json()["data"]["generated_by"] in {"Gemini", "fallback_template"}
