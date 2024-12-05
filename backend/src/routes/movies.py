from fastapi import APIRouter, Depends, HTTPException
from src.services.elastic import search_movie_plot
from src.models.movies import MovieSearchRequest

movie_router = APIRouter()


@movie_router.post("/search")
async def search_movie(request: MovieSearchRequest = Depends()):
    """Search movie plot in Elasticsearch.

    Args:
        request (MovieSearchRequest): Search request.

    Returns:
        dict: Search results.
    """
    response = search_movie_plot(request.query, "movies")

    if "error" in response:
        raise HTTPException(status_code=400, detail=response["error"])

    return response
