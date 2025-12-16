#!/bin/bash
# renice.sh — silenzioso

PID="$1"
NICE="$2"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGGER="$BASE_DIR/logger.sh"

[ -z "$PID" ] && exit 1
[ -z "$NICE" ] && exit 1

renice -n "$NICE" -p "$PID" >/dev/null 2>&1

[ -x "$LOGGER" ] && "$LOGGER" "ACTION" "RENICE pid=$PID nice=$NICE"

exit 0
