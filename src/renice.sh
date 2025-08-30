#!/bin/bash
# usage: renice_process.sh PID NICE
PID=$1
NICE=$2
if [ -z "$PID" ] || [ -z "$NICE" ]; then
echo "Usage: $0 PID NICE" >&2
exit 1
fi
renice -n "$NICE" -p "$PID" 2>&1