#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-gen-lang-client-0192428172}"
DATASET_ID="${BIGQUERY_DATASET:-crisisflow_demo}"

required_tables=(
  incidents
  weather_conditions
  hospitals
  hospital_capacity
  hospital_inventory
  hospital_staffing
  suppliers
  supplier_inventory
  traffic_routes
  transport_options
  emergency_contacts
  datasource_status
)

echo "Checking BigQuery dataset: ${PROJECT_ID}.${DATASET_ID}"
echo

location="$(bq show --format=prettyjson "${PROJECT_ID}:${DATASET_ID}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["location"])')"
echo "Dataset location: ${location}"
if [[ "$location" != "US" ]]; then
  echo "ERROR: dataset must be US for the current Fivetran destination."
  exit 1
fi

echo
echo "Table row counts:"
for table in "${required_tables[@]}"; do
  count="$(bq query --quiet --use_legacy_sql=false --format=csv \
    "SELECT COUNT(*) AS row_count FROM \`${PROJECT_ID}.${DATASET_ID}.${table}\`" | tail -n 1)"
  printf "%-24s %s\n" "$table" "$count"
done

echo
echo "Checking Fivetran-owned supplier inventory metadata:"
bq query --quiet --use_legacy_sql=false \
  "SELECT COUNT(*) AS row_count, MAX(_fivetran_synced) AS last_fivetran_sync
   FROM \`${PROJECT_ID}.${DATASET_ID}.supplier_inventory\`"

echo
echo "BigQuery P1/P2 check passed."
