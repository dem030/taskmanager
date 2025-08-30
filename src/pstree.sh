#!/bin/bash
# Output a simple pstree-like view
# Requires pstree (procps) or fallback to a python small tree
if command -v pstree >/dev/null 2>&1; then
pstree -p -a | sed 's/^[[:space:]]*//'
exit 0
fi
# Fallback: build a simple tree using ps
ps -eo pid,ppid,comm --no-headers | awk '
BEGIN{ OFS=" "; }
{ children[$2]=children[$2]" "$1; name[$1]=$3 }
END{
function printnode(pid, indent){
printf("%s%s(%d)\n", indent, name[pid], pid)
split(children[pid], arr)
for(i in arr){ if(arr[i]!="") printnode(arr[i], indent" ") }
}
# find roots (ppid==0 or missing)
for(p in name){ roots[p]=1 }
for(p in name){ if(children[p]){
split(children[p], arr)
for(i in arr){ if(arr[i] != "") delete roots[arr[i]] }
}}
for(r in roots) printnode(r, "")
}'