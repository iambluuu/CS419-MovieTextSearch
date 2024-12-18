from dotenv import load_dotenv
import os

load_dotenv(".env")

# Interface
config = {
    # Movie dataset
    "DATA_PATH": "src/data/merged_movies_dataset.xlsx",
    "CLEANED_DATA_PATH": "src/data/cleaned.xlsx",
    # API configuration
    "API_PORT": os.getenv("PORT") or 3001,
    # Elasticsearch configuration
    "ES_HOST": os.getenv("ELASTICSEARCH_HOST") or "localhost",
    "ES_PORT": os.getenv("ELASTICSEARCH_PORT") or "9200",
    "ES_CLIENT": os.getenv("ELASTICSEARCH_CLIENT"),
    "ES_PASSWORD": os.getenv("ELASTICSEARCH_PASSWORD"),
    # MongoDB configuration
    "MONGODB_URI": os.getenv("MONGODB_URI"),
    "MONGODB_USERNAME": os.getenv("MONGODB_USERNAME"),
    "MONGODB_PASSWORD": os.getenv("MONGODB_PASSWORD"),
    "MONGODB_CLUSTERNAME": os.getenv("MONGODB_CLUSTERNAME"),
}
