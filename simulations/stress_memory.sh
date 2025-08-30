#!/bin/bash
# stress_mem.sh
# Alloca MB di memoria in uno o più processi per testing.
# Usage: ./stress_mem.sh <MB_per_process> [count]
MB=${1:-100}
COUNT=${2:-1}


for i in $(seq 1 $COUNT); do
python3 - <<PY &
import sys, time, os
m = int(sys.argv[1])
a = bytearray(m * 1024 * 1024)
print(f"Allocated {m} MB - pid={os.getpid()}")
time.sleep(9999999)
PY $MB
done


echo "Started ${COUNT} memory-allocators of ${MB} MB each"