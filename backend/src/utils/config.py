from dotenv import load_dotenv
import os

load_dotenv(".env")

# Interface
config = {
    # Movie dataset
    "DATA_PATH": "src/data/movies.csv",
    # API configuration
    "API_PORT": os.getenv("PORT") or 3001,
    # Elasticsearch configuration
    "ES_HOST": "localhost",
    "ES_PORT": os.getenv("ELASTICSEARCH_PORT") or "9200",
    "ES_CLIENT": os.getenv("ELASTICSEARCH_CLIENT"),
    "ES_PASSWORD": os.getenv("ELASTICSEARCH_PASSWORD"),
}
