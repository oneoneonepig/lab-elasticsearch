#!/bin/bash

set -eu
shopt -s expand_aliases
source ./variables.sh

timeout=5
silence=false
if $silence; then
    alias curl='curl -s -o /dev/null'
fi


# Function to check the status of an Elasticsearch instance
check_elasticsearch_status() {
    instance_url=$1
    response=$(curl -s -o /dev/null -m $timeout "$instance_url" -w "%{http_code}" )
    if [ "$response" == "200" ]; then
        echo "Elasticsearch instance at $instance_url is running."
    else
        echo "Elasticsearch instance at $instance_url is down!"
    fi
}

echo "##### Check if nodes are running #####"
echo
for instance in "${elasticsearch_instances[@]}"; do
    check_elasticsearch_status "$instance"
done
echo

echo "##### Check cluster and node status #####"
echo
for instance in "${elasticsearch_instances[@]}"; do
    curl -s -m $timeout "$instance/_cat/health?v"
    if [ "$?" == 0 ]; then
        break
    else
        # echo "No response from health API through $instance, trying the next one..."
        if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
            echo "No response from health API through all elasticsearch instances"
        fi
    fi
done
echo

for instance in "${elasticsearch_instances[@]}"; do
    curl -s -m $timeout "$instance/_cat/nodes?v&s=name"
    if [ "$?" == 0 ]; then
        break
    else
        # echo "No response from node API through $instance, trying the next one..."
        if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
            echo "No response from node API through all elasticsearch instances"
        fi
    fi
done
echo

echo "##### Refresh index before query #####"
echo
for instance in "${elasticsearch_instances[@]}"; do
#while false; do
    curl -s -m $timeout "$instance/_refresh"
    if [ "$?" == 0 ]; then
        break
    else
        # echo "No response from shard API through $instance, trying the next one..."
        if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
            echo "Failed to refresh through all elasticsearch instances"
        fi
    fi
done
echo
echo


echo "##### Shard status #####"
echo
for instance in "${elasticsearch_instances[@]}"; do
    curl -s -m $timeout "$instance/_cat/shards/myindex-*?v&s=index,p,node"
    #curl -s -m $timeout "$instance/_cat/shards/myindex-1s3r?v&s=node"
    if [ "$?" == 0 ]; then
        break
    else
        # echo "No response from shard API through $instance, trying the next one..."
        if [ "$instance" == "${elasticsearch_instances[-1]}" ]; then
            echo "No response from shard API through all elasticsearch instances"
        fi
    fi
done
echo
