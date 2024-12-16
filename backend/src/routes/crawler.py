from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import Elasticsearch

from ..controllers.crawler import *

crawler_router = APIRouter()

@crawler_router.put("/crawl")   
async def RP_crawl_movies():
    """Crawl movies from the web.

    Returns:
        dict: Crawl results.
    """
    response: dict = RC_crawl_movies()

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response

