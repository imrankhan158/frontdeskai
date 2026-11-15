/**
 * Model Benchmark Leaderboard & Evaluation Reports:
 * Pure analytics & comparison dashboard.
 * Displays side-by-side model metrics, latency waterfall, failure filters, and audit reports.
 */

let _activeRunId = null;
let _latestRunId = null;
let _cachedHistory = [];
let _activeReportData = null;
let _currentFilter = "ALL"; // 'ALL' | 'FAIL' | 'PASS'

async function loadEvals() {
  await loadEvalRun(null);
}

/**
 * Loads either the latest evaluation report (if runId is null/latest)
 * or a specific historical run snapshot for side-by-side inspection.
 */
async function loadEvalRun(runId) {
  const container = document.getElementById("evalsList");
  if (!container) return;

  try {
    let url = "/evals";
    const isHistorical = runId && runId !== "latest" && runId !== _latestRunId;
    if (isHistorical) {
      url = `/evals/run/${encodeURIComponent(runId)}`;
    }

    const res = await fetch(url);
    const data = await res.json();

    if (!data || !data.results) {
      container.innerHTML = `<div class="empty-state">No evaluation report found. Run evaluations via CLI: <code>uv run python -m src.eval_runner</code></div>`;
      return;
    }

    _activeReportData = data;
    _activeRunId = data.run_id;
    if (!isHistorical) {
      _latestRunId = data.run_id;
    }

    // Always fetch canonical full history from /evals/history so all models (Qwen, GPT-OSS, etc.) remain visible
    try {
      const hRes = await fetch("/evals/history");
      const fullHistory = await hRes.json();
      if (Array.isArray(fullHistory) && fullHistory.length > 0) {
        _cachedHistory = fullHistory;
        if (!_latestRunId && _cachedHistory.length > 0) {
          _latestRunId = _cachedHistory[_cachedHistory.length - 1].run_id;
        }
      }
    } catch (e) {
      if (Array.isArray(data.history) && _cachedHistory.length === 0) {
        _cachedHistory = data.history;
      }
    }

    // 1. Update KPI Cards
    updateEvalKpis(data.summary || {}, data.results || []);

    // 2. Update Waterfall Chart for the inspected model
    updateWaterfall(data);

    // 3. Update Version Badge & Historical Banner
    const versionBadge = document.getElementById("currentVersionBadge");
    if (versionBadge) {
      const isLatest = _activeRunId === _latestRunId;
      versionBadge.innerText = `${data.version || "v1.0"} • ${data.model || "default"}${isLatest ? " (Latest)" : " (Historical)"}`;
      versionBadge.style.background = isLatest ? "#e0e7ff" : "#fef3c7";
      versionBadge.style.color = isLatest ? "#3730a3" : "#92400e";
    }

    const histBanner = document.getElementById("historicalBanner");
    const histBannerText = document.getElementById("historicalBannerText");
    if (histBanner) {
      if (_activeRunId && _latestRunId && _activeRunId !== _latestRunId) {
        histBanner.style.display = "flex";
        if (histBannerText) {
          const timeStr = data.timestamp ? new Date(data.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";
          histBannerText.innerText = `${data.version || "Historical"} • ${data.model || ""} (Recorded at ${timeStr})`;
        }
      } else {
        histBanner.style.display = "none";
      }
    }

    // 4. Render All Generated Reports Comparison Matrix (Leaderboard)
    renderHistoryTable(_cachedHistory, _activeRunId, _latestRunId);
    populateHistoryDropdown(_cachedHistory, _activeRunId, _latestRunId);

    // 5. Render Filterable Test Cases
    renderFilteredEvalCards();

  } catch (err) {
    container.innerHTML = `<div class="empty-state">Failed to load evaluations: ${err.message}</div>`;
  }
}

function updateEvalKpis(summary, results) {
  const kpiPass = document.getElementById("eval-kpi-pass");
  const kpiDev = document.getElementById("eval-kpi-dev");
  const kpiTotal = document.getElementById("eval-kpi-total");
  const kpiTtft = document.getElementById("eval-kpi-ttft");

  if (kpiPass) {
    kpiPass.innerText = summary.pass_rate_pct !== undefined ? `${summary.pass_rate_pct.toFixed(1)}%` : "--%";
  }
  if (kpiDev) {
    kpiDev.innerText = summary.avg_deviation_pct !== undefined ? `${summary.avg_deviation_pct.toFixed(1)}%` : "--%";
  }
  if (kpiTotal) {
    kpiTotal.innerText = summary.total_tests || results.length;
  }

  const avgTTFT = results.length
    ? Math.round(results.reduce((acc, r) => acc + (r.ttft_ms || 0), 0) / results.length)
    : (summary.avg_ttft_ms ? Math.round(summary.avg_ttft_ms) : 0);
  if (kpiTtft) {
    kpiTtft.innerText = avgTTFT ? `${avgTTFT} ms` : "-- ms";
  }
}

function updateWaterfall(data) {
  const modelNameSpan = document.getElementById("waterfallModelName");
  const totalTurnSpan = document.getElementById("waterfallTotalTurn");
  const groqVal = document.getElementById("waterfall-groq-val");
  const groqBar = document.getElementById("waterfall-groq-bar");

  const bm = data.benchmark || {};
  const ttft = bm.avg_ttft_ms || (data.summary ? data.summary.avg_ttft_ms : 300);
  const turnLatency = bm.voice_turn_latency_ms || Math.round(150 + 180 + ttft + 100 + 40);

  if (modelNameSpan) modelNameSpan.innerText = data.model || "Active Model";
  if (totalTurnSpan) totalTurnSpan.innerText = `Turn: ~${Math.round(turnLatency)} ms`;
  if (groqVal) groqVal.innerText = `${Math.round(ttft)} ms`;
  if (groqBar) {
    const pct = Math.min(Math.max(Math.round((ttft / turnLatency) * 100), 10), 65);
    groqBar.style.width = `${pct}%`;
  }
}

function renderHistoryTable(historyList, activeRunId, latestRunId) {
  const historyTable = document.getElementById("evalsHistoryTable");
  if (!historyTable) return;

  if (!historyList || historyList.length === 0) {
    historyTable.innerHTML = `<div style="font-size: 12px; color: #9ca3af;">No generated benchmark reports found.</div>`;
    return;
  }

  const rows = historyList
    .slice()
    .reverse()
    .map((h) => {
      const isLatest = h.run_id === latestRunId || (!latestRunId && h === historyList[historyList.length - 1]);
      const isActive = h.run_id === activeRunId;
      const timeStr = h.timestamp
        ? new Date(h.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
        : "--";
      const passPct = h.summary?.pass_rate_pct !== undefined ? `${h.summary.pass_rate_pct}%` : "--";
      const ttftStr = h.summary?.avg_ttft_ms ? `${Math.round(h.summary.avg_ttft_ms)}ms` : "--";
      const turnStr = h.summary?.voice_turn_latency_ms ? `${Math.round(h.summary.voice_turn_latency_ms)}ms` : "--";

      return `
        <tr class="history-row ${isActive ? "active-run" : ""}" onclick="loadEvalRun('${h.run_id}')" style="border-bottom: 1px solid #f3f4f6;">
          <td style="padding: 8px 10px;">
            <span class="badge-pill" style="font-size: 11px; background: ${isActive ? "#2563eb" : isLatest ? "#3b82f6" : "#e2e8f0"}; color: ${isActive || isLatest ? "#fff" : "#475569"};">
              ${escapeHtml(h.version || "v1.0")}
            </span>
            ${isActive ? '<span style="font-size: 10px; color: #2563eb; font-weight: 700; margin-left: 4px;">ACTIVE</span>' : isLatest ? '<span style="font-size: 10px; color: #16a34a; font-weight: 600; margin-left: 4px;">LATEST</span>' : ''}
          </td>
          <td style="padding: 8px 10px; font-family: ui-monospace, monospace; color: #1e293b; font-size: 12px; font-weight: 600;">${escapeHtml(h.model || "--")}</td>
          <td style="padding: 8px 10px; font-weight: 600; color: ${h.summary?.pass_rate_pct === 100 ? "#166534" : "#b45309"};">${passPct}</td>
          <td style="padding: 8px 10px; font-family: ui-monospace, monospace;">${ttftStr}</td>
          <td style="padding: 8px 10px; font-family: ui-monospace, monospace; font-weight: 600;">${turnStr}</td>
          <td style="padding: 8px 10px; color: #64748b; font-size: 11px;">${timeStr}</td>
          <td style="padding: 8px 10px; text-align: right;" onclick="event.stopPropagation()">
            <div style="display: inline-flex; gap: 4px;">
              <button class="btn-inspect ${isActive ? "active-view" : ""}" onclick="loadEvalRun('${h.run_id}')" title="Inspect test cases">
                ${isActive ? "✅ Inspecting" : "👁️ Compare"}
              </button>
              <button class="btn-inspect" onclick="viewMarkdownReport('${h.run_id}')" title="View Markdown Report">
                📄 MD
              </button>
            </div>
          </td>
        </tr>`;
    })
    .join("");

  historyTable.innerHTML = `
    <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">
      <thead>
        <tr style="border-bottom: 2px solid #e2e8f0; color: #64748b; font-weight: 600; font-size: 11px; text-transform: uppercase;">
          <th style="padding: 7px 10px;">Version</th>
          <th style="padding: 7px 10px;">Model</th>
          <th style="padding: 7px 10px;">Pass Rate</th>
          <th style="padding: 7px 10px;">Avg TTFT</th>
          <th style="padding: 7px 10px;">Voice Turn</th>
          <th style="padding: 7px 10px;">Recorded Time</th>
          <th style="padding: 7px 10px; text-align: right;">Action</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
}

function populateHistoryDropdown(historyList, activeRunId, latestRunId) {
  const select = document.getElementById("historyVersionDropdown");
  if (!select) return;

  if (!historyList || historyList.length === 0) {
    select.innerHTML = `<option value="">No reports available</option>`;
    return;
  }

  const options = historyList
    .slice()
    .reverse()
    .map((h) => {
      const isLatest = h.run_id === latestRunId;
      const isSelected = h.run_id === activeRunId;
      const label = `${h.version || "v1.0"} • ${h.model} ${isLatest ? "(Latest)" : ""}`;
      return `<option value="${h.run_id}" ${isSelected ? "selected" : ""}>${escapeHtml(label)}</option>`;
    })
    .join("");

  select.innerHTML = options;
}

function setTestFilter(filter) {
  _currentFilter = filter;
  ["All", "Fail", "Pass"].forEach((k) => {
    const btn = document.getElementById(`filterBtn${k}`);
    if (btn) btn.classList.remove("active-view");
  });

  const activeBtnId = filter === "FAIL" ? "filterBtnFail" : filter === "PASS" ? "filterBtnPass" : "filterBtnAll";
  const activeBtn = document.getElementById(activeBtnId);
  if (activeBtn) activeBtn.classList.add("active-view");

  renderFilteredEvalCards();
}

function renderFilteredEvalCards() {
  const container = document.getElementById("evalsList");
  if (!container || !_activeReportData) return;

  const results = _activeReportData.results || [];
  const failCount = results.filter((r) => r.status === "FAIL").length;
  const passCount = results.filter((r) => r.status === "PASS").length;

  const countAll = document.getElementById("countAll");
  const countFail = document.getElementById("countFail");
  const countPass = document.getElementById("countPass");
  if (countAll) countAll.innerText = results.length;
  if (countFail) countFail.innerText = failCount;
  if (countPass) countPass.innerText = passCount;

  const filtered = results.filter((r) => {
    if (_currentFilter === "FAIL") return r.status === "FAIL";
    if (_currentFilter === "PASS") return r.status === "PASS";
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `<div class="empty-state" style="padding: 24px; text-align: center;">
      ${_currentFilter === "FAIL" ? "🎉 No failures! All 10 test cases passed successfully for this model." : "No test cases found."}
    </div>`;
    return;
  }

  container.innerHTML = filtered
    .map((r) => {
      const isPass = r.status === "PASS";
      const devPct = r.deviation_pct !== undefined ? r.deviation_pct.toFixed(1) : "--";
      const ttft = r.ttft_ms ? `${Math.round(r.ttft_ms)}ms` : "--";

      let factStatusHtml = "";
      if (isPass) {
        factStatusHtml = `<span class="eval-facts-pass">✅ Grounded facts recalled (${devPct}% stylistic wording deviation)</span>`;
      } else {
        const missing = (r.missing_facts || []).map((f) => `Missing: "${escapeHtml(f)}"`).join(", ");
        const hall = (r.hallucinations || []).map((h) => `Hallucinated: "${escapeHtml(h)}"`).join(", ");
        factStatusHtml = `<span class="eval-facts-fail">⚠️ ${escapeHtml([missing, hall].filter(Boolean).join("; "))}</span>`;
      }

      return `
        <div class="eval-card ${isPass ? "pass" : "fail"}">
          <div class="eval-header">
            <div>
              <div class="eval-meta">
                <span class="eval-id">${escapeHtml(r.id)}</span>
                <span class="eval-category">${escapeHtml(r.category || "General")}</span>
              </div>
              <div class="eval-query">“${escapeHtml(r.input)}”</div>
            </div>
            <div class="eval-badges">
              <span class="eval-badge-dev">Δ ${devPct}% dev</span>
              <span class="${isPass ? "eval-badge-pass" : "eval-badge-fail"}">${escapeHtml(r.status)}</span>
            </div>
          </div>

          <div class="eval-grid">
            <div class="eval-box eval-box-expected">
              <div class="eval-box-label">🎯 Expected Ground Truth (Dataset)</div>
              <div>${escapeHtml(r.expected_output)}</div>
            </div>
            <div class="eval-box eval-box-actual">
              <div class="eval-box-label">🤖 Actual Agent Response</div>
              <div>${escapeHtml(r.actual_output)}</div>
            </div>
          </div>

          <div class="eval-footer">
            <div>${factStatusHtml}</div>
            <div style="font-family: ui-monospace, monospace;">TTFT: <strong>${ttft}</strong> | Latency: <strong>${Math.round(r.total_latency_ms || 0)}ms</strong></div>
          </div>
        </div>`;
    })
    .join("");
}

/**
 * Opens Markdown modal for inspecting the full text audit report
 */
async function viewMarkdownReport(runId) {
  const targetId = runId || _activeRunId || _latestRunId;
  const modal = document.getElementById("mdModal");
  const modalBody = document.getElementById("mdModalBody");
  const modalTitle = document.getElementById("mdModalTitle");

  if (!modal || !modalBody) return;

  modalBody.innerText = "Loading report markdown...";
  modal.classList.add("open");

  try {
    const res = await fetch(`/evals/markdown/${encodeURIComponent(targetId)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    modalBody.innerText = text;
    if (modalTitle) {
      modalTitle.innerText = `📄 Markdown Audit Report (${targetId})`;
    }
  } catch (err) {
    modalBody.innerText = `Error loading markdown report: ${err.message}`;
  }
}

function openCurrentMarkdownReport() {
  viewMarkdownReport(_activeRunId || _latestRunId);
}

function closeMarkdownModal() {
  const modal = document.getElementById("mdModal");
  if (modal) modal.classList.remove("open");
}

function copyMarkdownContent() {
  const modalBody = document.getElementById("mdModalBody");
  const btn = document.getElementById("copyMdBtn");
  if (!modalBody) return;

  navigator.clipboard.writeText(modalBody.innerText).then(() => {
    if (btn) {
      const orig = btn.innerText;
      btn.innerText = "✅ Copied!";
      setTimeout(() => (btn.innerText = orig), 2000);
    }
  });
}

// Close modal on Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeMarkdownModal();
});
