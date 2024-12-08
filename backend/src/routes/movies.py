"""This module contains the routes for movies.

Function names prefixed with:
    - `RX_` are for request handlers. Where X is the HTTP method (G, P, D, U).
    - `RC_` are for controller handlers.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from elasticsearch import Elasticsearch

from ..controllers.movies import *
from ..models.movies import MovieSearchRequest

movie_router = APIRouter()


@movie_router.get("/search")
async def RG_search_movie(request: Annotated[MovieSearchRequest, Query()]):
    """Search movie plot in Elasticsearch.

    Args:
        request (MovieSearchRequest): Search request.

    Returns:
        dict: Search results.
    """
    response: dict = RC_search_movie(request)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response


@movie_router.post("/search")
async def RP_search_movie(request: MovieSearchRequest):
    """Search movie plot in Elasticsearch.

    Args:
        request (MovieSearchRequest): Search request.

    Returns:
        dict: Search results.
    """
    response: dict = RC_search_movie(request)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response


@movie_router.get("/{id}")
async def RG_get_movie(id: str):
    """Get movie by ID.

    Args:
        id (str): Movie ID.

    Returns:
        dict: Movie details.
    """

    response: dict = RC_search_movie_id(id, "movies")

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response
