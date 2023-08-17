#!/bin/bash

set -euo pipefail
shopt -s expand_aliases
source ./variables.sh

timeout=5
silence=true
if $silence; then
    alias curl='curl -s -o /dev/null'
fi


index=$1
size=$2

if [ $# -ne 2 ]; then
    echo "Usage: $0 [index] [size]"
    exit 1
fi


post_data()
{
  cat <<EOF
{
  "size": "${size}"
}
EOF
}


for instance in "${elasticsearch_instances[@]}"; do
    #curl -X PUT -m $timeout "${instance}/${index}/_doc/1?pretty" -H 'Content-Type: application/json' -d \
    curl -s -X POST -m $timeout "${instance}/${index}/_search" -H 'Content-Type: application/json' -d \
    "$(post_data)" \
    #-o /dev/null -s
    if [ "$?" == 0 ]; then
        break
    else
        if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
            echo "Index $index failed through all elasticsearch instances"
            sleep 1
        fi
    fi
done
