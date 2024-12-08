import ast
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
                "title": {"type": "text"},
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
        df = pd.read_csv(csv_path)

        # Ensures Elasticsearch index is created
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name, body=mapping)
        # es.indices.create(index=index_name)

        # Bulk upload data
        actions: list = []

        for i, row in df.iterrows():
            source_dict = row.to_dict()

            # Convert variables into appropriate types
            source_dict["genres"] = source_dict["genres"].split(" ")
            source_dict["keywords"] = source_dict["keywords"].split(" ")
            source_dict["production_companies"] = ast.literal_eval(
                source_dict["production_companies"]
            )
            source_dict["production_countries"] = ast.literal_eval(
                source_dict["production_countries"]
            )
            source_dict["spoken_languages"] = ast.literal_eval(
                source_dict["spoken_languages"]
            )
            source_dict["cast"] = source_dict["cast"].split(" ")    
            source_dict["crew"] = ast.literal_eval(source_dict["crew"])

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
