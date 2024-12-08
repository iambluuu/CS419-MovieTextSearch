from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query

from ..controllers.es import *

es_router = APIRouter()


@es_router.get("/status", tags=["Index Management"])
async def RG_get_status(index_name: str = "movies"):
    """Get Elasticsearch status.

    Args:
        es (Elasticsearch): Elasticsearch client.

    Returns:
        dict: Elasticsearch status.
    """
    response: dict = RC_get_status(index_name)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response
