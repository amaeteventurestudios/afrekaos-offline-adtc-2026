#!/usr/bin/env bash
#
# run_local_web.sh
# AfrekaOS Offline - Task 004A local browser UI runner.
#
# Starts the standard-library-only local web UI at http://127.0.0.1:8787.
# Sets AFREKAOS_QWEN_NO_THINK=1 by default for Qwen direct-answer mode.
# Fully offline. No cloud, no external dependencies.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

export AFREKAOS_QWEN_NO_THINK="${AFREKAOS_QWEN_NO_THINK:-1}"

echo "AfrekaOS Offline — local browser UI"
echo "------------------------------------"
echo "Qwen direct-answer: AFREKAOS_QWEN_NO_THINK=${AFREKAOS_QWEN_NO_THINK}"
echo "Starting server..."
echo "Visit: http://127.0.0.1:8787"
echo

exec python3 -m app.web_app
