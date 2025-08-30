#!/bin/bash
# stress_cpu.sh
# Genera N processi che consumano CPU (default 1)
N=${1:-1}
for i in $(seq 1 $N); do
( while true; do :; done ) &
done
echo "Started $N cpu-hog(s)"