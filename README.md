# CrisisFlow AI

AI-powered emergency medical resource coordination for disaster response teams.

CrisisFlow predicts medical surge after a disaster, calculates hospital resource gaps, ranks pre-vetted suppliers by inventory and ETA, prepares human-approved dispatch requests, and generates executive briefings with Gemini.

## Live Backend

```txt
https://crisisflow-backend-556676992179.us-central1.run.app
```

API docs:

```txt
https://crisisflow-backend-556676992179.us-central1.run.app/docs
```

Demo identifiers:

```txt
incident_id: INC-2026-0529-MARIN-014
target_hospital_id: HOSP-SFGH
```

## Architecture

```txt
Google Sheets supplier inventory
  -> Fivetran
  -> BigQuery crisisflow_demo
  -> FastAPI on Cloud Run
  -> deterministic dispatch services
  -> Gemini briefing generation
  -> frontend command center
```

Real infrastructure:

- Cloud Run backend
- BigQuery data layer
- Fivetran Google Sheets sync
- Gemini briefing generation
- Fivetran REST status integration with safe fallback

Hackathon simulated datasets:

- wildfire incident
- weather and wind
- hospital capacity
- hospital inventory
- hospital staffing
- suppliers
- traffic routes
- emergency contacts

## Repository Contents

```txt
src/                                  Vite React frontend
src/CrisisFlow.jsx                    CrisisFlow command center UI
src/App.jsx                           Frontend app wrapper
src/main.jsx                          Vite entry point
backend/                              FastAPI backend, services, tests, deploy scripts
CrisisFlow_AI_PRD.md                  Product requirements document
CrisisFlow_Technical_Execution_Plan.md Technical architecture and execution plan
PERSON_A_FRONTEND_HANDOFF.md          Frontend API handoff
PROJECT_COMPLETION_STATUS.md          Completion status and remaining polish
```

## Frontend Local Run

```bash
npm install
npm run dev
```

The frontend calls the deployed Cloud Run backend directly:

```txt
https://crisisflow-backend-556676992179.us-central1.run.app
```

No Gemini, Fivetran, or database keys are needed in the browser.

## Core API

All API responses use:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "data_mode_used": "bigquery",
  "generated_at": "2026-06-07T00:00:00+00:00"
}
```

Important endpoints:

```txt
GET  /health
GET  /api/dashboard
GET  /api/data-sources
POST /api/agent/analyze-incident
GET  /api/resource-gaps/{incident_id}
GET  /api/suppliers/search?resource=Burn%20kits&quantity=240&destination=HOSP-SFGH
POST /api/dispatch-plans/generate
POST /api/approvals/{approval_id}/approve
POST /api/dispatch-requests/send
POST /api/briefings/generate
```

## Backend Local Run

```bash
cd backend
python3 -m venv /tmp/crisisflow-backend-venv
source /tmp/crisisflow-backend-venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Use cloud dependencies for BigQuery/Gemini SDK support:

```bash
pip install -r requirements-cloud.txt
```

## Backend Smoke Test

```bash
cd backend
bash scripts/smoke_test_api.sh https://crisisflow-backend-556676992179.us-central1.run.app
```

Expected:

```txt
All smoke checks passed.
```

## Cloud Run Deploy

```bash
cd backend
bash scripts/deploy_full_cloud_run.sh
```

This seeds supporting BigQuery tables while preserving the Fivetran-owned `supplier_inventory` table.
For the hackathon approval demo, the deployment script also keeps Cloud Run at one instance so short-lived approval state remains consistent during the flow.

## Security Notes

Do not commit:

- `.env`
- Gemini API keys
- Fivetran API keys/secrets
- service account JSON keys

Use Cloud Run environment variables or Secret Manager for runtime credentials.
