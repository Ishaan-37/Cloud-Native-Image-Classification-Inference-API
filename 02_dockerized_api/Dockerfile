# ─────────────────────────────────────────────────────────────────────────────
#  Dockerfile — Medical Image Inference API
#  Summer Internship Project – Week 2 (Containerisation)
#  Student: Ishaan Maurya | IIT Jammu 2026
#
#  Multi-stage build:
#    Stage 1 (builder) – install heavy dependencies into a clean layer
#    Stage 2 (runtime) – copy only what's needed → smaller final image
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Prevents Python from writing .pyc files and enables unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install system-level build tools needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libglib2.0-0 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (Docker layer cache: only re-run pip install
# if requirements.txt actually changes)
COPY requirements.txt .

# Install all Python packages into a dedicated prefix so we can copy them cleanly
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir \
       --extra-index-url https://download.pytorch.org/whl/cpu \
       -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Tell Python where the packages installed by Stage 1 live
    PYTHONPATH="/app:/install/lib/python3.11/site-packages"

# Runtime system libraries (no build tools needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security (good practice in any cloud deployment)
RUN useradd --create-home appuser
WORKDIR /app
USER appuser

# Copy installed packages from builder
COPY --from=builder /install /install

# Copy application source code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser imagenet_labels.json .
# Expose the port the app listens on
EXPOSE 8000

# Healthcheck so Docker (and EC2/ECS) knows if the container is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start the server
CMD ["python", "-m", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2"]
