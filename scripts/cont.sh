#!/bin/bash
# cont.sh — SIGCONT (silenzioso)

PID="$1"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGGER="$BASE_DIR/logger.sh"

[ -z "$PID" ] && exit 1

kill -CONT "$PID" >/dev/null 2>&1

[ -x "$LOGGER" ] && "$LOGGER" "ACTION" "SIGCONT pid=$PID"

exit 0
