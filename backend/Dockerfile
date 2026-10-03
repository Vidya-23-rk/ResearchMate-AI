# ============================================================
# ResearchMate AI — Backend Dockerfile
# ============================================================
# Multi-stage build keeps the final image lean.
# Stage 1: install dependencies
# Stage 2: copy only what the app needs to run
# ============================================================

FROM python:3.11-slim AS base

# System dependencies needed by PyMuPDF and FAISS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer is cached until
# requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create upload and index directories
RUN mkdir -p uploads faiss_index

# Expose the API port
EXPOSE 8000

# Start the FastAPI application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
