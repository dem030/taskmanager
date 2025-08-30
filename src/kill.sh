#!/bin/bash
# usage: kill_process.sh PID [KILL]
PID=$1
MODE=${2:-TERM}
if [ -z "$PID" ]; then
echo "Usage: $0 PID [KILL]" >&2
exit 1
fi
if [ "$MODE" = "KILL" ]; then
kill -9 "$PID" 2>&1
else
kill -15 "$PID" 2>&1
fi