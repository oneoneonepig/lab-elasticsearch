def init():
    global es_url
    es_url = "http://localhost:9200"

    global es_node_names
    es_node_names = ["es01", "es02", "es03", "es04", "es-voting"]

    global es_instances
    es_instances = [
        "http://localhost:9201",
        "http://localhost:9202",
        "http://localhost:9203",
        "http://localhost:9204",
        "http://localhost:9205",
    ]

    global indices
    indices = [
        "myindex-1s0r",
        "myindex-1s1r",
        "myindex-1s3r",
        "myindex-2s0r",
        "myindex-2s1r",
        "myindex-4s0r",
        "myindex-4s1r",
    ]
