#!/bin/bash

# ==============================================================================
# Humanitarian Data Pipeline & Dashboard Bridge
# ------------------------------------------------------------------------------
# Purpose: Orchestrates the execution of the humanitarian data pipeline,
#          validates output, and synchronizes assets for the dashboard.
# 
# Usage: ./run_dashboard_pipeline.sh
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

# Configuration
PIPELINE_DIR="humanitarian_pipeline"
PIPELINE_SCRIPT="$PIPELINE_DIR/pipeline.py"
OUTPUT_DIR="$PIPELINE_DIR/outputs"
DASHBOARD_ASSETS="web_map" # Folder where dashboard reads dynamic content

echo "[1/4] Starting Pipeline Execution..."
echo "      Running: python $PIPELINE_SCRIPT"

# Execute the pipeline with verbose logging
# Assuming pipeline.py supports internal logging or can be piped
if python3 "$PIPELINE_SCRIPT"; then
    echo "      [SUCCESS] Pipeline completed successfully."
else
    echo "      [ERROR] Pipeline failed during execution. Check logs in $PIPELINE_DIR/pipeline.log"
    exit 1
fi

echo "[2/4] Validating Outputs..."
if [ -d "$OUTPUT_DIR" ]; then
    echo "      [SUCCESS] Output directory found at $OUTPUT_DIR"
else
    echo "      [ERROR] Expected output directory $OUTPUT_DIR not created."
    exit 1
fi

echo "[3/4] Synchronizing Assets to Dashboard..."
# Clear old assets if necessary or just sync new ones
# Using rsync for efficiency if available, or cp
if [ -d "$DASHBOARD_ASSETS" ]; then
    echo "      Syncing outputs to $DASHBOARD_ASSETS..."
    cp -r "$OUTPUT_DIR/"* "$DASHBOARD_ASSETS/"
    echo "      [SUCCESS] Assets updated."
else
    echo "      [WARNING] Dashboard assets folder $DASHBOARD_ASSETS not found. Creating it."
    mkdir -p "$DASHBOARD_ASSETS"
    cp -r "$OUTPUT_DIR/"* "$DASHBOARD_ASSETS/"
fi

echo "[4/4] Process Complete."
echo "      Dashboard is now synchronized with the latest pipeline data."
echo "      Ready for viewing in index.html."
