from fastapi import APIRouter, Depends, HTTPException
from elasticsearch import Elasticsearch

from ..controllers.movies import *
from ..models.movies import MovieSearchRequest

movie_router = APIRouter()


@movie_router.get("/search")
async def Rsearch_movie(request: MovieSearchRequest = Depends()):
    """Search movie plot in Elasticsearch.

    Args:
        request (MovieSearchRequest): Search request.

    Returns:
        dict: Search results.
    """
    response: dict = Csearch_movie(request)

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response


@movie_router.get("/{id}")
async def Rget_movie(id: str):
    """Get movie by ID.

    Args:
        id (str): Movie ID.

    Returns:
        dict: Movie details.
    """

    response: dict = Csearch_movie_id(id, "movies")

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response
