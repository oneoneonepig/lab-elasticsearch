
#!/usr/bin/env python3

import sys
import argparse
from elasticsearch import Elasticsearch

import myvars

TIMEOUT = 1

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
parser.add_argument(
    "-i",
    "--index",
    type=str,
    required=False,
    help="show status for a specific index",
)
args = parser.parse_args()

myvars.init()
es = Elasticsearch(args.url, request_timeout=TIMEOUT)


def check_nodes():
    print()
    print(">> Checking nodes...")
    for node in myvars.es_instances:
        with Elasticsearch(node, request_timeout=TIMEOUT) as es_node:
            if es_node.ping():
                print("Elasticsearch instance at {} is running".format(node))
            else:
                print("Elasticsearch instance at {} is down".format(node))


def check_cluster():
    print()

    try:
        print(">> Listing cluster nodes...")
        resp = es.cat.nodes(v=True)
        print(resp)
    except Exception as e:
        print("Failed checking cluster nodes:", e)



def refresh_indices():
    print()

    try:
        if args.index:
            print(">> Refreshing index {}...".format(args.index))
            es.indices.refresh(index=args.index)
            print("Refreshed index {}".format(args.index))
        else:
            print(">> Refreshing all indices...")
            es.indices.refresh(index="_all")
            print("Refreshed all indices")
    except Exception as e:
        print("Refresh failed:", e)


def check_indices():
    print()

    try:
        if args.index:
            print(">> Checking index {}...".format(args.index))
            resp = es.cat.indices(index=args.index, v=True)
            print(resp)
        else:
            print(">> Checking all indices...")
            resp = es.cat.indices(v=True)
            print(resp)
    except Exception as e:
        print("Failed listing indices:", e)


def check_shards():

    try:
        if args.index:
            print(">> Checking shards for index {}...".format(args.index))
            resp = es.cat.shards(index=args.index, v=True)
            print(resp)
        else:
            print(">> Checking all shards...")
            resp = es.cat.shards(v=True)
            print(resp)
    except Exception as e:
        print("Failed listing shards:", e)


def main():
    try:
        if not es.ping():
            raise Exception("cannot connect to elasticsearch")
    except Exception as e:
        print("error:", e)
        sys.exit(1)

    check_nodes()
    check_cluster()
    refresh_indices()
    check_indices()
    check_shards()


if __name__ == "__main__":
    main()
