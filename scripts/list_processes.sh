#!/bin/bash
# Output: pid user cpu% mem% stat comm
ps -eo comm, pid,user,pcpu,pmem,stat --no-headers --sort=-pcpu