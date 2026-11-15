/**
 * Main Application Orchestrator:
 * Manages tab navigation and initial data loading.
 */

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

  const targetBtn = document.getElementById(`tab-${tab}-btn`);
  const targetContent = document.getElementById(`tab-${tab}`);

  if (targetBtn) targetBtn.classList.add("active");
  if (targetContent) targetContent.classList.add("active");

  if (tab === "bookings") loadBookings();
  if (tab === "telemetry") loadTelemetry();
  if (tab === "benchmarks") {
    loadEvals();
  }
}

// Initial badge counts & preloads on page ready
document.addEventListener("DOMContentLoaded", () => {
  loadBookings();
  loadTelemetry();
});
