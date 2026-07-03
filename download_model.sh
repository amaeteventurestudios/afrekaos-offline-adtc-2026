#!/usr/bin/env bash
#
# download_model.sh
# AfrekaOS Offline - ADTC 2026
#
# SAFE PLACEHOLDER SCRIPT
# -----------------------------------------------------------------------------
# This script does NOT download a real model yet.
#
# The exact model URL is NOT locked yet. Once the target GGUF model and
# quantization are chosen (see specs/001-afrekaos-offline/), this script will
# be updated to fetch the locked artifact and verify its checksum.
#
# For now it only:
#   1. Creates the model/ directory if it is missing.
#   2. Prints a clear status note.
# -----------------------------------------------------------------------------

set -euo pipefail

# Resolve repo root relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="${SCRIPT_DIR}/model"
MODEL_PATH="${MODEL_DIR}/afrekaos.gguf"

# URL is intentionally empty until the model is locked.
MODEL_URL=""

echo "AfrekaOS Offline - model fetch (placeholder)"
echo "---------------------------------------------"

# Ensure the model directory exists.
if [ ! -d "${MODEL_DIR}" ]; then
  echo "Creating model directory: ${MODEL_DIR}"
  mkdir -p "${MODEL_DIR}"
else
  echo "model directory already exists: ${MODEL_DIR}"
fi

if [ -n "${MODEL_URL}" ]; then
  echo "ERROR: This branch is not wired to fetch yet. MODEL_URL is expected to be empty."
  exit 1
fi

# Check if a model is already present.
if [ -f "${MODEL_PATH}" ]; then
  echo "Found existing model at: ${MODEL_PATH}"
  echo "Nothing to do."
  exit 0
fi

cat <<'EOF'

STATUS: model URL is not locked yet.

  - Expected runtime path:  model/afrekaos.gguf
  - Format:                 GGUF
  - Engine:                 llama.cpp

No model was downloaded. Place a GGUF file at model/afrekaos.gguf manually,
or wait until the model URL is locked in a later task.

EOF

exit 0
