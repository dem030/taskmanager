#!/bin/bash
# zombie.sh
# Crea un processo zombie: il figlio esce subito, il padre dorme a lungo
(
python3 - <<'PY'
import os, time
pid = os.fork()
if pid == 0:
os._exit(0)
else:
time.sleep(1200)
PY
) &
echo "Zombie parent started (background). Controlla con 'ps aux | grep Z'"