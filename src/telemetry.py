import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from livekit.agents.metrics import LLMMetrics, TTSMetrics

logger = logging.getLogger("telemetry")
from src.config import TELEMETRY_LOG_PATH, USD_TO_INR

# Industry average combined voice pipeline cost: ~$0.015 / minute (Deepgram + Groq + Cartesia)
ESTIMATED_COST_PER_MINUTE_USD = 0.015


class TelemetryCollector:
    """Lightweight session telemetry collector for latency and cost tracking."""

    def __init__(
        self,
        session_id: str,
        llm_model: str = "groq/openai/gpt-oss-20b",
        tts_model: str = "cartesia/sonic-3.6",
        stt_model: str = "deepgram/nova-3",
    ):
        self.session_id = session_id
        self.llm_model = llm_model
        self.tts_model = tts_model
        self.stt_model = stt_model
        self.start_time = datetime.now()

        self.ttft_samples: List[float] = []
        self.ttfa_samples: List[float] = []
        self.turns_count = 0

    def record_metric(self, metric: Any) -> None:
        """Capture TTFT (LLM) and TTFA (TTS) from LiveKit events."""
        if isinstance(metric, LLMMetrics):
            if metric.ttft and metric.ttft > 0:
                self.ttft_samples.append(round(metric.ttft * 1000, 1))
            self.turns_count += 1
        elif isinstance(metric, TTSMetrics):
            if metric.ttfb and metric.ttfb > 0:
                self.ttfa_samples.append(round(metric.ttfb * 1000, 1))

    def get_summary(self) -> Dict[str, Any]:
        """Compile session latency averages and estimated cost."""
        duration_sec = max((datetime.now() - self.start_time).total_seconds(), 1.0)

        avg_ttft = (
            round(sum(self.ttft_samples) / len(self.ttft_samples), 1)
            if self.ttft_samples
            else 0.0
        )
        avg_ttfa = (
            round(sum(self.ttfa_samples) / len(self.ttfa_samples), 1)
            if self.ttfa_samples
            else 0.0
        )

        # Voice-to-voice turn latency = VAD endpointing (~150ms) + STT (~200ms) + TTFT + TTFA
        avg_turn = (
            round(avg_ttft + avg_ttfa + 350.0, 1)
            if (avg_ttft and avg_ttfa)
            else 0.0
        )

        total_cost_usd = round(
            (duration_sec / 60.0) * ESTIMATED_COST_PER_MINUTE_USD, 4
        )
        total_cost_inr = round(total_cost_usd * USD_TO_INR, 2)
        cost_per_min_usd = round(ESTIMATED_COST_PER_MINUTE_USD, 4)
        cost_per_min_inr = round(cost_per_min_usd * USD_TO_INR, 2)

        return {
            "session_id": self.session_id,
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": round(duration_sec, 1),
            "turns_count": max(self.turns_count, len(self.ttft_samples)),
            "models": {
                "stt": self.stt_model,
                "llm": self.llm_model,
                "tts": self.tts_model,
            },
            "latency_ms": {
                "ttft": {"avg": avg_ttft},
                "ttfa": {"avg": avg_ttfa},
                "voice_to_voice_turn": {"avg": avg_turn},
            },
            "economics": {
                "total_cost_usd": total_cost_usd,
                "total_cost_inr": total_cost_inr,
                "cost_per_minute_usd": cost_per_min_usd,
                "cost_per_minute_inr": cost_per_min_inr,
            },
        }

    def finalize(self) -> Dict[str, Any]:
        """Save session telemetry to data/telemetry.json and return summary."""
        summary = self.get_summary()
        existing = []
        if TELEMETRY_LOG_PATH.exists():
            try:
                existing = json.loads(TELEMETRY_LOG_PATH.read_text(encoding="utf-8"))
            except Exception:
                existing = []

        existing.append(summary)
        TELEMETRY_LOG_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        logger.info(
            f"TELEMETRY LOGGED: Session {self.session_id} | "
            f"Turns: {summary['turns_count']} | "
            f"Avg TTFT: {summary['latency_ms']['ttft']['avg']}ms | "
            f"Avg TTFA: {summary['latency_ms']['ttfa']['avg']}ms | "
            f"Cost/min: ${summary['economics']['cost_per_minute_usd']} (₹{summary['economics']['cost_per_minute_inr']})"
        )
        return summary
