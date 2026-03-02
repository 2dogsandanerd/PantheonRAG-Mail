# syntax=docker/dockerfile:1
# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Force CPU-only PyTorch to save space (approx 2GB savings)
RUN --mount=type=cache,target=/root/.cache/pip pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Copy application code
COPY src ./src
COPY .env.example ./.env

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=33800

# Expose port
EXPOSE 33800

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:33800/api/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "33800"]
