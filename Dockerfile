# 1. Base Image: lightweight Debian-based Python 3.12
FROM python:3.12-slim

# 2. Install uv binary directly from official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Environment & Workspace setup
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 4. Cache and install dependencies (frozen = respect lockfile, no-dev = exclude pytest/ruff)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 5. Copy application source and assets
COPY src/ ./src/
COPY static/ ./static/
COPY data/ ./data/
COPY knowledge/ ./knowledge/
COPY run_dev.py ./

# 6. Expose web server port
EXPOSE 8000

# 7. Start FastAPI web server (listening on all interfaces)
CMD ["uv", "run", "python", "-m", "uvicorn", "src.web_server:app", "--host", "0.0.0.0", "--port", "8000"]
