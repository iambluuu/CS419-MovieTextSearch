import pandas as pd

from elasticsearch import Elasticsearch
from ..utils.config import config

# Initialize Elasticsearch client
es = Elasticsearch(
    [{"host": config["ES_HOST"], "port": int(config["ES_PORT"]), "scheme": "http"}],
    basic_auth=(config["ES_CLIENT"], config["ES_PASSWORD"]),
    verify_certs=False,
)

print(es.info())


def load_movies_to_es(csv_path: str, index_name: str) -> None:
    """Load movies data to Elasticsearch.

    Args:
        csv_path (str): Path to the CSV file.
        index_name (str): Name of the Elasticsearch index.

    Returns:
        None
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
                "release_date": {"type": "date", "format": "dd/MM/yyyy"},
                "runtime": {"type": "float"},
                "vote_average": {"type": "float"},
                "vote_count": {"type": "integer"},
                "title": {"type": "text"},
                "director": {"type": "text"},
            }
        }
    }

    try:
        df = pd.read_csv(csv_path)
        # Ensures Elasticsearch index is created
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name)

        # Bulk upload data
        for i, row in df.iterrows():
            doc = row.to_dict()
            es.index(index=index_name, body=doc)

    except Exception as e:
        raise e


if __name__ == "__main__":
    load_movies_to_es("./src/data/cleaned.csv", "movies")
