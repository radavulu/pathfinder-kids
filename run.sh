#!/bin/bash

# --- Configuration ---
# If HOMEKUMON_HOST is not set, it defaults to 0.0.0.0 for external access.
# If HOMEKUMON_PORT is not set, it defaults to 8700.
HOST=${HOMEKUMON_HOST:-0.0.0.0}
PORT=${HOMEKUMON_PORT:-8700}

echo "Starting Home Kumon on http://$HOST:$PORT"

# Check if we are in a Docker environment
if [ -f "/.dockerenv" ] || [ -f "/run/docker/docker.sock" ]; then
  echo "Detected Docker environment."
else
  echo "Detected local environment."
fi

# Use the virtual environment's uvicorn
VENV_UVICORN="/Users/ravi/Desktop/coding-llm/home-ku/.venv/bin/uvicorn"

if [ -f "$VENV_UVICORN" ]; then
  echo "Using venv uvicorn: $VENV_UVICORN"
  export HOMEKUMON_HOST=$HOST
  export HOMEKUMON_PORT=$PORT
  $VENV_UVICORN app.main:app --host $HOST --port $PORT --workers 1 --log-level info
else
  echo "Error: Virtual environment uvicorn not found at $VENV_UVICORN"
  echo "Please run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi
