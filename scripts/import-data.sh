#!/usr/bin/env bash
# Import a backup created by export-data.sh onto this machine.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ARCHIVE="${1:?Usage: ./scripts/import-data.sh backup.tar.gz}"

if [ ! -f "$ARCHIVE" ]; then
  echo "Archive not found: $ARCHIVE" >&2
  exit 1
fi

if [ -n "$HOMEKUMON_DATA_DIR" ]; then
  DATA="$HOMEKUMON_DATA_DIR"
else
  DATA="$(python3 -c "import sys; sys.path.insert(0,'.'); from app.config import DATA_DIR; print(DATA_DIR)" 2>/dev/null || echo "./data")"
fi

mkdir -p "$DATA"
echo "Importing into: $DATA"
tar xzf "$ARCHIVE" -C "$DATA"
echo "Done. Start the app with ./run.sh or ./docker-run.sh"
