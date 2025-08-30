#!/bin/bash
# monitor.sh
LOGFILE=${1:-monitor.log}
INTERVAL=${2:-5}
CPU_THRESH=${CPU_THRESH:-90}
ZOMBIE_AGE=${ZOMBIE_AGE:-60}


while true; do
# CPU > threshold
ps -eo pid,pcpu,comm --no-headers | awk -v thr="$CPU_THRESH" '$2 > thr { print strftime("%Y-%m-%d %H:%M:%S"), "CPU_HIGH", $1, $2, $3 }' >> "$LOGFILE"


# zombie processes
ps -eo pid,stat,etime,comm --no-headers | awk -v za="$ZOMBIE_AGE" '
$2 ~ /Z/ { split($3, t, "-");
# etime format [[dd-]hh:]mm:ss - approximate seconds
s=0; if(index($3,"-")>0){ split($3, a, "-"); days=a[1]; rest=a[2]; } else { days=0; rest=$3 }
n=split(rest,b,":"); if(n==3) s=b[1]*3600+b[2]*60+b[3]; else if(n==2) s=b[1]*60+b[2]; else s=0;
s_total = s + days*86400;
if(s_total > za) print strftime("%Y-%m-%d %H:%M:%S"), "ZOMBIE_STALE", $1, s_total, $4 }' >> "$LOGFILE"


sleep "$INTERVAL"
done