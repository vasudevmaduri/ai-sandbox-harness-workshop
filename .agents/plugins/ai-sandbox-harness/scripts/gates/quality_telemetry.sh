#!/usr/bin/env sh
# PostToolUse Gate: Stack-aware static lint, checkpoint snapshot, and JSONL telemetry logger.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="$(command -v python3 || command -v python)"
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_gate.py" quality_telemetry
