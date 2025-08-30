#!/bin/bash
# Output: pid user cpu% mem% stat comm
ps -eo pid,user,pcpu,pmem,stat,comm --no-headers --sort=-pcpu