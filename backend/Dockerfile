FROM python:3.11-slim

# System dependencies for psycopg2 and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for cache
COPY requirements.txt .
# Unset VERSION to avoid pip InvalidVersion errors
RUN unset VERSION && pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy rest of the backend code
COPY . .

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy .env if present (for local dev, not for prod)
COPY .env* ./

# Create non-root user
RUN useradd -m appuser

# Create logs directory and set permissions
RUN mkdir -p logs && chown appuser:appuser logs && chmod 755 logs

# Change ownership of .env files to appuser
RUN chown appuser:appuser .env* 2>/dev/null || true

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 