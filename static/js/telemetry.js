/**
 * Telemetry & Cost Dashboard:
 * Aggregates TTFT, TTFA, turn latency, and cost-per-minute metrics across sessions.
 */

async function loadTelemetry() {
  const container = document.getElementById("sessionsList");
  const badge = document.getElementById("telemetryBadge");
  if (!container) return;

  try {
    const res = await fetch("/telemetry");
    const data = await res.json();
    if (badge) badge.innerText = data.length || 0;

    if (!data || data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          No session logs recorded yet.<br />
          Complete a voice call to capture live latency and cost metrics.
        </div>`;
      return;
    }

    // Aggregate overall KPIs
    let totalTTFT = 0, ttftCount = 0;
    let totalTTFA = 0, ttfaCount = 0;
    let totalTurn = 0, turnCount = 0;
    let totalCostMinINR = 0;

    data.forEach((s) => {
      if (s.latency_ms?.ttft?.avg) { totalTTFT += s.latency_ms.ttft.avg; ttftCount++; }
      if (s.latency_ms?.ttfa?.avg) { totalTTFA += s.latency_ms.ttfa.avg; ttfaCount++; }
      if (s.latency_ms?.voice_to_voice_turn?.avg) { totalTurn += s.latency_ms.voice_to_voice_turn.avg; turnCount++; }
      if (s.economics?.cost_per_minute_inr) {
        totalCostMinINR += s.economics.cost_per_minute_inr;
      }
    });

    const kpiTtft = document.getElementById("kpi-ttft");
    const kpiTtfa = document.getElementById("kpi-ttfa");
    const kpiTurn = document.getElementById("kpi-turn");
    const kpiCost = document.getElementById("kpi-cost");

    if (kpiTtft) kpiTtft.innerText = ttftCount ? `${Math.round(totalTTFT / ttftCount)} ms` : "-- ms";
    if (kpiTtfa) kpiTtfa.innerText = ttfaCount ? `${Math.round(totalTTFA / ttfaCount)} ms` : "-- ms";
    if (kpiTurn) kpiTurn.innerText = turnCount ? `${Math.round(totalTurn / turnCount)} ms` : "-- ms";
    if (kpiCost) kpiCost.innerText = data.length ? `₹${(totalCostMinINR / data.length).toFixed(2)}/min` : "--";

    // Render sessions list
    container.innerHTML = data
      .slice()
      .reverse()
      .map((s) => {
        const timeStr = s.timestamp ? new Date(s.timestamp).toLocaleTimeString() : "";
        const ttft = s.latency_ms?.ttft?.avg ? `${Math.round(s.latency_ms.ttft.avg)}ms` : "--";
        const ttfa = s.latency_ms?.ttfa?.avg ? `${Math.round(s.latency_ms.ttfa.avg)}ms` : "--";
        const turn = s.latency_ms?.voice_to_voice_turn?.avg ? `${Math.round(s.latency_ms.voice_to_voice_turn.avg)}ms` : "--";
        const cost = s.economics?.total_cost_usd !== undefined ? `$${s.economics.total_cost_usd.toFixed(4)} (₹${s.economics.total_cost_inr?.toFixed(2) || '0.00'})` : "--";

        return `
          <div class="session-card">
            <div class="session-top">
              <div class="session-id">Room: ${escapeHtml(s.session_id)} ${timeStr ? `• ${timeStr}` : ""}</div>
              <span class="session-cost">${cost}</span>
            </div>
            <div class="session-models">
              ${escapeHtml(s.models?.stt || "deepgram")} • ${escapeHtml(s.models?.llm || "groq")} • ${escapeHtml(s.models?.tts || "cartesia")}
            </div>
            <div class="session-stats">
              <span>Turns: <strong>${s.turns_count || 0}</strong></span>
              <span>TTFT: <strong>${ttft}</strong></span>
              <span>TTFA: <strong>${ttfa}</strong></span>
              <span>Turn: <strong>${turn}</strong></span>
              <span>Duration: <strong>${Math.round(s.duration_seconds || 0)}s</strong></span>
            </div>
          </div>`;
      })
      .join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Failed to load telemetry: ${err.message}</div>`;
  }
}
