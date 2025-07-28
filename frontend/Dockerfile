# syntax=docker/dockerfile:1
FROM python:3.11-slim

# System dependencies for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for cache
COPY requirements.txt .
# Unset VERSION to avoid pip InvalidVersion errors
RUN unset VERSION && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy rest of the frontend code
COPY . .

# Copy .env if present (for local dev, not for prod)
COPY .env* ./

# Create non-root user
RUN useradd -m appuser
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"] 