from elasticsearch import Elasticsearch
from utils.config import config

es = Elasticsearch(
    f"http://{config['ES_CLIENT']}:{config['ES_PORT']}",
    http_auth=(config["ES_CLIENT"], config["ES_PASSWORD"]),
)

print(es.info())
