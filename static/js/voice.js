/**
 * LiveKit WebRTC Voice Client:
 * Handles audio playback, real-time streaming transcripts, and voice turn latency measurement.
 */

let room;
const statusEl = document.getElementById("status");
const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const transcriptBox = document.getElementById("transcriptBox");
const lastLatencyEl = document.getElementById("lastLatency");
const avgLatencyEl = document.getElementById("avgLatency");

const segmentElements = new Map();
let userWasSpeaking = false;
let agentWasSpeaking = false;
let userStoppedAt = null;
let latencies = [];

function updateLatencyBadge(ms) {
  latencies.push(ms);
  const avg = Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length);

  if (lastLatencyEl) lastLatencyEl.innerText = `${ms} ms`;
  if (avgLatencyEl) avgLatencyEl.innerText = `${avg} ms`;

  if (lastLatencyEl) lastLatencyEl.className = "badge " + (ms < 700 ? "fast" : ms < 1200 ? "medium" : "slow");
  if (avgLatencyEl) avgLatencyEl.className = "badge " + (avg < 700 ? "fast" : avg < 1200 ? "medium" : "slow");
}

function upsertTranscriptSegment(segment, isLocal) {
  const emptyState = document.getElementById("emptyState");
  if (emptyState) emptyState.remove();

  let msgEl = segmentElements.get(segment.id);
  if (!msgEl) {
    msgEl = document.createElement("div");
    msgEl.className = `msg ${isLocal ? "user" : "agent"}`;
    msgEl.innerHTML = `<div class="sender">${isLocal ? "You" : "Agent"}</div><div class="text"></div>`;
    transcriptBox.appendChild(msgEl);
    segmentElements.set(segment.id, msgEl);
  }

  msgEl.querySelector(".text").innerText = segment.text;
  msgEl.classList.toggle("interim", !segment.final);
  transcriptBox.scrollTop = transcriptBox.scrollHeight;
}

if (connectBtn) {
  connectBtn.onclick = async () => {
    try {
      if (statusEl) statusEl.innerText = "Status: Connecting...";
      segmentElements.clear();
      latencies = [];
      if (lastLatencyEl) {
        lastLatencyEl.innerText = "-- ms";
        lastLatencyEl.className = "badge";
      }
      if (avgLatencyEl) {
        avgLatencyEl.innerText = "-- ms";
        avgLatencyEl.className = "badge";
      }
      if (transcriptBox) {
        transcriptBox.innerHTML = `<div class="empty-state" id="emptyState">Listening...</div>`;
      }

      const res = await fetch("/token");
      const { token, url } = await res.json();

      room = new LivekitClient.Room();

      // 1. Play incoming audio from the Python AI agent
      room.on(LivekitClient.RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === "audio") {
          const audioEl = track.attach();
          document.getElementById("audioContainer").appendChild(audioEl);
        }
      });

      // 2. Render live streaming transcripts for both User and Agent
      room.on(LivekitClient.RoomEvent.TranscriptionReceived, (segments, participant) => {
        const isLocal = participant && participant.isLocal;
        for (const segment of segments) {
          if (segment.text && segment.text.trim().length > 0) {
            upsertTranscriptSegment(segment, isLocal);
          }
        }
      });

      // 3. Measure Voice-to-Voice Turn Latency (User stops -> Agent starts)
      room.on(LivekitClient.RoomEvent.ActiveSpeakersChanged, (speakers) => {
        const userSpeakingNow = speakers.some((p) => p.isLocal);
        const agentSpeakingNow = speakers.some((p) => !p.isLocal);

        if (userWasSpeaking && !userSpeakingNow) {
          userStoppedAt = performance.now();
        }

        if (!agentWasSpeaking && agentSpeakingNow && userStoppedAt !== null) {
          const turnLatency = Math.round(performance.now() - userStoppedAt);
          updateLatencyBadge(turnLatency);
          userStoppedAt = null;
        }

        userWasSpeaking = userSpeakingNow;
        agentWasSpeaking = agentSpeakingNow;
      });

      await room.connect(url, token);
      await room.localParticipant.setMicrophoneEnabled(true);

      if (statusEl) statusEl.innerText = "Status: Connected — Speak now!";
      connectBtn.disabled = true;
      if (disconnectBtn) disconnectBtn.disabled = false;
    } catch (err) {
      console.error(err);
      if (statusEl) statusEl.innerText = "Error: " + err.message;
    }
  };
}

if (disconnectBtn) {
  disconnectBtn.onclick = async () => {
    if (room) await room.disconnect();
    if (statusEl) statusEl.innerText = "Status: Disconnected";
    if (connectBtn) connectBtn.disabled = false;
    disconnectBtn.disabled = true;

    setTimeout(() => {
      if (typeof loadBookings === "function") loadBookings();
      if (typeof loadTelemetry === "function") loadTelemetry();
    }, 1000);
  };
}
