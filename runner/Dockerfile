# # ===============================
# # 🧠 Ultra-Lean CPU-Only Orchestrator Image
# # ===============================

# # -------------------------------
# # Stage 1: Builder
# # -------------------------------
# FROM python:3.11-slim AS builder

# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# WORKDIR /app

# # Install build dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     cmake \
#     && rm -rf /var/lib/apt/lists/*

# # Create virtual environment
# RUN python -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"


# # Install other requirements
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# # -------------------------------
# # Stage 2: Runtime
# # -------------------------------
# FROM python:3.11-slim AS runtime

# ENV PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PATH="/opt/venv/bin:$PATH"

# WORKDIR /app

# # Install minimal runtime deps (if any needed, e.g. curl for healthcheck)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Copy virtual environment from builder
# COPY --from=builder /opt/venv /opt/venv

# # Copy application code
# COPY app.py .

# # Create non-root user and fix permissions
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# EXPOSE 8000

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


# ===============================
# 🧠 Ultra-Lean CPU-Only GGUF Runner
# ===============================

# -------------------------------
# Stage 1: Builder
# -------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install deps needed to compile llama-cpp-python (CPU-only)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Create virtual env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install llama-cpp-python CPU-only
RUN pip install llama-cpp-python==0.2.70 --verbose

# Add your Python deps (no heavy ML libs)
COPY requirements.txt .
RUN pip install -r requirements.txt

# -------------------------------
# Stage 2: Runtime
# -------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Minimal runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy optimized environment
COPY --from=builder /opt/venv /opt/venv

# Copy your app
COPY app.py .

# Non-root user for safety
RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
