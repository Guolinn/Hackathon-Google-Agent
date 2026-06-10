#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-gen-lang-client-0192428172}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-crisisflow-backend}"
DATASET_ID="${BIGQUERY_DATASET:-crisisflow_demo}"

if [[ ! -f "app/main.py" || ! -f "Dockerfile" ]]; then
  echo "ERROR: run this script from the backend directory."
  exit 1
fi

echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Dataset: ${DATASET_ID}"
echo

gcloud config set project "$PROJECT_ID" >/dev/null

echo "Enabling required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  bigquerystorage.googleapis.com \
  storage.googleapis.com >/dev/null

echo "Checking BigQuery dataset location..."
location="$(bq show --format=prettyjson "${PROJECT_ID}:${DATASET_ID}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["location"])')"
if [[ "$location" != "US" ]]; then
  echo "ERROR: ${PROJECT_ID}:${DATASET_ID} is ${location}, but Fivetran destination is US."
  echo "Create/recreate the dataset in US before deploying BigQuery mode."
  exit 1
fi

echo "Installing cloud dependencies in a temporary virtualenv for BigQuery seeding..."
python3 -m venv /tmp/crisisflow-deploy-venv
source /tmp/crisisflow-deploy-venv/bin/activate
pip install -q -r requirements-cloud.txt

echo "Seeding supporting BigQuery tables without overwriting Fivetran supplier_inventory..."
python scripts/load_mock_data_to_bigquery.py \
  --project "$PROJECT_ID" \
  --dataset "$DATASET_ID" \
  --exclude-table supplier_inventory

echo "Checking required BigQuery tables..."
bash scripts/check_bigquery_p1_p2.sh

PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Granting Cloud Run runtime service account BigQuery read/query permissions..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/bigquery.dataViewer" >/dev/null
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/bigquery.jobUser" >/dev/null

echo "Deploying full FastAPI backend to Cloud Run with DATA_MODE=bigquery..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=1 \
  --update-env-vars "DATA_MODE=bigquery,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},BIGQUERY_DATASET=${DATASET_ID},GEMINI_MODEL=gemini-2.5-flash"

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"
echo
echo "Service URL: ${SERVICE_URL}"
echo

echo "Running end-to-end smoke test..."
bash scripts/smoke_test_api.sh "$SERVICE_URL"

echo
echo "Checking deployed API data modes..."
python3 - "$SERVICE_URL" <<'PY'
import json
import sys
import urllib.parse
import urllib.request

base_url = sys.argv[1].rstrip("/")
checks = {
    "/api/dashboard": "dashboard",
    "/api/data-sources": "data sources",
    "/api/suppliers/search?" + urllib.parse.urlencode(
        {"resource": "Burn kits", "quantity": 240, "destination": "HOSP-SFGH"}
    ): "supplier search",
}

for path, label in checks.items():
    with urllib.request.urlopen(base_url + path, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    mode = payload.get("data_mode_used")
    print(f"{label}: data_mode_used={mode}")
    if mode != "bigquery":
        raise SystemExit(f"ERROR: {label} did not use BigQuery")
PY

echo
echo "Full P1/P2 backend deployment finished."
