import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
)
from livekit.plugins import cartesia, deepgram, groq, silero

load_dotenv()
logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

from src.config import BOOKINGS_PATH, get_faq_content

FAQ_CONTENT = get_faq_content()


def _load_bookings() -> list:
    if not BOOKINGS_PATH.exists():
        return []
    try:
        return json.loads(BOOKINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_bookings(bookings: list) -> None:
    BOOKINGS_PATH.write_text(json.dumps(bookings, indent=2), encoding="utf-8")


class FrontDeskAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a concise, polite front-desk assistant for SmileCare Dental Clinic. "
                "Always use lookup_clinic_policy before answering questions about pricing, "
                "hours, location, insurance, or cancellations. "
                "When a caller asks for open times or availability, use check_availability. "
                "When a caller wants to book, use book_appointment with their name, day, and time. Don't create a booking without name, day, and time or answer with a guess."
                "Never guess policies or booking statuses. "
                "Keep all responses under two short sentences and avoid markdown or emojis."
            )
        )

    @function_tool
    async def lookup_clinic_policy(self, topic: str) -> str:
        """Look up clinic policies, pricing, hours, location, insurance, or cancellation rules."""
        logger.info(f"FAQ TOOL EXECUTED: Searching policy for '{topic}'")
        if not FAQ_CONTENT:
            return "Policy document is currently unavailable."

        # Split markdown by sections and match keywords
        sections = [s.strip() for s in FAQ_CONTENT.split("## ") if s.strip()]
        keywords = [w.lower() for w in topic.split() if len(w) > 2]

        matched = [
            sec for sec in sections if any(word in sec.lower() for word in keywords)
        ]

        # Return matched sections, or full FAQ if the query is broad
        return "\n\n".join(matched) if matched else FAQ_CONTENT

    @function_tool
    async def check_availability(self, preferred_day: str) -> str:
        """Check available appointment slots or existing bookings for a given day."""
        logger.info(f"AVAILABILITY TOOL: Checking slots for '{preferred_day}'")
        bookings = _load_bookings()
        day_normalized = preferred_day.strip().lower()

        booked_slots = [
            b.get("time_slot")
            for b in bookings
            if b.get("preferred_day", "").strip().lower() == day_normalized
        ]

        if booked_slots:
            return (
                f"On {preferred_day}, the following slots are already booked: {', '.join(booked_slots)}. "
                f"Other clinic hours between 9:00 AM and 7:00 PM are available."
            )
        return f"All standard slots on {preferred_day} between 9:00 AM and 7:00 PM are currently available."

    @function_tool
    async def book_appointment(
        self, patient_name: str, preferred_day: str, time_slot: str
    ) -> str:
        """Book a dental consultation appointment for a caller."""
        logger.info(
            f"BOOKING TOOL EXECUTED: {patient_name} on {preferred_day} at {time_slot}"
        )
        bookings = _load_bookings()
        day_normalized = preferred_day.strip().lower()
        slot_normalized = time_slot.strip().lower()

        # Check for slot collision
        for b in bookings:
            if (
                b.get("preferred_day", "").strip().lower() == day_normalized
                and b.get("time_slot", "").strip().lower() == slot_normalized
            ):
                return (
                    f"I am sorry, {preferred_day} at {time_slot} is already booked for another patient. "
                    f"Please suggest an alternative time slot."
                )

        # Generate a unique booking reference
        booking_ref = f"BK-{len(bookings) + 101}"
        new_booking = {
            "booking_ref": booking_ref,
            "patient_name": patient_name.strip(),
            "preferred_day": preferred_day.strip(),
            "time_slot": time_slot.strip(),
            "booked_at": datetime.now().isoformat(),
        }
        bookings.append(new_booking)
        _save_bookings(bookings)

        return (
            f"Confirmed appointment for {patient_name} on {preferred_day} at {time_slot}. "
            f"Your booking reference is {booking_ref}."
        )



async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Fixed Production Stack: Deepgram (STT) -> Groq (LLM) -> Cartesia (TTS)
    groq_model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    cartesia_voice = os.getenv("CARTESIA_VOICE", "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4")

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3", language="en"),
        llm=groq.LLM(model=groq_model),
        tts=cartesia.TTS(model="sonic-3.6", voice=cartesia_voice),
    )

    from src.telemetry import TelemetryCollector

    telemetry = TelemetryCollector(
        session_id=ctx.room.name,
        llm_model=f"groq/{groq_model}",
        tts_model="cartesia/sonic-3.6",
        stt_model="deepgram/nova-3",
    )

    @session.on("metrics_collected")
    def _on_metrics_collected(ev):
        metrics.log_metrics(ev.metrics)
        telemetry.record_metric(ev.metrics)

    # When caller leaves or room closes, compute and persist final session telemetry
    async def _on_shutdown(reason: str = ""):
        summary = telemetry.finalize()
        logger.info(
            f"SESSION COMPLETED: {summary['session_id']} | "
            f"Turns: {summary['turns_count']} | "
            f"Avg TTFT: {summary['latency_ms']['ttft']['avg']}ms | "
            f"Avg TTFA: {summary['latency_ms']['ttfa']['avg']}ms | "
            f"Cost/min: ${summary['economics']['cost_per_minute_usd']} (₹{summary['economics']['cost_per_minute_inr']})"
        )

    ctx.add_shutdown_callback(_on_shutdown)

    # 4. Start the session in the LiveKit room and greet the caller
    await session.start(room=ctx.room, agent=FrontDeskAgent())
    await session.generate_reply(
        instructions="Greet the caller warmly and ask how you can help them today."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
