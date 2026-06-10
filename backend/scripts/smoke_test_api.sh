#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-https://crisisflow-backend-556676992179.us-central1.run.app}"
INCIDENT_ID="INC-2026-0529-MARIN-014"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

request_json() {
  local method="$1"
  local path="$2"
  local body="${3:-}"
  local output="$4"

  if [[ -n "$body" ]]; then
    curl --http1.1 -fsS -X "$method" "$BASE_URL$path" \
      -H "Content-Type: application/json" \
      -d "$body" > "$output"
  else
    curl --http1.1 -fsS -X "$method" "$BASE_URL$path" > "$output"
  fi
}

print_check() {
  printf "OK  %s\n" "$1"
}

echo "CrisisFlow smoke test"
echo "Base URL: $BASE_URL"
echo

request_json GET "/health" "" "$tmpdir/health.json"
python3 - "$tmpdir/health.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["success"] is True
PY
print_check "health"

request_json GET "/api/dashboard" "" "$tmpdir/dashboard.json"
python3 - "$tmpdir/dashboard.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["data"]["incident"]["incident_id"] == "INC-2026-0529-MARIN-014"
PY
print_check "dashboard"

request_json POST "/api/agent/analyze-incident" \
  "{\"incident_id\":\"$INCIDENT_ID\",\"use_gemini\":false,\"check_data_freshness\":true}" \
  "$tmpdir/analysis.json"
python3 - "$tmpdir/analysis.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["data"]["patient_surge"]["total"] == 180
PY
print_check "agent analysis"

request_json GET "/api/suppliers/search?resource=Burn%20kits&quantity=240&destination=HOSP-SFGH" "" \
  "$tmpdir/suppliers.json"
python3 - "$tmpdir/suppliers.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
candidates = payload["data"]["candidates"]
assert candidates
assert candidates[0]["supplier_name"] == "MedSupply Oakland"
PY
print_check "supplier ranking"

request_json POST "/api/dispatch-plans/generate" \
  "{\"incident_id\":\"$INCIDENT_ID\",\"target_hospital_id\":\"HOSP-SFGH\"}" \
  "$tmpdir/plan.json"
approval_id="$(python3 - "$tmpdir/plan.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert len(payload["data"]["recommendations"]) == 5
print(payload["data"]["approval_requests"][0]["approval_id"])
PY
)"
print_check "dispatch plan generated with approval $approval_id"

request_json POST "/api/approvals/$approval_id/approve" \
  '{"approver_name":"EOC Commander","approver_role":"Emergency Operations Center","notes":"Smoke test approval."}' \
  "$tmpdir/approval.json"
python3 - "$tmpdir/approval.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["data"]["status"] == "approved"
PY
print_check "approval"

request_json POST "/api/dispatch-requests/send" \
  "{\"approval_id\":\"$approval_id\"}" \
  "$tmpdir/dispatch.json"
python3 - "$tmpdir/dispatch.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["data"]["status"] == "accepted"
PY
print_check "dispatch request"

request_json POST "/api/briefings/generate" \
  "{\"incident_id\":\"$INCIDENT_ID\",\"audience\":\"mayor\"}" \
  "$tmpdir/briefing.json"
python3 - "$tmpdir/briefing.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["data"]["generated_by"] in {"Gemini", "fallback_template"}
PY
print_check "briefing"

echo
echo "All smoke checks passed."
