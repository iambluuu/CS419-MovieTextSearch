from typing import Dict

from ..services.elastic import es
from ..models.movies import MovieSearchRequest


def Csearch_movie(search_query: MovieSearchRequest, index_name: str = "movies") -> dict:
    """Search movies with given filters/sort in Elasticsearch.

    The search query can include the following parameters:
    - query: Search text for the movie (e.g., title, plot).
    - genres: Filter by genres.
    - cast: Filter by cast members.
    - director: Filter by director.
    - release_year: Filter by release year.
    - sort_by: Field to sort the results by.
    - order: Order of sorting: 'asc' or 'desc'.
    - page: Page number for pagination.
    - size: Number of results per page.

    Args:
        search_query (MovieSearchRequest): Search query.
        index_name (str): Name of the Elasticsearch index.

    Returns:
        dict: Search results.
    """

    try:
        # Base query
        query: Dict = {
            "bool": {
                "must": [],
                "filter": [],
            }
        }

        # Add full-text search if query exists
        if search_query.query:
            query["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": search_query.query,
                        "fields": ["title^3", "overview", "cast", "director"],
                        "type": "best_fields",
                    }
                }
            )

        # Add filters
        if search_query.genres:
            query["bool"]["filter"].append(
                {"terms": {"genres.keyword": search_query.genres}}
            )
        if search_query.cast:
            query["bool"]["filter"].append(
                {"terms": {"cast.keyword": search_query.cast}}
            )
        if search_query.director:
            query["bool"]["filter"].append(
                {"term": {"director.keyword": search_query.director}}
            )
        if search_query.release_year:
            query["bool"]["filter"].append(
                {
                    "range": {
                        "release_date": {
                            "gte": f"{search_query.release_year}-01-01",
                            "lte": f"{search_query.release_year}-12-31",
                        }
                    }
                }
            )

        # Sorting
        sort_field = (
            search_query.sort_by
            if search_query.sort_by in ["rank", "popularity", "release_date"]
            else "popularity"
        )
        order = search_query.order if search_query.order in ["asc", "desc"] else "desc"

        # Search request body
        body = {
            "query": query,
            "sort": [{sort_field: {"order": order}}],
            "from": (search_query.page - 1) * search_query.size,
            "size": search_query.size,
        }

        # Execute the search
        response = es.search(index="movies", body=body)
        hits = response["hits"]["hits"]

        # Extract the results
        results = [hit["_source"] for hit in hits]

        return {
            "total": response["hits"]["total"]["value"],
            "results": results,
            "page": search_query.page or 1,
            "size": search_query.size or 10,
        }
    except Exception as e:
        return {"error": str(e)}


def Csearch_movie_id(id: str, index_name: str) -> dict:
    """Search movie with a specific ID in Elasticsearch.

    Args:
        id (str): Movie ID.
        index_name (str): Name of the Elasticsearch index.

    Returns:
        dict: Search results.
    """

    body = {"query": {"match": {"id": id}}}

    try:
        response = es.search(index=index_name, body=body)
        hits = response["hits"]["hits"]

        # Extract the results
        results = [hit["_source"] for hit in hits]

        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
