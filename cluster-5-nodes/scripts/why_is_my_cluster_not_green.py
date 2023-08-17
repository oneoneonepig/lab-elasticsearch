#!/usr/bin/env python3

import json
import sys
import argparse
from elasticsearch import Elasticsearch
import logging
import myvars

# log_format = "[%(levelname)s]: %(message)s"
# logging.basicConfig(format=log_format, level=logging.WARNING)

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description="Tells you why your cluster is red",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "-u",
    "--url",
    type=str,
    required=False,
    default="http://localhost:9200",
    help="seconds",
)
parser.add_argument(
    "-t",
    "--timeout",
    type=int,
    required=False,
    default=5,
    help="set timeout in seconds",
)
# parser.add_argument(
#     "-d",
#     "--decider",
#     type=bool,
#     required=False,
#     default=False,
#     help="show decisions about why the shards are not allocated to nodes",
# )
args = parser.parse_args()

myvars.init()
es = Elasticsearch(args.url, request_timeout=args.timeout)


def main():
    # check if can connect to elasticsearch
    print()
    try:
        if es.ping():
            print(f">> Connected to elasticsearch {args.url}")
        else:
            raise Exception(f">> Cannot connect to elasticsearch {args.url}")
    except Exception as e:
        print("error:", e)
        sys.exit(1)

    # check if cluster is red
    es_cluster_health = es.cluster.health()
    es_color = es_cluster_health["status"]
    if es_color == "green":
        print(">> Cluster is green, exitting...")
        sys.exit(0)
    elif es_color == "red":
        print(">> Cluster is red, checking why...")
    elif es_color == "yellow":
        print(">> Cluster is yellow, checking why...")
    else:
        print(">> Unknown cluster status:", es_color)
        sys.exit(1)

    # check which indices are not green
    es_cat_indices = es.cat.indices(format="json").body
    unhealthy_indices = [
        index for index in es_cat_indices if index["health"] != "green"
    ]
    unhealthy_indices_name = [index["index"] for index in unhealthy_indices]
    unhealthy_yellow_indices_name = [
        index["index"] for index in unhealthy_indices if index["health"] == "yellow"
    ]
    unhealthy_red_indices_name = [
        index["index"] for index in unhealthy_indices if index["health"] == "red"
    ]

    print()
    print(
        ">> There are {} red indices and {} yellow indices:".format(
            len(unhealthy_yellow_indices_name), len(unhealthy_red_indices_name)
        )
    )
    print("Red indices: {}".format(",".join(unhealthy_red_indices_name)))
    print("Yellow indices: {}".format(",".join(unhealthy_yellow_indices_name)))

    # check which shards of the indices are not started

    es_cat_shards = es.cat.shards(
        format="json", index=",".join(unhealthy_indices_name)
    ).body
    unhealthy_shards = [shard for shard in es_cat_shards if shard["state"] != "STARTED"]
    # print(json.dumps(unhealthy_shards, indent=4))

    # check why the shards are not started
    reasons = []
    for shard in unhealthy_shards:
        reasons.append(
            es.cluster.allocation_explain(
                index=shard["index"],
                shard=shard["shard"],
                primary=(True if shard["prirep"] == "p" else False),
            ).body
        )

    print()
    print(">> There are {} unhealthy shards:".format(len(reasons)))
    for idx, reason in enumerate(reasons, start=0):
        print("{}: {}: {}".format(idx, reason["index"], reason["allocate_explanation"]))


if __name__ == "__main__":
    main()
