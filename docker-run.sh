#!/usr/bin/env bash
# Build and run PathfinderKids in Docker (one command).
set -e
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop, or use ./run.sh instead." >&2
  exit 1
fi

mkdir -p "${HOMEKUMON_DATA_DIR:-./data}"

echo "Building PathfinderKids image…"
docker compose build

echo "Starting container…"
docker compose up -d

PORT="${HOMEKUMON_PORT:-8700}"
echo ""
echo "PathfinderKids is running at http://127.0.0.1:${PORT}"
echo "Data folder: ${HOMEKUMON_DATA_DIR:-./data}  (mounted into the container as /data)"
echo "LM Studio must be running on the host at localhost:1234"
echo ""
echo "View logs:  docker compose logs -f"
echo "Stop:       docker compose down"
