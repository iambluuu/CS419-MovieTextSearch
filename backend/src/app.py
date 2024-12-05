"""Main FastAPI application file."""

import logging
import os

from src.services.load_movies import load_movies_to_es
from src.utils.preprocess import preprocess_data
from src.utils.config import config
from src.utils import logconfig
from src.server import Server

log = logging.getLogger(name="MovieApp")
logconfig.setup_logging()


def __init__() -> None:
    """Initialize the server."""

    try:
        # Path for dataset and cleaned dataset
        dataset_path = config["DATA_PATH"]
        cleaned_dataset_path = "./src/data/cleaned.csv"

        # Check if preprocessing is required
        if not os.path.exists(cleaned_dataset_path) or (
            os.path.exists(dataset_path)
            and os.path.getmtime(dataset_path) > os.path.getmtime(cleaned_dataset_path)
        ):
            log.info("Preprocessing the dataset...")
            preprocess_data(dataset_path, cleaned_dataset_path, -1)

        # Load the cleaned dataset to Elasticsearch
        log.info("Loading the dataset to Elasticsearch...")
        load_movies_to_es(cleaned_dataset_path, "movies")
        log.info("Dataset loaded successfully!")
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
