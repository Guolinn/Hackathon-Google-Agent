# CrisisFlow Backend

FastAPI backend for the Person B scope: mock data, deterministic resource gap calculation, supplier ranking, approval flow, dispatch requests, optional Gemini briefing, optional BigQuery data mode, and Fivetran-style data source health.

## Quick Start

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend automatically reads `backend/.env` if present. Keep real keys in `.env`, not in source files.

Gemini briefing works through the REST API with only `GEMINI_API_KEY`; no extra package is required. For BigQuery and optional Gemini SDK support, install the optional cloud dependencies:

```bash
pip install -r requirements-cloud.txt
```

Health check:

```bash
curl http://localhost:8000/health
```

## Environment

```bash
DATA_MODE=mock
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_CLOUD_PROJECT=
BIGQUERY_DATASET=crisisflow_demo
FIVETRAN_API_KEY=
FIVETRAN_API_SECRET=
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

`DATA_MODE=mock` is the stable demo mode. `DATA_MODE=bigquery` attempts BigQuery and automatically falls back to mock data if credentials, dataset, or libraries fail.

## Public API

All API responses use:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "data_mode_used": "mock",
  "generated_at": "2026-05-29T17:45:00Z"
}
```

Core endpoints:

- `GET /health`
- `GET /api/dashboard`
- `GET /api/data-sources`
- `POST /api/agent/analyze-incident`
- `GET /api/resource-gaps/{incident_id}`
- `GET /api/suppliers/search?resource=Burn kits&quantity=240&destination=HOSP-SFGH`
- `POST /api/dispatch-plans/generate`
- `POST /api/approvals/{approval_id}/approve`
- `POST /api/approvals/{approval_id}/reject`
- `POST /api/approvals/{approval_id}/request-changes`
- `POST /api/dispatch-requests/send`
- `GET /api/dispatch-requests/{dispatch_request_id}`
- `POST /api/briefings/generate`

## Demo Flow

```bash
curl -X POST http://localhost:8000/api/agent/analyze-incident \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"INC-2026-0529-MARIN-014","use_gemini":false,"check_data_freshness":true}'

curl -X POST http://localhost:8000/api/dispatch-plans/generate \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"INC-2026-0529-MARIN-014","target_hospital_id":"HOSP-SFGH"}'
```

Approve the first returned approval id, then send the dispatch request:

```bash
curl -X POST http://localhost:8000/api/approvals/APR-001/approve \
  -H "Content-Type: application/json" \
  -d '{"approver_name":"EOC Commander","approver_role":"Emergency Operations Center","notes":"Approved under Level 4 wildfire emergency."}'

curl -X POST http://localhost:8000/api/dispatch-requests/send \
  -H "Content-Type: application/json" \
  -d '{"approval_id":"APR-001"}'
```

## Tests

```bash
cd backend
pytest
```

## Cloud Run

Use the full deployment script for the hackathon environment:

```bash
cd backend
bash scripts/deploy_full_cloud_run.sh
```

The script:

- verifies the BigQuery dataset is in `US`
- seeds supporting demo tables
- preserves the Fivetran-owned `supplier_inventory` table
- deploys Cloud Run with `DATA_MODE=bigquery`
- pins Cloud Run to one instance for the in-memory approval demo state
- runs the end-to-end smoke test

To build a Docker image with optional cloud SDKs:

```bash
docker build --build-arg REQUIREMENTS=requirements-cloud.txt -t crisisflow-backend:cloud .
```

## BigQuery Seeding

After installing optional cloud dependencies and authenticating with `gcloud auth application-default login`, load the mock demo data into BigQuery:

```bash
cd backend
pip install -r requirements-cloud.txt
python scripts/load_mock_data_to_bigquery.py --project YOUR_GCP_PROJECT --dataset crisisflow_demo
```
