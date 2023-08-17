#!/bin/bash

set -eo pipefail
shopt -s expand_aliases
source ./variables.sh

timeout=5
silence=false
if $silence; then
    alias curl='curl -s -o /dev/null'
fi


create_index_post_data()
{
  cat <<EOF
{
    "settings": {
        "index": {
            "number_of_shards": $1,
            "number_of_replicas": $2
        }
    }
}
EOF
}

print_usage()
{
    echo "usage: $0 [create|delete]"
}

create_indices()
{
for index in ${indices_all[@]}; do
    for instance in ${elasticsearch_instances[@]}; do
        curl -X PUT -m $timeout "${instance}/${index}" -H 'Content-Type: application/json' -d \
        "`create_index_post_data ${index:8:1} ${index:10:1}`"
        if [ "$?" == 0 ]; then
            break
        else
            if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
                echo "Index $index failed through all elasticsearch instances"
                sleep 1
            fi
        fi
    done
    echo
done
}

delete_indices()
{
for index in ${indices_all[@]}; do
    for instance in ${elasticsearch_instances[@]}; do
        curl -X DELETE -m $timeout "${instance}/${index}"
        if [ "$?" == 0 ]; then
            break
        else
            if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
                echo "Index $index failed through all elasticsearch instances"
                sleep 1
            fi
        fi
    done
    echo
done
}

main()
{
case "$1" in
    "create")
        create_indices
        ;;
    "delete")
        delete_indices
        ;;
    *)
        echo "Error: Invalid operator. Allowed values are 'create' or 'delete'."
        print_usage
        exit 1
        ;;
esac
}


main $@