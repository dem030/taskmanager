#!/bin/bash
# monitor.sh — silenzioso, logging centralizzato

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOGGER="$BASE_DIR/logger.sh"

CPU_THRESH=90
ZOMBIE_AGE=60

now_epoch() { date +%s; }

# ---------------- CPU > 90% ----------------
ps -eo pid,pcpu,user,comm --no-headers | while read -r pid pcpu user comm; do
  over=$(awk -v a="$pcpu" -v b="$CPU_THRESH" 'BEGIN{print (a>b)?1:0}')
  if [ "$over" -eq 1 ]; then
    [ -x "$LOGGER" ] && "$LOGGER" "ALERT" "CPU>90 pid=$pid user=$user cpu=$pcpu cmd=$comm"
  fi
done

# ---------------- ZOMBIE > 60s ----------------
# usa etimes (secondi) per semplicità/affidabilità
ps -eo pid,stat,etimes,ppid,user,comm --no-headers | while read -r pid stat etimes ppid user comm; do
  case "$stat" in
    Z*)
      if [ "$etimes" -ge "$ZOMBIE_AGE" ]; then
        [ -x "$LOGGER" ] && "$LOGGER" "ALERT" "ZOMBIE>60 pid=$pid ppid=$ppid user=$user age_s=$etimes cmd=$comm"
      fi
    ;;
  esac
done

exit 0
