import json
import os
import pandas as pd

from elasticsearch import helpers
from ..services.elastic import es


def load_movies_to_es(csv_path: str, index_name: str) -> None:
    """Load movies data to Elasticsearch.

    Args:
        csv_path (str): Path to the CSV file.
        index_name (str): Name of the Elasticsearch index.

    Returns:
        None

    Raises:
        FileNotFoundError: If the CSV file is not found.
    """

    mapping = {
        "mappings": {
            "properties": {
                "budget": {"type": "float"},
                "genres": {"type": "text"},
                "homepage": {"type": "keyword"},
                "keywords": {"type": "text"},
                "original_language": {"type": "keyword"},
                "overview": {"type": "text"},
                "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                "runtime": {"type": "float"},
                "vote_average": {"type": "float"},
                "vote_count": {"type": "integer"},
                "title": {"type": "text"},
                "director": {"type": "text"},
            }
        }
    }

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)

        # Ensures Elasticsearch index is created
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name, body=mapping)

        # Bulk upload data
        actions: list = []

        for i, row in df.iterrows():
            action = {
                "_index": index_name,
                "_id": i,
                "_source": row.to_dict(),
            }
            actions.append(action)

        if len(actions) > 0:
            helpers.bulk(es, actions, index=index_name)

    except Exception as e:
        raise e


if __name__ == "__main__":
    load_movies_to_es("./src/data/cleaned.csv", "movies")
