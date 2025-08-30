#!/bin/bash
# sleep.sh
# Avvia un processo sleep in background (utile per test semplici)
DURATION=${1:-300}
sleep "$DURATION" &
echo "sleep started (pid $!) for ${DURATION} seconds"