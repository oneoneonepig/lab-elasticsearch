#!/usr/bin/env python3

import re
import sys
from elasticsearch import Elasticsearch

import myvars

TIMEOUT = 5

myvars.init()
es = Elasticsearch(myvars.es_url, request_timeout=TIMEOUT)


def usage():
    print("usage:", sys.argv[0], "[create|delete|list]")
    sys.exit(1)


def index_settings(shards, replicas):
    return {"number_of_shards": shards, "number_of_replicas": replicas}


def create_indices():
    for index in myvars.indices:
        s = re.match(r"\w+-(\d)s(\d)r", index)
        try:
            resp = es.indices.create(index=index, settings=index_settings(s[1], s[2]))
        except Exception as e:
            print("error creating index:", index)
            print(e)
            return
    print("All indices created successfully")


def delete_indices():
    for index in myvars.indices:
        try:
            resp = es.indices.delete(index=index)
        except Exception as e:
            print("error deleting index:", index)
            print(e)
            return
    print("All indices deleted successfully")


def list_indices():
    try:
        resp = es.indices.get(index="*")
        for k, v in resp.body.items():
            print(f"{k}")
    except Exception as e:
        print(e)
        return


def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    # check if es is running
    try:
        if not es.ping():
            raise Exception("elasticsearch not running")
    except:
        print("error connecting to elasticsearch")
        sys.exit(1)

    operation = sys.argv[1]
    match operation:
        case "create":
            create_indices()
        case "delete":
            delete_indices()
        case "list":
            list_indices()
        case default:
            usage()
            return


if __name__ == "__main__":
    main()
