#!/bin/bash
# stop.sh — SIGSTOP (silenzioso)

PID="$1"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGGER="$BASE_DIR/logger.sh"

[ -z "$PID" ] && exit 1

kill -STOP "$PID" >/dev/null 2>&1

[ -x "$LOGGER" ] && "$LOGGER" "ACTION" "SIGSTOP pid=$PID"

exit 0
