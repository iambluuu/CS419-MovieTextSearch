import logging
import pandas as pd

from elasticsearch import Elasticsearch
from ..utils.config import config

# Initialize Elasticsearch client
logging.info("Initializing Elasticsearch client...")
es = Elasticsearch(
    [{"host": config["ES_HOST"], "port": int(config["ES_PORT"]), "scheme": "http"}],
    basic_auth=(config["ES_CLIENT"], config["ES_PASSWORD"]),
    verify_certs=False,
)

if not es.ping():
    raise ValueError("Connection failed")
