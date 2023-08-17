#!/bin/bash

set -euo pipefail
shopt -s expand_aliases
source ./variables.sh

timeout=5
silence=true
if $silence; then
    alias curl='curl -s -o /dev/null'
fi


print_usage()
{
    echo "usage: $0 [index]"
}

post_data_shuf()
{
  cat <<EOF
{
    "message": "Hello, $(shuf -n 50 /usr/share/dict/words | tr '\n' ' ')!"
}
EOF
}

post_data()
{
  cat <<EOF
{
    "message": "Hello, world!"
}
EOF
}

count=0
print_count()
{
    duration=$SECONDS
    echo Indexed $count documents within $duration seconds
    echo Average indexing rate: `echo "scale=2; $count/$duration" | bc` docs/sec
}

if [ $# -ge 1 ]; then
    index=$1
else
    print_usage
    exit 1
fi

echo "Indexing into ${index} ..."
trap print_count SIGINT
while true; do
    for instance in ${elasticsearch_instances[@]}; do
        curl -X POST -m $timeout "${instance}/${index}/_doc?pretty" -H 'Content-Type: application/json' -d \
        "$(post_data_shuf)"
        if [ "$?" == 0 ]; then
            break
        else
            if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
                echo "Index $index failed through all elasticsearch instances"
                sleep 1
            fi
        fi
    done
    count=$((count+1))
done
