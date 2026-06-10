# Person B Handoff

This document is the backend, agent, and data handoff for CrisisFlow.

## Current Cloud Endpoint

```txt
https://crisisflow-backend-556676992179.us-central1.run.app
```

## Completion Status

Person B scope is demo-complete when these checks pass:

- FastAPI public API is reachable from Cloud Run.
- Gemini briefing generation works, with template fallback if the key is missing.
- Google Sheets supplier inventory syncs through Fivetran into BigQuery.
- BigQuery contains `crisisflow_demo.supplier_inventory` with `_fivetran_synced`.
- Core flow works: analyze incident, calculate gaps, rank suppliers, generate dispatch plan, approve, send dispatch request, generate briefing.

## Real vs Simulated Data

Real infrastructure:

- Cloud Run backend
- Gemini API briefing generation
- Fivetran Google Sheets connector
- BigQuery dataset and table

Simulated hackathon data:

- Incident
- Weather
- Hospital capacity
- Hospital inventory
- Staffing
- Supplier contracts
- Traffic routes
- Emergency contacts

This is the correct demo framing: real cloud pipeline, simulated emergency operations data.

## BigQuery Tables

Fivetran owns this table:

```txt
crisisflow_demo.supplier_inventory
```

Do not overwrite it when using the local seed script.

To seed all supporting demo tables into BigQuery while preserving the Fivetran-owned supplier inventory table:

```bash
cd backend
pip install -r requirements-cloud.txt
python scripts/load_mock_data_to_bigquery.py \
  --project gen-lang-client-0192428172 \
  --dataset crisisflow_demo \
  --exclude-table supplier_inventory
```

After this, `DATA_MODE=bigquery` can use BigQuery for supporting tables and the Fivetran-owned supplier inventory table.

## Cloud Run Environment

Recommended final demo settings:

```txt
DATA_MODE=bigquery
GOOGLE_CLOUD_PROJECT=gen-lang-client-0192428172
BIGQUERY_DATASET=crisisflow_demo
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_KEY=<configured in Cloud Run secret or env var>
```

Optional Fivetran REST status:

```txt
FIVETRAN_API_KEY=<api key>
FIVETRAN_API_SECRET=<api secret>
```

If Fivetran credentials are missing, `/api/data-sources` returns stable Fivetran-style mock connector health.

For the hackathon demo, Cloud Run should stay at one instance because the approval flow stores short-lived demo state in memory:

```bash
gcloud run services update crisisflow-backend \
  --region us-central1 \
  --min-instances=1 \
  --max-instances=1
```

## Smoke Test

Run this from local terminal or Cloud Shell:

```bash
cd backend
bash scripts/smoke_test_api.sh
```

Or with a custom URL:

```bash
bash scripts/smoke_test_api.sh https://YOUR_CLOUD_RUN_URL
```

Expected result:

```txt
All smoke checks passed.
```

## Frontend API Contract

Every response has this shape:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "data_mode_used": "mock",
  "generated_at": "2026-06-07T00:00:00+00:00"
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
- `POST /api/dispatch-requests/send`
- `POST /api/briefings/generate`

## Demo Story

Use this sequence:

1. Wildfire incident is detected near Marin.
2. CrisisFlow predicts 180 total patients and identifies burn, respiratory, oxygen, ICU, and nurse gaps.
3. Fivetran syncs supplier inventory from Google Sheets into BigQuery.
4. CrisisFlow ranks suppliers by inventory fit, ETA, route risk, contract status, and integration type.
5. The system generates a dispatch plan.
6. EOC commander approves the recommendation.
7. CrisisFlow sends an emergency dispatch request.
8. Gemini generates the mayor or EOC briefing based only on backend-calculated numbers.

## Screenshots To Keep

- Google Sheet source inventory.
- Fivetran active connection: `crisisflow_demo.supplier_inventory`.
- BigQuery query result showing 5 rows and `_fivetran_synced`.
- Cloud Run health or API response.

## Optional Production Hardening

These are not required for the hackathon demo, but they are the next real-product upgrades:

- Move approval and dispatch state from in-memory storage to Firestore or Redis.
- Move `GEMINI_API_KEY` and Fivetran credentials into Secret Manager.
- Add more Fivetran-backed sheets for hospital inventory, hospital capacity, and traffic routes.
- Add audit logs for every recommendation, approval, and dispatch request.
