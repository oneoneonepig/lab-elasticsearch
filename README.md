# Lab for Elasticsearch

This script can allow you to easily provision a new Elasticsearch cluster.

- `cluster-3-nodes` can provision a three-node cluster
- `cluster-5-nodes` can provision a five-node cluster, one of the nodes is voting-only master-eligible node

## Requirements

- Memory usage
  - At least 6G for `cluster-3-nodes`
  - At least 10G `cluster-5-nodes`
- Docker
- Docker Compose
- Python
- Wordlist `sudo apt install wordlist`

## Setup

### Choose between 3 or 5 nodes

> Pick one, do not provision both!

To provision a 3 node cluster:
```bash
$ cd cluster-3-nodes
$ docker compose up -d
```

To provision a 5 node cluster:
```bash
$ cd cluster-3-nodes
$ docker compose up -d
```

## Prepare Python environment

```bash
sudo apt install python3.10-venv
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

### Create indices

```bash
$ cd scripts

$ ./op_index.py create
All indices created successfully

$ ./op_index.py list
myindex-1s0r
myindex-1s1r
myindex-1s3r
myindex-2s0r
myindex-2s1r
myindex-4s0r
myindex-4s1r
```

> `4s1r` represents an index sliced into 4 shards with 1 replica each

### Monitor the cluster

```bash
# monitor all indices
$ watch -n 1 ./monitor.py
[output too long, not displayed here]

# monitor a specific index
$ watch -n 1 ./monitor.py -i myindex-4s1r
>> Checking nodes...
Elasticsearch instance at http://localhost:9201 is running
Elasticsearch instance at http://localhost:9202 is running
Elasticsearch instance at http://localhost:9203 is running

>> Refreshing index myindex-4s1r...
Refreshed index myindex-4s1r

>> Checking index myindex-4s1r...
health status index        uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   myindex-4s1r cuTeZG0HQ6SjDUBQXgNf5Q   4   1        614            0    179.1kb         89.5kb

>> Checking shards for index myindex-4s1r...
index        shard prirep state   docs  store ip         node
myindex-4s1r 0     p      STARTED  156 21.4kb 172.27.0.3 es01
myindex-4s1r 0     r      STARTED  156 21.4kb 172.27.0.2 es02
myindex-4s1r 1     r      STARTED  161 26.3kb 172.27.0.6 es03
myindex-4s1r 1     p      STARTED  161 26.3kb 172.27.0.2 es02
myindex-4s1r 2     p      STARTED  153 21.4kb 172.27.0.6 es03
myindex-4s1r 2     r      STARTED  153 21.4kb 172.27.0.3 es01
myindex-4s1r 3     p      STARTED  144 20.3kb 172.27.0.3 es01
myindex-4s1r 3     r      STARTED  144 20.3kb 172.27.0.2 es02
```

### Index some documents
> Press Ctrl-C to stop the index script
```bash
$ cd scripts

$ ./index.py myindex-4s1r
Indexing into myindex-4s1r ...
^C
Indexed 613 documents within 4.39 seconds
Average indexing rate: 139.48 docs/sec
```

### Query some documents
```bash
./query.py -i myindex-4s1r -n 10
```

## Failover tests

Elasticsearch can make copies and move shards around to prevent from degraded performance and potential data loss.

When performing tests, you can open a new windows and keep the `./monitor.py` script running and observe the cluster status.

### Stop a single node in a three-node cluster

```bash
docker stop `docker compose ps es02 -q`
```

After stopping a single node, the remaining nodes can reach the quorum.

- Master node remains or a new node will be elected as master node
- Indices with replication will be available
- Indices without replication will not be available if any of the shard is on the stopped node

## Clean up

```bash
# to delete the containers
docker compose down

# to delete the containers and the volumes
docker compose down -v
```

## Components

- Elasticsearch nodes x 3 or 5 (9201-9203 or 9201-9205)
- Kibana (5601)
- HAProxy (9200)
- [monitor] elasticsearch_exporter (9114)
- [monitor] cAdvisor (8080)

> The monitoring related containers are disabled by default. To run the monitoring containers, use `docker compose --profile monitor up -d`

### HAProxy

Connects to all nodes round-robinly, except the voting-only node. Health check configured.

- [Dockerfile](https://github.com/docker-library/haproxy/blob/4fe74fe536642ccfe90c0753767a7f344f820047/2.8/Dockerfile)
- [Sample Configuration](https://learn.microsoft.com/en-us/previous-versions/troubleshoot/winautomation/product-documentation/processrobot-help-files/haproxy-sample-configuration)

## Scripts

Under `scripts/` directory, there are multiple bash scripts to interact with Elasticsearch

- `why_is_my_cluster_not_green.py` tells you why your cluster is not green
- `variables.py` defines shared variables such as node list and index list
- `index.py` inserts documents into the cluster
- `monitor.py` monitors the status of the cluster
- `op_index.py` creates, deletes or lists indices
- `query.py` queries documents

> Under the `scripts/` directory, there is a folder `archive/`, which contains the Bash version of the scripts. The Bash scripts are not maintained.

## Something worth mentioning

### Docker Compose Extensions

To simplify the docker-compose.yml content, we use [Extensions](https://docs.docker.com/compose/compose-file/11-extension/) and [Fragments](https://docs.docker.com/compose/compose-file/10-fragments/). For example:

```yaml
x-default-es: &default-es
  image: docker.elastic.co/elasticsearch/elasticsearch:${STACK_VERSION}
  mem_limit: ${ES_MEM_LIMIT}

services:
  es01:
    <<: *default-es
```

`&default-es` and `<<: *default-es` are YAML anchors and aliases, not a feature introduced by Docker Compose. To learn more, see how Atlassian explains [YAML anchors](https://support.atlassian.com/bitbucket-cloud/docs/yaml-anchors/) and the [YAML specifications](https://yaml.org/spec/1.2.2/#3222-anchors-and-aliases).

### Docker Compose Profiles

To temporarily disable some services specified in `docker compose`, we use [Profiles](https://docs.docker.com/compose/profiles/). For example:
```yaml
services:
  es01:
    image: ...
  elasticsearch_exporter:
    profiles:
      - monitor
    image: ...
```
This will assign the `elasticsearch_exporter` service to profile `monitor`. If you start the service through command `docker compose up -d`, the services attached to specific profile will not be brought up.

To start the services attached to profile, remove the profile section in `docker-compose.yml` or use `docker compose --profile monitor up -d`