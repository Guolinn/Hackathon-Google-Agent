# CrisisFlow Person A Frontend Handoff

This is the frontend handoff for connecting the CrisisFlow UI to the backend.

## API Base URL

```txt
https://crisisflow-backend-556676992179.us-central1.run.app
```

Use this in the frontend:

```ts
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://crisisflow-backend-556676992179.us-central1.run.app";
```

## Response Envelope

Every endpoint returns the same outer shape:

```ts
type ApiEnvelope<T> = {
  success: boolean;
  data: T;
  error: string | null;
  data_mode_used: "mock" | "bigquery";
  generated_at: string;
};
```

Frontend should always read from `response.data`, not from the root object.

Recommended fetch helper:

```ts
export async function crisisflowFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiEnvelope<T>> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  const payload = (await res.json()) as ApiEnvelope<T>;
  if (!res.ok || !payload.success) {
    throw new Error(payload.error ?? `CrisisFlow API failed: ${res.status}`);
  }
  return payload;
}
```

## Demo Incident ID

Use this incident everywhere:

```txt
INC-2026-0529-MARIN-014
```

Use this target hospital:

```txt
HOSP-SFGH
```

## Recommended Frontend Pages

### 1. Command Center

Purpose: first screen, show disaster status and overall operating picture.

Call:

```http
GET /api/dashboard
```

Show:

- Incident name/type/severity.
- Affected area.
- Patient surge summary.
- Top resource gaps.
- Data source health.
- CTA button: `Analyze Incident`.

### 2. Agent Analysis

Purpose: show the AI agent has analyzed the incident and identified shortages.

Call:

```http
POST /api/agent/analyze-incident
```

Body:

```json
{
  "incident_id": "INC-2026-0529-MARIN-014",
  "use_gemini": true,
  "check_data_freshness": true
}
```

Show:

- Patient surge total: `180`.
- Burns: `35`.
- Smoke inhalation: `80`.
- Trauma: `28`.
- ICU risk: `12`.
- Observation: `25`.
- Agent recommendation summary.

### 3. Resource Gaps

Purpose: show deterministic calculation, not random AI output.

Call:

```http
GET /api/resource-gaps/INC-2026-0529-MARIN-014
```

Show table:

- Burn kits: needed `420`, available `180`, gap `240`.
- Albuterol doses: needed `300`, available `180`, gap `120`.
- Oxygen cylinders: needed `90`, available `54`, gap `36`.
- ICU beds: needed `12`, available `7`, gap `5`.
- ER nurses: needed `28`, available `20`, gap `8`.

### 4. Supplier Ranking

Purpose: show CrisisFlow searches available resources and compares ETA/risk.

Calls:

```http
GET /api/suppliers/search?resource=Burn%20kits&quantity=240&destination=HOSP-SFGH
GET /api/suppliers/search?resource=Albuterol%20doses&quantity=120&destination=HOSP-SFGH
GET /api/suppliers/search?resource=Oxygen%20cylinders&quantity=36&destination=HOSP-SFGH
```

Show:

- Supplier name.
- Available quantity.
- ETA minutes.
- Route risk.
- Contract status.
- Integration type.
- Score.
- Recommendation label: `Best`, `Backup`, etc.

Important demo winners:

- Burn kits best: `MedSupply Oakland`.
- Albuterol best: `UCSF Storage`.
- Oxygen best: `NorCal Oxygen`.

### 5. Dispatch Plan

Purpose: show the system creates approval-ready actions.

Call:

```http
POST /api/dispatch-plans/generate
```

Body:

```json
{
  "incident_id": "INC-2026-0529-MARIN-014",
  "target_hospital_id": "HOSP-SFGH",
  "include_briefing": false,
  "include_ai_explanations": false
}
```

Show the 5 recommendations:

- Transfer burn kits from MedSupply Oakland to SF General.
- Transfer albuterol from UCSF Storage to SF General.
- Dispatch oxygen cylinders from NorCal Oxygen to SF General.
- Divert low-acuity patients to UCSF/CPMC.
- Place BayMed Logistics on standby.

Store the first `approval_requests[0].approval_id` for the next step.

### 6. Approval Queue

Purpose: make it clear AI does not autonomously move emergency resources.

Call:

```http
POST /api/approvals/{approval_id}/approve
```

Body:

```json
{
  "approver_name": "EOC Commander",
  "approver_role": "Emergency Operations Center",
  "notes": "Approved under Level 4 wildfire emergency."
}
```

Show:

- Approval status changed to `approved`.
- `next_action`: `dispatch_request_ready`.
- Approver name/role.

### 7. Dispatch Request

Purpose: show the final action is ready to send to supplier/vendor.

Call:

```http
POST /api/dispatch-requests/send
```

Body:

```json
{
  "approval_id": "APR-001"
}
```

Show:

- Dispatch request ID.
- Supplier.
- Destination.
- Resource.
- Quantity.
- ETA.
- Contact method.
- Supplier confirmation status: `accepted`.
- Emergency dispatch message.

### 8. Briefing Generator

Purpose: show Gemini-generated executive communication.

Call:

```http
POST /api/briefings/generate
```

Body:

```json
{
  "incident_id": "INC-2026-0529-MARIN-014",
  "audience": "mayor"
}
```

Show:

- Briefing markdown/text.
- `generated_by`: `Gemini` or `fallback_template`.
- Data used.
- Approval note.

### 9. Data Pipeline

Purpose: show why Fivetran matters.

Call:

```http
GET /api/data-sources
```

Show:

- Source name.
- Last sync freshness.
- Connector status.
- Used by agent.

Also keep screenshots of:

- Google Sheet source data.
- Fivetran active connector.
- BigQuery table with `_fivetran_synced`.

## Ideal Demo Click Flow

1. Open Command Center.
2. Click `Analyze Incident`.
3. Show resource gaps.
4. Click a resource gap and show supplier ranking.
5. Click `Generate Dispatch Plan`.
6. Click `Approve`.
7. Click `Send Dispatch Request`.
8. Click `Generate Mayor Briefing`.
9. End on Data Pipeline proof: Google Sheets -> Fivetran -> BigQuery.

## UI Copy To Use

Use concise product language:

```txt
CrisisFlow predicts emergency medical resource gaps, ranks pre-vetted suppliers by ETA and route risk, and prepares human-approved dispatch requests.
```

Use this disclaimer in small text only where needed:

```txt
Scenario data is simulated for the hackathon; the cloud data pipeline, API, and Gemini briefing generation are live.
```

## What Not To Build

Do not spend time on:

- Marketing landing page.
- Login/auth.
- Real map routing.
- Real SMS/call integration.
- Editing all dataset values from the frontend.

Focus on a polished emergency operations dashboard and a smooth dispatch flow.
