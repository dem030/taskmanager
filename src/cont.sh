#!/bin/bash
PID=$1
if [ -z "$PID" ]; then echo "Missing PID" >&2; exit 1; fi
kill -CONT "$PID" 2>&1