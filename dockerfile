###############################################################################
# Stage 1 — “builder”: compile everything (wheels) so the runtime image is slim
###############################################################################
FROM python:3.11-slim AS builder

# ─ Environment tweaks: speeds up pip and stops any interactive Debian prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# ─ System packages needed only while building Python wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .

# Upgrade pip first, then build wheels into /wheels
RUN pip install --upgrade pip && \
    pip wheel --wheel-dir /wheels -r requirements.txt

###############################################################################
# Stage 2 — “runtime”: super-light image with just what we need to run
###############################################################################
FROM python:3.11-slim

# ─ Install runtime libraries that OpenCV (used by YOLO) needs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# ─ Copy pre-built wheels from the builder stage and install them offline
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels --upgrade pip && \
    pip install --no-index --find-links=/wheels /wheels/*

# ─ Set working directory to /app
WORKDIR /app

# ─ Include src/ on Python’s import path
ENV PYTHONPATH=/app/src

# ─ Copy your project code into /app
COPY . .

# ─ Expose ports
# 3000 → Dagster UI (dagit)
# 8000 → FastAPI (Uvicorn)
EXPOSE 3000 8000

# ─ Default command:
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000"]
