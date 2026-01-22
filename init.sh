#!/bin/sh
set -e

pip install uv
uv sync

DATA_DIR="./data/muenster"
DOWNLOAD_URL="https://download.geofabrik.de/europe/germany/nordrhein-westfalen/muenster-regbez-latest.osm.pbf"
TARGET_FILE="$DATA_DIR/muenster.osm.pbf"

# Create directory if missing
mkdir -p "$DATA_DIR"

# Check if ANY .pbf file exists
if ! ls "$DATA_DIR"/*.pbf >/dev/null 2>&1; then
    echo "No .pbf file found in $DATA_DIR — downloading..."
    wget -O "$TARGET_FILE" "$DOWNLOAD_URL"
else
    echo ".pbf file already present in $DATA_DIR — skipping download."
fi