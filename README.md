# FrontDeskAI: Real-Time Self-Hosted Voice Assistant & Benchmark Telemetry

An enterprise-grade, ultra-low latency (<700ms voice turn) AI receptionist for appointment bookings, policy recall, and real-time telemetry. Built with LiveKit WebRTC, Groq LPUs, Cartesia TTS, Deepgram STT, and FastAPI.

---

## ⚡ Architecture & Pipeline

```text
               +-------------------------------------------------+
               |       Client Browser (LiveKit WebRTC SDK)       |
               +-----------------------+-------------------------+
                                       | Bidirectional Audio Stream
                                       v
               +-------------------------------------------------+
               |          LiveKit SFU Server (Port 7880)          |
               +-----------------------+-------------------------+
                                       | WebRTC Room Transport
                                       v
               +-------------------------------------------------+
               |          FrontDeskAI Python Agent Worker        |
               |                                                 |
               |  1. Deepgram Nova-2    (Streaming STT)          |
               |  2. Groq GPT-OSS 20B   (Fast Reasoning LLM)     |
               |  3. Cartesia Sonic     (Low-Latency Audio TTS)  |
               +-----------------------+-------------------------+
                                       | Structured Bookings & Telemetry
                                       v
               +-------------------------------------------------+
               |      FastAPI Server & Modular HUD Dashboard     |
               |             (http://localhost:8000)             |
               +-------------------------------------------------+
```

---

## 📁 Project Directory Structure

The project has been cleaned and modularized into dedicated directories for runtime code, frontend UI, domain knowledge, datasets, and reports:

```text
FrontDeskAI/
├── src/                          # Application source code
│   ├── __init__.py
│   ├── config.py                 # Central configuration and resolved paths
│   ├── agent.py                  # LiveKit WebRTC Voice Receptionist worker
│   ├── web_server.py             # FastAPI backend (WebRTC tokens, bookings, telemetry API)
│   ├── telemetry.py              # Real-time session metrics collector
│   └── eval_runner.py            # Unified accuracy, hallucination & latency benchmark suite
├── static/                       # 🌐 Modular Frontend Web Dashboard
│   ├── index.html                # Semantic HTML skeleton (<200 lines)
│   ├── css/
│   │   └── style.css             # Unified CSS design system, cards, badges & animations
│   └── js/
│       ├── utils.js              # HTML escaping & string helpers
│       ├── voice.js              # LiveKit WebRTC client, audio, & latency badge HUD
│       ├── bookings.js           # Confirmed appointment cards & refresh handler
│       ├── telemetry.js          # Production latency & cost telemetry cards
│       ├── benchmarks.js         # Provider decision matrix & latency waterfall
│       ├── evals.js              # Accuracy, fact recall & hallucination evals
│       └── app.js                # Tab switcher & application bootstrap
├── knowledge/                    # Agent domain grounding
│   └── clinic_faq.md             # Dental clinic hours, pricing, insurance, cancellation policies
├── data/                         # Persistent datasets & logs
│   ├── bookings.json             # Confirmed appointment bookings
│   ├── telemetry.json            # Call session telemetry logs
│   ├── benchmarks.json           # Cached empirical benchmark results
│   ├── eval_dataset.json         # Ground-truth Q&A test cases (10 scenarios)
│   └── eval_report.json          # Results of accuracy and hallucination evaluations
├── reports/                      # Generated evaluation and benchmark audits
│   ├── BENCHMARKS.md             # Provider comparison (Groq vs Claude, Cartesia vs Deepgram)
│   └── EVAL_REPORT.md            # LLM accuracy, pass rates, and output deviation report
├── docker-compose.yml            # Local LiveKit Server & Redis infrastructure
├── pyproject.toml                # uv Python dependencies & project config
├── run_dev.py                    # One-command runner for both web server & agent
├── .env.example                  # Environment configuration template
└── .env                          # Local API keys (git-ignored)
```

---

## 🔑 Environment Variables

FrontDeskAI uses a clean `.env` configuration. Copy `.env.example` to get started:

```bash
cp .env.example .env
```

| Variable | Required | Description | Default / Example |
| :--- | :--- | :--- | :--- |
| `LIVEKIT_URL` | **Yes** | LiveKit WebSocket endpoint | `ws://localhost:7880` |
| `LIVEKIT_API_KEY` | **Yes** | LiveKit API Key | `devkey` |
| `LIVEKIT_API_SECRET` | **Yes** | LiveKit API Secret | `secret` |
| `DEEPGRAM_API_KEY` | **Yes** | Deepgram API key for Nova-2 STT | `token_...` |
| `GROQ_API_KEY` | **Yes** | Groq API key for LPU fast inference | `gsk_...` |
| `CARTESIA_API_KEY` | **Yes** | Cartesia API key for Sonic TTS | `sk_car_...` |
| `GROQ_MODEL` | No | Groq model override | `openai/gpt-oss-20b` |
| `CARTESIA_VOICE` | No | Cartesia voice ID override | `db6b0ed5-d5d3-463d-...` |

---

## 🚀 How to Run the Services

### 1. Start Infrastructure
Launch the local LiveKit WebRTC server:
```bash
docker compose up -d
```

---

### Option A: Single-Command Runner (Easiest)
Launch **both** the FastAPI Web Server and the Voice Agent concurrently in one terminal:
```bash
uv run python run_dev.py
```
*Press `Ctrl+C` in that terminal to gracefully shut down both services.*

---

### Option B: Two-Terminal Workflow (Dev & Live Reload)

#### Terminal 1: Web Server & Frontend Dashboard
Runs the FastAPI backend and serves the WebRTC interface at [http://localhost:8000](http://localhost:8000):
```bash
uv run uvicorn src.web_server:app --port 8000 --reload
```

#### Terminal 2: LiveKit AI Voice Agent
Connects the Python agent worker to the LiveKit server in dev mode:
```bash
uv run python -m src.agent dev
```

---

## 🧪 Unified Evaluation & Benchmarking Suite

Run comprehensive accuracy, safety guardrail, and latency waterfall benchmarks across the 10 domain scenarios:

```bash
# Default free-tier model (openai/gpt-oss-20b):
uv run python -m src.eval_runner

# Evaluate specific model:
uv run python -m src.eval_runner --model llama-3.3-70b-versatile
```

- **Live UI**: Select any model in the dropdown and test live in the **Benchmarks & Evals Tab** at `http://localhost:8000/#benchmarks`.
- **Generated Reports**: Creates [data/eval_report.json](data/eval_report.json) and [reports/EVAL_REPORT.md](reports/EVAL_REPORT.md).
