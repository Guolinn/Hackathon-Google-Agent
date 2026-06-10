import { useState, useEffect, useRef } from "react";

const API = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? "" : "https://crisisflow-backend-556676992179.us-central1.run.app");
const INCIDENT_ID = "INC-2026-0529-MARIN-014";
const HOSP_ID = "HOSP-SFGH";

async function cfFetch(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(opts.headers ?? {}) },
  });
  const payload = await res.json();
  if (!res.ok || !payload.success) throw new Error(payload.error ?? `API error ${res.status}`);
  return payload;
}

const SEVERITY_COLOR = { critical: "#E24B4A", high: "#EF9F27", moderate: "#1D9E75", low: "#378ADD" };

function Badge({ label, color = "#378ADD", bg }) {
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, letterSpacing: "0.04em",
      padding: "2px 8px", borderRadius: 4,
      background: bg ?? color + "22", color,
      textTransform: "uppercase", whiteSpace: "nowrap",
    }}>{label}</span>
  );
}

function Spinner() {
  return (
    <span style={{ display: "inline-block", width: 14, height: 14, border: "2px solid #ffffff33", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
  );
}

function StatCard({ label, value, sub, color = "#22D3EE" }) {
  return (
    <div style={{ background: "#131929", border: "1px solid #1e2d47", borderRadius: 8, padding: "14px 16px", minWidth: 0 }}>
      <div style={{ fontSize: 11, color: "#6b7fa3", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, fontFamily: "JetBrains Mono, monospace", color }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "#4a5870", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function SectionHeader({ icon, title, meta }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
      <span style={{ fontSize: 18, color: "#22D3EE" }}>{icon}</span>
      <span style={{ fontSize: 15, fontWeight: 600, color: "#e2e8f0" }}>{title}</span>
      {meta && <span style={{ fontSize: 11, color: "#4a5870", marginLeft: "auto" }}>{meta}</span>}
    </div>
  );
}

function Btn({ onClick, loading, children, variant = "primary", small }) {
  const base = {
    display: "inline-flex", alignItems: "center", gap: 8,
    padding: small ? "6px 14px" : "9px 20px",
    borderRadius: 6, fontWeight: 600, fontSize: small ? 12 : 13,
    cursor: loading ? "not-allowed" : "pointer",
    border: "none", transition: "opacity 0.15s",
    opacity: loading ? 0.7 : 1,
  };
  const styles = {
    primary: { background: "#F59E0B", color: "#1a1000" },
    cyan: { background: "#22D3EE", color: "#031a1e" },
    ghost: { background: "transparent", color: "#94a3b8", border: "1px solid #1e2d47" },
    danger: { background: "#E24B4A22", color: "#E24B4A", border: "1px solid #E24B4A44" },
    success: { background: "#1D9E7522", color: "#1D9E75", border: "1px solid #1D9E7544" },
  };
  return (
    <button style={{ ...base, ...(styles[variant] ?? styles.primary) }} onClick={onClick}>
      {loading ? <Spinner /> : null}{children}
    </button>
  );
}

const STEPS = [
  { id: "dashboard", label: "Command Center" },
  { id: "analysis", label: "Agent Analysis" },
  { id: "gaps", label: "Resource Gaps" },
  { id: "suppliers", label: "Supplier Ranking" },
  { id: "dispatch", label: "Dispatch Plan" },
  { id: "approval", label: "Approval Queue" },
  { id: "send", label: "Dispatch Request" },
  { id: "briefing", label: "Mayor Briefing" },
  { id: "pipeline", label: "Data Pipeline" },
];

export default function App() {
  const [activeStep, setActiveStep] = useState("dashboard");
  const [data, setData] = useState({});
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  const [approvalId, setApprovalId] = useState(null);

  const setLoad = (k, v) => setLoading(p => ({ ...p, [k]: v }));
  const setErr = (k, v) => setErrors(p => ({ ...p, [k]: v }));
  const setDat = (k, v) => setData(p => ({ ...p, [k]: v }));

  async function run(key, fn) {
    setLoad(key, true); setErr(key, null);
    try { const r = await fn(); setDat(key, r); return r; }
    catch (e) { setErr(key, e.message); }
    finally { setLoad(key, false); }
  }

  async function loadDashboard() {
    await run("dashboard", () => cfFetch("/api/dashboard"));
  }

  async function loadAnalysis() {
    await run("analysis", () => cfFetch("/api/agent/analyze-incident", {
      method: "POST",
      body: JSON.stringify({ incident_id: INCIDENT_ID, use_gemini: true, check_data_freshness: true }),
    }));
  }

  async function loadGaps() {
    await run("gaps", () => cfFetch(`/api/resource-gaps/${INCIDENT_ID}`));
  }

  async function loadSuppliers() {
    const resources = [
      { resource: "Burn kits", quantity: 240 },
      { resource: "Albuterol doses", quantity: 120 },
      { resource: "Oxygen cylinders", quantity: 36 },
    ];
    setLoad("suppliers", true); setErr("suppliers", null);
    try {
      const results = await Promise.all(
        resources.map(({ resource, quantity }) =>
          cfFetch(`/api/suppliers/search?resource=${encodeURIComponent(resource)}&quantity=${quantity}&destination=${HOSP_ID}`)
        )
      );
      setDat("suppliers", results);
    } catch (e) { setErr("suppliers", e.message); }
    finally { setLoad("suppliers", false); }
  }

  async function loadDispatch() {
    const r = await run("dispatch", () => cfFetch("/api/dispatch-plans/generate", {
      method: "POST",
      body: JSON.stringify({
        incident_id: INCIDENT_ID,
        target_hospital_id: HOSP_ID,
        include_briefing: false,
        include_ai_explanations: false,
      }),
    }));
    if (r?.data?.approval_requests?.[0]?.approval_id) {
      setApprovalId(r.data.approval_requests[0].approval_id);
    }
  }

  async function loadApproval() {
    const id = approvalId || "APR-001";
    await run("approval", () => cfFetch(`/api/approvals/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({
        approver_name: "EOC Commander",
        approver_role: "Emergency Operations Center",
        notes: "Approved under Level 4 wildfire emergency.",
      }),
    }));
  }

  async function loadSend() {
    await run("send", () => cfFetch("/api/dispatch-requests/send", {
      method: "POST",
      body: JSON.stringify({ approval_id: approvalId || "APR-001" }),
    }));
  }

  async function loadBriefing() {
    await run("briefing", () => cfFetch("/api/briefings/generate", {
      method: "POST",
      body: JSON.stringify({ incident_id: INCIDENT_ID, audience: "mayor" }),
    }));
  }

  async function loadPipeline() {
    await run("pipeline", () => cfFetch("/api/data-sources"));
  }

  useEffect(() => { loadDashboard(); }, []);

  const stepData = {
    dashboard: data.dashboard?.data,
    analysis: data.analysis?.data,
    gaps: data.gaps?.data,
    suppliers: data.suppliers,
    dispatch: data.dispatch?.data,
    approval: data.approval?.data,
    send: data.send?.data,
    briefing: data.briefing?.data,
    pipeline: data.pipeline?.data,
  };

  function navigate(id, loader) {
    setActiveStep(id);
    if (!stepData[id] && loader) loader();
  }

  return (
    <div style={{ fontFamily: "Inter, system-ui, sans-serif", background: "#070d1a", minHeight: "100vh", color: "#cbd5e1" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:.4; } }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #0a0e1a; } ::-webkit-scrollbar-thumb { background: #1e2d47; border-radius: 4px; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        table { border-collapse: collapse; width: 100%; }
        th { font-size: 11px; color: #4a5870; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; text-align: left; padding: 8px 12px; border-bottom: 1px solid #1e2d47; }
        td { font-size: 13px; color: #94a3b8; padding: 10px 12px; border-bottom: 1px solid #0f1826; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #0f1826; }
        pre { font-family: 'JetBrains Mono', monospace; font-size: 12px; background: #0a0f1c; border: 1px solid #1e2d47; border-radius: 6px; padding: 14px; color: #7dd3fc; overflow-x: auto; white-space: pre-wrap; line-height: 1.6; }
      `}</style>

      {/* Top bar */}
      <div style={{ background: "#0a0e1a", borderBottom: "1px solid #1e2d47", padding: "0 24px", display: "flex", alignItems: "center", gap: 16, height: 52 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#E24B4A", animation: "pulse 1.5s infinite" }} />
          <span style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", letterSpacing: "0.04em" }}>CRISISFLOW</span>
        </div>
        <span style={{ fontSize: 11, color: "#4a5870", fontFamily: "JetBrains Mono, monospace" }}>{INCIDENT_ID}</span>
        <Badge label="MARIN WILDFIRE" color="#E24B4A" />
        <Badge label="LEVEL 4" color="#EF9F27" />
        <span style={{ marginLeft: "auto", fontSize: 11, color: "#2d3d57" }}>
          {data.dashboard?.data_mode_used === "bigquery" ? "● BIGQUERY LIVE" : data.dashboard?.data_mode_used === "mock" ? "● MOCK DATA" : ""}
        </span>
      </div>

      <div style={{ display: "flex", height: "calc(100vh - 52px)", overflow: "hidden" }}>
        {/* Sidebar */}
        <nav style={{ width: 200, background: "#0a0e1a", borderRight: "1px solid #1e2d47", padding: "16px 0", flexShrink: 0, overflowY: "auto" }}>
          {STEPS.map((s, i) => {
            const active = activeStep === s.id;
            const loaders = { dashboard: loadDashboard, analysis: loadAnalysis, gaps: loadGaps, suppliers: loadSuppliers, dispatch: loadDispatch, approval: loadApproval, send: loadSend, briefing: loadBriefing, pipeline: loadPipeline };
            return (
              <button key={s.id} onClick={() => navigate(s.id, loaders[s.id])} style={{
                display: "flex", alignItems: "center", gap: 10, width: "100%", padding: "9px 16px",
                background: active ? "#131929" : "transparent", border: "none", cursor: "pointer",
                borderLeft: active ? "2px solid #F59E0B" : "2px solid transparent",
                color: active ? "#f1f5f9" : "#4a5870", fontSize: 12, fontWeight: active ? 600 : 400,
                textAlign: "left", transition: "all 0.1s",
              }}>
                <span style={{ fontSize: 10, color: active ? "#F59E0B" : "#2d3d57", fontFamily: "JetBrains Mono, monospace", width: 16 }}>{String(i + 1).padStart(2, "0")}</span>
                {s.label}
                {loading[s.id] && <span style={{ marginLeft: "auto", width: 10, height: 10, border: "1.5px solid #22D3EE44", borderTopColor: "#22D3EE", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />}
              </button>
            );
          })}
        </nav>

        {/* Main */}
        <main style={{ flex: 1, overflowY: "auto", padding: "24px" }}>
          {activeStep === "dashboard" && <DashboardPage d={stepData.dashboard} loading={loading.dashboard} error={errors.dashboard} onAnalyze={() => navigate("analysis", loadAnalysis)} />}
          {activeStep === "analysis" && <AnalysisPage d={stepData.analysis} loading={loading.analysis} error={errors.analysis} onNext={() => navigate("gaps", loadGaps)} />}
          {activeStep === "gaps" && <GapsPage d={stepData.gaps} loading={loading.gaps} error={errors.gaps} onNext={() => navigate("suppliers", loadSuppliers)} />}
          {activeStep === "suppliers" && <SuppliersPage d={stepData.suppliers} loading={loading.suppliers} error={errors.suppliers} onNext={() => navigate("dispatch", loadDispatch)} />}
          {activeStep === "dispatch" && <DispatchPage d={stepData.dispatch} loading={loading.dispatch} error={errors.dispatch} approvalId={approvalId} onNext={() => navigate("approval", loadApproval)} />}
          {activeStep === "approval" && <ApprovalPage d={stepData.approval} loading={loading.approval} error={errors.approval} approvalId={approvalId} onNext={() => navigate("send", loadSend)} />}
          {activeStep === "send" && <SendPage d={stepData.send} loading={loading.send} error={errors.send} onNext={() => navigate("briefing", loadBriefing)} />}
          {activeStep === "briefing" && <BriefingPage d={stepData.briefing} loading={loading.briefing} error={errors.briefing} onNext={() => navigate("pipeline", loadPipeline)} />}
          {activeStep === "pipeline" && <PipelinePage d={stepData.pipeline} loading={loading.pipeline} error={errors.pipeline} />}
        </main>
      </div>
    </div>
  );
}

function LoadState({ loading, error, onRetry }) {
  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "40px 0", color: "#4a5870" }}>
      <span style={{ width: 20, height: 20, border: "2px solid #1e2d47", borderTopColor: "#22D3EE", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
      <span style={{ fontSize: 13 }}>Fetching from CrisisFlow API...</span>
    </div>
  );
  if (error) return (
    <div style={{ background: "#E24B4A11", border: "1px solid #E24B4A33", borderRadius: 8, padding: "16px", margin: "16px 0" }}>
      <div style={{ fontSize: 13, color: "#E24B4A", marginBottom: 8 }}>API Error: {error}</div>
      {onRetry && <Btn onClick={onRetry} variant="danger" small>Retry</Btn>}
    </div>
  );
  return null;
}

function JsonViewer({ data, title }) {
  const [open, setOpen] = useState(false);
  if (!data) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <button onClick={() => setOpen(o => !o)} style={{ fontSize: 11, color: "#4a5870", background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ transform: open ? "rotate(90deg)" : "none", display: "inline-block", transition: "0.15s" }}>▶</span>
        {title || "Raw API response"}
      </button>
      {open && <pre style={{ marginTop: 8 }}>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}

// ---- Pages ----

function DashboardPage({ d, loading, error, onAnalyze }) {
  const surge = d?.patient_surge_summary ?? d?.surge_summary ?? {
    total: d?.summary?.projected_patients,
  };
  const severity = d?.incident?.severity ?? d?.severity ?? "critical";
  const dataSources = d?.data_sources ?? [];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Command Center</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>Emergency operational picture — {INCIDENT_ID}</p>
        </div>
        <div style={{ marginLeft: "auto" }}>
          <Btn onClick={onAnalyze}>Analyze Incident →</Btn>
        </div>
      </div>

      <LoadState loading={loading} error={error} />

      {d && (
        <>
          <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
              <div>
                <div style={{ fontSize: 11, color: "#4a5870", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Active Incident</div>
                <div style={{ fontSize: 18, fontWeight: 700, color: "#f1f5f9" }}>{d.incident?.name ?? d.name ?? "Marin County Wildfire"}</div>
                <div style={{ fontSize: 13, color: "#6b7fa3", marginTop: 4 }}>{d.incident?.type ?? "Wildfire"} · {d.incident?.location_name ?? d.incident?.affected_area ?? d.affected_area ?? "Marin County, CA"}</div>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <Badge label={severity} color={SEVERITY_COLOR[severity] ?? "#E24B4A"} />
                <Badge label="ACTIVE" color="#1D9E75" />
              </div>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12, marginBottom: 20 }}>
            <StatCard label="Total Surge" value={surge?.total ?? 180} color="#F59E0B" />
            <StatCard label="Burns" value={surge?.burns ?? 35} color="#E24B4A" />
            <StatCard label="Smoke Inhalation" value={surge?.smoke_inhalation ?? 80} color="#EF9F27" />
            <StatCard label="Trauma" value={surge?.trauma ?? 28} color="#EA580C" />
            <StatCard label="ICU Risk" value={surge?.icu_risk ?? 12} color="#E24B4A" />
          </div>

          {(d.resource_gaps ?? d.top_resource_gaps) && (
            <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
              <SectionHeader icon="⚠" title="Top Resource Gaps" />
              <table>
                <thead><tr><th>Resource</th><th>Gap</th><th>Status</th></tr></thead>
                <tbody>
                  {(d.resource_gaps ?? d.top_resource_gaps ?? []).slice(0, 5).map((g, i) => (
                    <tr key={i}>
                      <td style={{ color: "#e2e8f0" }}>{g.resource ?? g.name}</td>
                      <td style={{ color: "#E24B4A", fontFamily: "JetBrains Mono, monospace" }}>−{g.gap ?? g.shortage}</td>
                      <td><Badge label="CRITICAL" color="#E24B4A" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {(d.data_source_health || dataSources.length > 0) && (
            <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px" }}>
              <SectionHeader icon="🔗" title="Data Sources" />
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                {d.data_source_health
                  ? Object.entries(d.data_source_health).map(([k, v]) => (
                    <span key={k} style={{ fontSize: 11, background: "#131929", border: "1px solid #1e2d47", borderRadius: 6, padding: "4px 10px", color: v === "healthy" || v === "connected" ? "#1D9E75" : "#EF9F27" }}>
                      {k}: {v}
                    </span>
                  ))
                  : dataSources.map((source) => (
                    <span key={source.connector_id ?? source.source_name} style={{ fontSize: 11, background: "#131929", border: "1px solid #1e2d47", borderRadius: 6, padding: "4px 10px", color: source.setup_state === "connected" || source.used_by_agent ? "#1D9E75" : "#EF9F27" }}>
                      {source.service ?? source.source_name}: {source.sync_state ?? source.status}
                    </span>
                  ))}
              </div>
            </div>
          )}
          <JsonViewer data={d} title="Full dashboard payload" />
        </>
      )}
    </div>
  );
}

function AnalysisPage({ d, loading, error, onNext }) {
  const surge = d?.patient_surge ?? d?.surge_breakdown ?? {};
  const SURGE = [
    { label: "Burns", value: 35, color: "#E24B4A" },
    { label: "Smoke Inhalation", value: 80, color: "#EF9F27" },
    { label: "Trauma", value: 28, color: "#EA580C" },
    { label: "ICU Risk", value: 12, color: "#9333ea" },
    { label: "Observation", value: 25, color: "#378ADD" },
  ];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Agent Analysis</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>AI incident analysis · Gemini-powered</p>
        </div>
        {d && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>View Resource Gaps →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      {(d || loading === false) && (
        <>
          <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
            <SectionHeader icon="🤖" title="Patient Surge Forecast" meta="Model: Gemini Flash" />
            <StatCard label="Total Projected Patients" value={surge.total ?? d?.total_surge ?? 180} color="#F59E0B" sub="Next 4 hours" />
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: 10, marginTop: 12 }}>
              {SURGE.map(s => <StatCard key={s.label} label={s.label} value={surge[s.label.toLowerCase().replace(" ", "_")] ?? s.value} color={s.color} />)}
            </div>
          </div>
          {(d?.recommendation ?? d?.agent_recommendation ?? d?.agent_summary) && (
            <div style={{ background: "#0a1f14", border: "1px solid #1D9E7544", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
              <SectionHeader icon="💡" title="Agent Recommendation" />
              <p style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.7 }}>{d.recommendation ?? d.agent_recommendation ?? d.agent_summary}</p>
            </div>
          )}
          {d && <JsonViewer data={d} title="Full analysis payload" />}
          <div style={{ marginTop: 20 }}>
            <Btn onClick={onNext}>View Resource Gaps →</Btn>
          </div>
        </>
      )}
    </div>
  );
}

function GapsPage({ d, loading, error, onNext }) {
  const FALLBACK = [
    { resource: "Burn kits", needed: 420, available: 180, gap: 240 },
    { resource: "Albuterol doses", needed: 300, available: 180, gap: 120 },
    { resource: "Oxygen cylinders", needed: 90, available: 54, gap: 36 },
    { resource: "ICU beds", needed: 12, available: 7, gap: 5 },
    { resource: "ER nurses", needed: 28, available: 20, gap: 8 },
  ];
  const gaps = d?.gaps ?? d?.resource_gaps ?? FALLBACK;
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Resource Gaps</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>Deterministic shortage calculation — not AI-generated</p>
        </div>
        {(d || !loading) && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Find Suppliers →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
        <SectionHeader icon="📊" title="Shortfall by Resource" meta={`Target: ${HOSP_ID}`} />
        <table>
          <thead><tr><th>Resource</th><th>Needed</th><th>Available</th><th>Gap</th><th>Fill Rate</th></tr></thead>
          <tbody>
            {gaps.map((g, i) => {
              const needed = g.needed ?? g.required ?? 0;
              const available = g.available ?? g.on_hand ?? 0;
              const gap = g.gap ?? g.shortage ?? Math.max(0, needed - available);
              const fill = needed > 0 ? Math.round((available / needed) * 100) : 0;
              return (
                <tr key={i}>
                  <td style={{ color: "#e2e8f0", fontWeight: 500 }}>{g.resource ?? g.name}</td>
                  <td style={{ fontFamily: "JetBrains Mono, monospace" }}>{needed}</td>
                  <td style={{ fontFamily: "JetBrains Mono, monospace", color: "#1D9E75" }}>{available}</td>
                  <td style={{ fontFamily: "JetBrains Mono, monospace", color: "#E24B4A", fontWeight: 600 }}>−{gap}</td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ flex: 1, height: 4, background: "#1e2d47", borderRadius: 2, overflow: "hidden" }}>
                        <div style={{ width: `${fill}%`, height: "100%", background: fill < 50 ? "#E24B4A" : fill < 75 ? "#EF9F27" : "#1D9E75", transition: "width 0.6s" }} />
                      </div>
                      <span style={{ fontSize: 11, color: "#6b7fa3", minWidth: 28 }}>{fill}%</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {d && <JsonViewer data={d} title="Full gaps payload" />}
      <div style={{ marginTop: 20 }}>
        <Btn onClick={onNext}>Find Suppliers →</Btn>
      </div>
    </div>
  );
}

function SuppliersPage({ d, loading, error, onNext }) {
  const resources = ["Burn kits", "Albuterol doses", "Oxygen cylinders"];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Supplier Ranking</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>ETA + route risk scoring across pre-vetted vendors</p>
        </div>
        {d && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Generate Dispatch Plan →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      {d && d.map((result, ri) => {
        const payload = result?.data ?? {};
        const suppliers = payload.candidates ?? payload.suppliers ?? (Array.isArray(payload) ? payload : []);
        return (
          <div key={ri} style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 16 }}>
            <SectionHeader icon="🏭" title={resources[ri]} meta={`${suppliers.length} suppliers found`} />
            <table>
              <thead><tr><th>Supplier</th><th>Qty</th><th>ETA</th><th>Route Risk</th><th>Contract</th><th>Score</th><th></th></tr></thead>
              <tbody>
                {suppliers.slice(0, 4).map((s, i) => (
                  <tr key={i}>
                    <td style={{ color: "#e2e8f0", fontWeight: 500 }}>{s.name ?? s.supplier_name}</td>
                    <td style={{ fontFamily: "JetBrains Mono, monospace" }}>{s.available_quantity ?? s.available ?? s.quantity ?? "—"}</td>
                    <td style={{ fontFamily: "JetBrains Mono, monospace", color: "#22D3EE" }}>{s.eta_minutes ?? s.eta_min ?? s.eta}m</td>
                    <td><Badge label={s.route_risk ?? "low"} color={(s.route_risk ?? "").toLowerCase() === "high" ? "#E24B4A" : (s.route_risk ?? "").toLowerCase() === "medium" ? "#EF9F27" : "#1D9E75"} /></td>
                    <td style={{ fontSize: 11, color: "#6b7fa3" }}>{s.contract_status ?? "active"}</td>
                    <td style={{ fontFamily: "JetBrains Mono, monospace", color: "#F59E0B", fontWeight: 600 }}>{typeof s.score === "number" ? s.score.toFixed(1) : s.score ?? "—"}</td>
                    <td>{(s.recommendation === "Best" || i === 0) && <Badge label="BEST" color="#1D9E75" />}{s.recommendation === "Backup" && <Badge label="BACKUP" color="#378ADD" />}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })}
      <div style={{ marginTop: 8 }}>
        <Btn onClick={onNext}>Generate Dispatch Plan →</Btn>
      </div>
    </div>
  );
}

function DispatchPage({ d, loading, error, approvalId, onNext }) {
  const recs = d?.recommendations ?? d?.dispatch_recommendations ?? d?.approval_requests ?? [];
  const FALLBACK = [
    "Transfer burn kits from MedSupply Oakland to SF General",
    "Transfer albuterol from UCSF Storage to SF General",
    "Dispatch oxygen cylinders from NorCal Oxygen to SF General",
    "Divert low-acuity patients to UCSF/CPMC",
    "Place BayMed Logistics on standby",
  ];
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Dispatch Plan</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>Approval-ready action set — awaiting EOC sign-off</p>
        </div>
        {(d || !loading) && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Approve →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
        <SectionHeader icon="📋" title="Recommended Actions" meta="Human approval required" />
        {(recs.length > 0 ? recs : FALLBACK).map((item, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "12px 0", borderBottom: i < (recs.length > 0 ? recs.length : FALLBACK.length) - 1 ? "1px solid #0f1826" : "none" }}>
            <span style={{ width: 22, height: 22, background: "#131929", border: "1px solid #1e2d47", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#F59E0B", flexShrink: 0, fontFamily: "JetBrains Mono, monospace", fontWeight: 600 }}>{i + 1}</span>
            <div>
              <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 500 }}>{typeof item === "string" ? item : (item.action ?? item.description ?? item.recommendation ?? JSON.stringify(item))}</div>
              {typeof item === "object" && item.resource && <div style={{ fontSize: 11, color: "#4a5870", marginTop: 3 }}>{item.resource} · {item.quantity} units</div>}
            </div>
            <Badge label="PENDING" color="#EF9F27" />
          </div>
        ))}
      </div>
      {approvalId && (
        <div style={{ background: "#0a1f14", border: "1px solid #1D9E7544", borderRadius: 8, padding: "12px 16px", marginBottom: 20, fontSize: 12, color: "#1D9E75", fontFamily: "JetBrains Mono, monospace" }}>
          Approval ID captured: {approvalId}
        </div>
      )}
      {d && <JsonViewer data={d} title="Full dispatch payload" />}
      <div style={{ marginTop: 20 }}>
        <Btn onClick={onNext}>Approve Plan →</Btn>
      </div>
    </div>
  );
}

function ApprovalPage({ d, loading, error, approvalId, onNext }) {
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Approval Queue</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>AI does not autonomously move emergency resources</p>
        </div>
        {(d || !loading) && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Send Dispatch →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      <div style={{ background: "#0a1a28", border: "1px solid #22D3EE33", borderRadius: 10, padding: "20px", marginBottom: 20 }}>
        <div style={{ fontSize: 11, color: "#22D3EE", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>Approval Authority</div>
        <div style={{ fontSize: 16, fontWeight: 600, color: "#f1f5f9" }}>EOC Commander</div>
        <div style={{ fontSize: 12, color: "#6b7fa3", marginTop: 4 }}>Emergency Operations Center</div>
        <div style={{ marginTop: 12, fontSize: 12, color: "#94a3b8", fontStyle: "italic" }}>"Approved under Level 4 wildfire emergency."</div>
      </div>
      {(d || !loading) && (
        <div style={{ background: "#0a1f14", border: "1px solid #1D9E7544", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
            <span style={{ fontSize: 20 }}>✅</span>
            <span style={{ fontSize: 15, fontWeight: 600, color: "#1D9E75" }}>Approved</span>
            <Badge label={d?.status ?? "approved"} color="#1D9E75" />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <div style={{ fontSize: 11, color: "#4a5870", marginBottom: 4 }}>Approval ID</div>
              <div style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace", color: "#22D3EE" }}>{d?.approval_id ?? approvalId ?? "APR-001"}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: "#4a5870", marginBottom: 4 }}>Next Action</div>
              <div style={{ fontSize: 12, color: "#e2e8f0" }}>{d?.next_action ?? "dispatch_request_ready"}</div>
            </div>
          </div>
        </div>
      )}
      {d && <JsonViewer data={d} title="Full approval payload" />}
      <div style={{ marginTop: 20 }}>
        <Btn onClick={onNext}>Send Dispatch Request →</Btn>
      </div>
    </div>
  );
}

function SendPage({ d, loading, error, onNext }) {
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Dispatch Request</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>Final request transmitted to supplier</p>
        </div>
        {(d || !loading) && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Generate Briefing →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      {d && (
        <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "20px", marginBottom: 20 }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
            {[
              ["Dispatch ID", d.dispatch_request_id ?? d.id ?? "DR-001", "#22D3EE"],
              ["Supplier", d.supplier ?? "MedSupply Oakland", "#e2e8f0"],
              ["Destination", d.destination ?? HOSP_ID, "#e2e8f0"],
              ["Resource", d.resource ?? "Burn kits", "#e2e8f0"],
              ["Quantity", d.quantity ?? 240, "#F59E0B"],
              ["ETA", `${d.eta_minutes ?? d.eta ?? 45} min`, "#22D3EE"],
              ["Contact Method", d.contact_method ?? "API", "#e2e8f0"],
              ["Confirmation", d.supplier_confirmation_status ?? d.confirmation ?? "accepted", "#1D9E75"],
            ].map(([label, value, color]) => (
              <div key={label} style={{ background: "#131929", borderRadius: 8, padding: "12px 14px" }}>
                <div style={{ fontSize: 11, color: "#4a5870", marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 13, color, fontFamily: typeof value === "number" || label.includes("ID") || label.includes("ETA") ? "JetBrains Mono, monospace" : "inherit", fontWeight: 500 }}>{value}</div>
              </div>
            ))}
          </div>
          {d.emergency_dispatch_message && (
            <div style={{ background: "#0a0f1c", border: "1px solid #1e2d47", borderRadius: 6, padding: "14px", fontSize: 12, color: "#94a3b8", lineHeight: 1.7 }}>
              <div style={{ fontSize: 10, color: "#4a5870", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.1em" }}>Dispatch Message</div>
              {d.emergency_dispatch_message}
            </div>
          )}
        </div>
      )}
      {d && <JsonViewer data={d} title="Full dispatch request payload" />}
      <div style={{ marginTop: 20 }}>
        <Btn onClick={onNext}>Generate Mayor Briefing →</Btn>
      </div>
    </div>
  );
}

function BriefingPage({ d, loading, error, onNext }) {
  const text = d?.body ?? d?.briefing ?? d?.content ?? d?.text ?? "";
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Briefing Generator</h1>
          <p style={{ fontSize: 12, color: "#4a5870" }}>Gemini-generated executive communication — audience: Mayor</p>
        </div>
        {(d || !loading) && <Btn onClick={onNext} style={{ marginLeft: "auto" }}>Data Pipeline →</Btn>}
      </div>
      <LoadState loading={loading} error={error} />
      {d && (
        <>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
            <Badge label={`Generated by: ${d.generated_by ?? "Gemini"}`} color="#22D3EE" />
            {d.audience && <Badge label={`Audience: ${d.audience}`} color="#6366f1" />}
            {d.data_used && <Badge label={`Data: ${Array.isArray(d.data_used) ? d.data_used.join(", ") : d.data_used}`} color="#4a5870" />}
          </div>
          <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "24px", marginBottom: 20, lineHeight: 1.8, fontSize: 13, color: "#94a3b8", whiteSpace: "pre-wrap" }}>
            {d.title && <div style={{ fontSize: 16, fontWeight: 700, color: "#f1f5f9", marginBottom: 12 }}>{d.title}</div>}
            {text || <span style={{ color: "#4a5870" }}>No briefing text returned. Check raw payload below.</span>}
          </div>
          {d.approval_note && (
            <div style={{ fontSize: 11, color: "#4a5870", fontStyle: "italic", marginBottom: 16 }}>{d.approval_note}</div>
          )}
          <JsonViewer data={d} title="Full briefing payload" />
        </>
      )}
      <div style={{ marginTop: 20 }}>
        <Btn onClick={onNext}>View Data Pipeline →</Btn>
      </div>
    </div>
  );
}

function PipelinePage({ d, loading, error }) {
  const sources = d?.sources ?? d?.data_sources ?? d ?? [];
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", marginBottom: 4 }}>Data Pipeline</h1>
        <p style={{ fontSize: 12, color: "#4a5870" }}>Google Sheets → Fivetran → BigQuery live connector health</p>
      </div>
      <LoadState loading={loading} error={error} />

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {["Google Sheets", "→", "Fivetran", "→", "BigQuery", "→", "CrisisFlow API"].map((s, i) => (
          s === "→" ? <span key={i} style={{ color: "#1e2d47", fontSize: 18 }}>→</span> : (
            <span key={i} style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 6, padding: "6px 12px", fontSize: 12, color: "#22D3EE", fontWeight: 500 }}>{s}</span>
          )
        ))}
      </div>

      {(Array.isArray(sources) && sources.length > 0) ? (
        <div style={{ background: "#0f1826", border: "1px solid #1e2d47", borderRadius: 10, padding: "18px 20px", marginBottom: 20 }}>
          <SectionHeader icon="🔄" title="Connector Status" />
          <table>
            <thead><tr><th>Source</th><th>Last Sync</th><th>Status</th><th>Used By Agent</th></tr></thead>
            <tbody>
              {sources.map((s, i) => (
                <tr key={i}>
                  <td style={{ color: "#e2e8f0", fontWeight: 500 }}>{s.name ?? s.source_name ?? s.source}</td>
                  <td style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 11 }}>{s.last_sync ?? s.last_synced ?? s.freshness ?? "—"}</td>
                  <td><Badge label={s.status ?? s.connector_status ?? "active"} color={s.status === "error" ? "#E24B4A" : "#1D9E75"} /></td>
                  <td style={{ color: s.used_by_agent ? "#1D9E75" : "#4a5870" }}>{s.used_by_agent ? "Yes" : (s.used_by_agent === false ? "No" : "—")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : d ? (
        <JsonViewer data={d} title="Raw pipeline data" />
      ) : null}

      <div style={{ background: "#0a0e1a", border: "1px solid #1e2d47", borderRadius: 10, padding: "20px", marginTop: 8 }}>
        <div style={{ fontSize: 11, color: "#4a5870", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>Demo Infrastructure</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 10 }}>
          {[
            ["Data Source", "Google Sheets", "#378ADD"],
            ["ETL", "Fivetran", "#6366f1"],
            ["Warehouse", "BigQuery + _fivetran_synced", "#22D3EE"],
            ["AI", "Gemini Flash", "#F59E0B"],
            ["Backend", "Cloud Run (GCP)", "#1D9E75"],
          ].map(([label, value, color]) => (
            <div key={label} style={{ background: "#131929", borderRadius: 8, padding: "12px 14px" }}>
              <div style={{ fontSize: 10, color: "#4a5870", marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 12, color, fontWeight: 500 }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: 20, fontSize: 11, color: "#2d3d57" }}>
        Scenario data is simulated for the hackathon; the cloud data pipeline, API, and Gemini briefing generation are live.
      </div>
    </div>
  );
}
