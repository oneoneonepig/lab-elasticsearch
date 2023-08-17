#!/usr/bin/env python3

import random
import time
from elasticsearch import Elasticsearch

import myvars

TIMEOUT = 5
SILENCE = True
POST_RANDOM = True
WORD_FILE = "/usr/share/dict/words"
WORDS = open(WORD_FILE).read().splitlines()

myvars.init()
es = Elasticsearch(myvars.es_url, request_timeout=TIMEOUT)


def usage():
    print("usage:", sys.argv[0], "[index]")
    sys.exit(1)


def post_data():
    if POST_RANDOM:
        return {"message": random.choice(WORDS)}
    else:
        return {"message": "Hello, world!"}


def signal_handler(sig, frame):
    print("You pressed Ctrl+C!")
    sys.exit(0)


def print_count(start_time, count):
    duration = time.time() - start_time
    print(f"Indexed {count} documents within {duration:.2f} seconds")
    print(f"Average indexing rate: {count/duration:.2f} docs/sec")


def main():
    index = ""
    if len(sys.argv) >= 2:
        index = sys.argv[1]
    else:
        usage()
        sys.exit(1)

    start_time = time.time()
    count = 0

    print(f"Indexing into {index} ...")
    # signal.signal(signal.SIGINT, lambda sig, frame: print_count(start_time, count))

    while True:
        try:
            resp = es.index(index=index, document=post_data())
            if resp["result"] != "created":
                print(resp)
                break
            count += 1
        except KeyboardInterrupt:
            print()
            print_count(start_time, count)
            sys.exit(0)


if __name__ == "__main__":
    import signal
    import sys

    main()
