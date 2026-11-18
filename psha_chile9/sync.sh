#!/usr/bin/env bash
# usage: ./sync.sh pull|push <host> [remote dir]
# copies the files git does not hold; only new and newer files, never deletes
set -e
cd "$(dirname "$0")"
mode=$1; host=$2; rdir=${3:-$PWD}
items="data runs refs trials figures/out"
[ "$mode" = pull ] || [ "$mode" = push ] || { echo "usage: ./sync.sh pull|push <host> [remote dir]"; exit 1; }
for d in $items; do
  if [ "$mode" = pull ]; then
    mkdir -p "$d"
    rsync -au --info=progress2 "$host:$rdir/$d/" "$d/"
  else
    ssh "$host" "mkdir -p '$rdir/$d'"
    rsync -au --info=progress2 "$d/" "$host:$rdir/$d/"
  fi
done
