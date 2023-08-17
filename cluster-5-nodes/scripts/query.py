#!/usr/bin/env python3

import sys
import argparse
from elasticsearch import Elasticsearch, NotFoundError

import myvars

parser = argparse.ArgumentParser(
    prog=sys.argv[0],
    description="Search for documents in an index",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    # epilog="Text at the bottom of help",
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
parser.add_argument("-i", "--index", type=str, required=True, help="specify index name")
parser.add_argument(
    "-n", "--count", type=int, required=True, help="query for n documents"
)
args = parser.parse_args()

myvars.init()
es = Elasticsearch(args.url, request_timeout=args.timeout)


def main():
    try:
        if not es.ping():
            raise Exception("cannot connect to elasticsearch")
    except Exception as e:
        print("error:", e)
        sys.exit(1)

    index = args.index
    count = args.count

    try:
        resp = es.search(index=index, size=count, query={"match_all": {}}).body
        if resp['_shards']['failed'] > 0:
            raise Exception(f"failed shards, reason: {resp['_shards']['failures']}")
    except NotFoundError as e:
        print("Index not found:", index)
        sys.exit(1)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

    # print(resp)
    print("total hits:", resp["hits"]["total"]["value"])
    print(f"search results (maximum {args.count}):")
    print([hit.get('_source') for hit in resp["hits"]["hits"]])


if __name__ == "__main__":
    main()
