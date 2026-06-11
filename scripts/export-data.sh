#!/usr/bin/env bash
# Export kids' progress for moving to another machine or backup.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUT="${1:-homekumon-backup-$(date +%Y%m%d).tar.gz}"

if [ -n "$HOMEKUMON_DATA_DIR" ]; then
  DATA="$HOMEKUMON_DATA_DIR"
elif [ -f "./data/homekumon.db" ]; then
  DATA="./data"
else
  DATA="$(python3 -c "import sys; sys.path.insert(0,'.'); from app.config import DATA_DIR; print(DATA_DIR)" 2>/dev/null || echo "./data")"
fi

if [ ! -d "$DATA" ]; then
  echo "Data folder not found: $DATA" >&2
  exit 1
fi

tar czf "$OUT" -C "$DATA" .
echo "Exported to: $OUT"
echo "On the new machine: copy the HomeKumon folder, then run:"
echo "  ./scripts/import-data.sh $OUT"
