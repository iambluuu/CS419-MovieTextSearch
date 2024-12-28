"""Main FastAPI application file."""

import logging
import os

from src.services.load_movies import load_movies_to_es
from src.utils.preprocess import preprocess_data
from src.utils.config import config
from src.utils import logconfig
from src.utils.loadintodb import load_data_into_db
from src.server import Server

log = logging.getLogger(name="MovieApp")
logconfig.setup_logging()


mapping = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 10,
                    "token_chars": ["letter", "digit"],
                },
            },
            "analyzer": {
                "default": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"],
                },
                "edge_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": ["lowercase"],
                },
            },
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "title": {
                "type": "text",
                "analyzer": "edge_ngram_analyzer",
                "fields": {
                    "suggest": {
                        "type": "completion",
                        "analyzer": "standard",
                        "search_analyzer": "standard",
                    },
                    "keyword": {"type": "keyword"},
                },
            },
            "vote_average": {"type": "float"},
            "vote_count": {"type": "integer"},
            "status": {"type": "keyword"},
            "release_date": {"type": "date"},
            "revenue": {"type": "long"},
            "runtime": {"type": "integer"},
            "budget": {"type": "long"},
            "original_language": {"type": "keyword"},
            "poster_path": {"type": "text"},
            "genres": {"type": "keyword"},
            "production_companies": {"type": "keyword"},
            "production_countries": {"type": "keyword"},
            "spoken_languages": {"type": "keyword"},
            "cast": {"type": "keyword"},
            "director": {"type": "keyword"},
            "imdb_rating": {"type": "float"},
            "imdb_votes": {"type": "integer"},
            "plot_synopsis": {"type": "text", "analyzer": "english"},
            "feedback": {"type": "integer", "null_value": 0},
        }
    },
}


def __init__() -> None:
    """Initialize the server."""

    try:
        # Path for dataset and cleaned dataset
        dataset_path = config["DATA_PATH"]
        cleaned_dataset_path = config["CLEANED_DATA_PATH"]

        # Check if preprocessing is required
        if not os.path.exists(cleaned_dataset_path) or (
            os.path.exists(dataset_path)
            and os.path.getmtime(dataset_path) > os.path.getmtime(cleaned_dataset_path)
        ):
            log.info("Preprocessing the dataset...")
            preprocess_data(dataset_path, cleaned_dataset_path, -1)

        # Load the cleaned dataset to Elasticsearch
        log.info("Loading the dataset to Elasticsearch...")
        load_movies_to_es(cleaned_dataset_path, "movies", mapping=mapping)
        log.info("Dataset loaded successfully!")

        # Load the dataset into MongoDB
        # log.info("Loading the dataset into MongoDB if needed...")
        # cleaned_dataset_path = "./src/data/merged_movies_dataset.xlsx"
        # load_data_into_db(cleaned_dataset_path)
        # log.info("Dataset loaded successfully into MongoDB!")

    except Exception as e:
        log.error(f"An error occurred: {e}")
        raise e


if __name__ == "__main__":
    """Run the FastAPI application."""

    # Initialize the server
    __init__()

    # Run the server
    app = Server()
    app.run()
