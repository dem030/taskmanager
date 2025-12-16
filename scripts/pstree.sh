#!/bin/bash
# pstree.sh — stampa su stdout (per la GUI)

if command -v pstree >/dev/null 2>&1; then
    pstree -p -a
else
    ps -eo pid,ppid,cmd --forest
fi

exit 0
