#!/bin/bash
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn petfit.api.main:app --host 0.0.0.0 --port 8080