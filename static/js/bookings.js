/**
 * Bookings Manager:
 * Fetches and renders clinic appointment records from /bookings.
 */

async function loadBookings() {
  const container = document.getElementById("bookingsList");
  const badge = document.getElementById("bookingBadge");
  if (!container) return;

  try {
    const res = await fetch("/bookings");
    const data = await res.json();
    if (badge) badge.innerText = data.length || 0;

    if (!data || data.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          No appointments booked yet.<br />
          Start a call and say: <em>"Book an appointment for Sarah on Tuesday at 4:00 PM"</em>.
        </div>`;
      return;
    }

    container.innerHTML = data
      .slice()
      .reverse()
      .map((b) => {
        const dateStr = b.booked_at ? new Date(b.booked_at).toLocaleString() : "";
        return `
          <div class="booking-card">
            <div>
              <div class="booking-patient">${escapeHtml(b.patient_name || "Patient")}</div>
              <div class="booking-slot">📅 ${escapeHtml(b.preferred_day)} at ${escapeHtml(b.time_slot)}</div>
              ${dateStr ? `<div class="booking-time">Booked on ${dateStr}</div>` : ""}
            </div>
            <div class="booking-ref">${escapeHtml(b.booking_ref || "CONFIRMED")}</div>
          </div>`;
      })
      .join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">Failed to load bookings: ${err.message}</div>`;
  }
}
