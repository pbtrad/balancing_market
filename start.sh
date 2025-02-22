#!/bin/bash

echo "Waiting for PostgreSQL to start..."
sleep 5

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
