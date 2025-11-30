#!/bin/sh
pip install uv
uv sync

set -e

DATA_DIR="./data/muenster"
DOWNLOAD_URL="https://download.geofabrik.de/europe/germany/nordrhein-westfalen/muenster-regbez-latest.osm.pbf"
TARGET_FILE="$DATA_DIR/muenster.osm.pbf"

# Create directory if missing
mkdir -p "$DATA_DIR"

# Check if directory is empty
if [ -z "$(ls -A "$DATA_DIR")" ]; then
    echo "No data found in $DATA_DIR — downloading..."
    wget -O "$TARGET_FILE" "$DOWNLOAD_URL"
else
    echo "Data already present in $DATA_DIR — skipping download."
fi
