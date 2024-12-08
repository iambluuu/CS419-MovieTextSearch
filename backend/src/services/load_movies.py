import ast
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
                "index": {"type": "integer"},
                "budget": {"type": "double"},
                "genres": {"type": "keyword"},
                "keywords": {"type": "text"},
                "original_language": {"type": "keyword"},
                "original_title": {"type": "text"},
                "overview": {"type": "text"},
                "popularity": {"type": "double"},
                "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                "revenue": {"type": "double"},
                "runtime": {"type": "double"},
                "status": {"type": "keyword"},
                "tagline": {"type": "text"},
                "title": {
                    "type": "text",
                    "fields": {
                        "suggest": {
                            "type": "completion",
                            "analyzer": "standard",
                            "search_analyzer": "standard",
                        }
                    },
                },
                "vote_average": {"type": "double"},
                "vote_count": {"type": "integer"},
                "cast": {"type": "keyword"},
                "director": {"type": "text"},
            }
        }
    }

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    try:
        # Ensures Elasticsearch index is created
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name, body=mapping)

        # Bulk upload data
        actions: list = []

        # Load the CSV file
        df = pd.read_csv(csv_path)

        # Convert columns to appropriate data types
        df["genres"] = df["genres"].apply(lambda x: x.split(" "))
        df["keywords"] = df["keywords"].apply(lambda x: x.split(" "))
        df["production_companies"] = df["production_companies"].apply(ast.literal_eval)
        df["production_countries"] = df["production_countries"].apply(ast.literal_eval)
        df["spoken_languages"] = df["spoken_languages"].apply(ast.literal_eval)
        df["cast"] = df["cast"].apply(lambda x: x.split(" "))
        df["crew"] = df["crew"].apply(ast.literal_eval)

        for i, row in df.iterrows():
            source_dict = row.to_dict()
            source_dict["suggest"] = {
                "input": source_dict["title"].split(),
                "weight": float(source_dict["popularity"]),
            }

            action = {
                "_index": index_name,
                "_id": i,
                "_source": source_dict,
            }
            actions.append(action)

        helpers.bulk(es, actions, index=index_name, raise_on_error=False)

        # Preview the mapping
        template = es.indices.get_mapping(index=index_name)
        print(template)

    except Exception as e:
        raise e


if __name__ == "__main__":
    load_movies_to_es("./src/data/cleaned.csv", "movies")
