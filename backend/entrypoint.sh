#!/bin/bash
set -e

cd /app

# Ensure logs directory exists and is owned by appuser
mkdir -p logs
chown appuser:appuser logs

echo "[Entrypoint] Running Alembic migrations..."
alembic upgrade head || { echo "Alembic migration failed"; exit 1; }

echo "[Entrypoint] Starting FastAPI app..."

exec "$@" 