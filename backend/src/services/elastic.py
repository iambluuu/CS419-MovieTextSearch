import pandas as pd

from elasticsearch import Elasticsearch
from ..utils.config import config

# Initialize Elasticsearch client
es = Elasticsearch(
    [{"host": config["ES_HOST"], "port": int(config["ES_PORT"]), "scheme": "http"}],
    basic_auth=(config["ES_CLIENT"], config["ES_PASSWORD"]),
    verify_certs=False,
)


def search_movie_plot(query: str, index_name: str) -> dict:
    """Search movie plot in Elasticsearch.

    Args:
        query (str): Search query.
        index_name (str): Name of the Elasticsearch index.

    Returns:
        dict: Search results.
    """

    body = {"query": {"match": {"overview": query}}}

    try:
        response = es.search(index=index_name, body=body)
        results = [hit["_source"] for hit in response["hits"]["hits"]]

        return {"results": results}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
