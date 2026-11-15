import json
import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from livekit import api

from src.config import (
    BOOKINGS_PATH,
    TELEMETRY_LOG_PATH,
    BENCHMARKS_JSON_PATH,
    REPORT_JSON_PATH,
    REPORT_MD_PATH,
    EVAL_HISTORY_PATH,
    REPORTS_HISTORY_DIR,
    INDEX_HTML_PATH,
    STATIC_DIR,
)

app = FastAPI(title="FrontDeskAI Service")

# Static assets mount
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def get_ui():
    if INDEX_HTML_PATH.exists():
        return FileResponse(str(INDEX_HTML_PATH))
    return {"message": "FrontDeskAI API Running. index.html not found."}


@app.get("/token")
async def get_token():
    room_name = f"test-room-{uuid.uuid4().hex[:6]}"
    token = (
        api.AccessToken(
            os.getenv("LIVEKIT_API_KEY", "devkey"),
            os.getenv("LIVEKIT_API_SECRET", "secret"),
        )
        .with_identity("browser-user")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    return {"token": token, "url": os.getenv("LIVEKIT_URL", "ws://localhost:7880")}


@app.get("/bookings")
async def get_bookings():
    if BOOKINGS_PATH.exists():
        try:
            with open(BOOKINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


@app.get("/telemetry")
async def get_telemetry():
    if TELEMETRY_LOG_PATH.exists():
        try:
            with open(TELEMETRY_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


@app.get("/benchmarks")
async def get_benchmarks():
    if BENCHMARKS_JSON_PATH.exists():
        try:
            with open(BENCHMARKS_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}



@app.get("/evals")
async def get_evals():
    if REPORT_JSON_PATH.exists():
        try:
            with open(REPORT_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


@app.get("/evals/history")
async def get_eval_history():
    if EVAL_HISTORY_PATH.exists():
        try:
            with open(EVAL_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


@app.get("/evals/run/{run_id}")
async def get_eval_run(run_id: str):
    # Match by exact run_id or version string (e.g. v1.0)
    resolved_id = run_id
    if run_id.startswith("v") and EVAL_HISTORY_PATH.exists():
        try:
            with open(EVAL_HISTORY_PATH, "r", encoding="utf-8") as f:
                hist = json.load(f)
                for item in hist:
                    if item.get("version") == run_id:
                        resolved_id = item.get("run_id")
                        break
        except Exception:
            pass

    history_file = REPORTS_HISTORY_DIR / f"{resolved_id}.json"
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed reading history: {e}"}

    if REPORT_JSON_PATH.exists():
        try:
            with open(REPORT_JSON_PATH, "r", encoding="utf-8") as f:
                curr = json.load(f)
                if curr.get("run_id") == resolved_id or curr.get("version") == run_id:
                    return curr
        except Exception:
            pass

    return {"error": f"Historical run {run_id} not found."}


@app.get("/evals/markdown/{run_id}")
async def get_eval_markdown(run_id: str):
    resolved_id = run_id
    if run_id.startswith("v") and EVAL_HISTORY_PATH.exists():
        try:
            with open(EVAL_HISTORY_PATH, "r", encoding="utf-8") as f:
                hist = json.load(f)
                for item in hist:
                    if item.get("version") == run_id:
                        resolved_id = item.get("run_id")
                        break
        except Exception:
            pass

    md_file = REPORTS_HISTORY_DIR / f"EVAL_{resolved_id}.md"
    if md_file.exists():
        return FileResponse(str(md_file), media_type="text/markdown")

    if REPORT_MD_PATH.exists():
        return FileResponse(str(REPORT_MD_PATH), media_type="text/markdown")

    return {"error": f"Report markdown for {run_id} not found."}



