from typing import Dict
import logging

from ..services.elastic import es
from ..models.movies import MovieSearchRequest


log = logging.getLogger(name="MovieApp")


def build_query(search_query: MovieSearchRequest) -> Dict:
    """Build Elasticsearch query from search query.

    Args:
        search_query (MovieSearchRequest): Search query.

    Returns:
        Dict: Elasticsearch query.
    """

    # Base query
    query: Dict = {
        "bool": {
            "must": [],
            "filter": [],
            "should": [],
        }
    }

    # Add full-text search if query exists
    if search_query.query:
        # Title Field
        query["bool"]["should"].append(
            {
                "match": {
                    "title": {
                        "query": "{}".format(search_query.query),
                        "fuzziness": "AUTO",
                        "operator": "and",
                        "boost": 5,
                    }
                }
            },
        )

        query["bool"]["should"].append(
            {
                "match_phrase": {
                    "title": {
                        "query": "{}".format(search_query.query),
                        "boost": 10,
                        "slop": 2,
                    }
                }
            },
        )

        # Plot_synopsis Field
        query["bool"]["should"].append(
            {
                "match": {
                    "plot_synopsis": {
                        "query": "{}".format(search_query.query),
                        "operator": "and",
                        "fuzziness": "AUTO",
                        "boost": 1,
                    }
                },
            },
        )

        query["bool"]["should"].append(
            {
                "match_phrase": {
                    "plot_synopsis": {
                        "query": "{}".format(search_query.query),
                        "boost": 2,
                        "slop": 2,
                    }
                },
            }
        )
        query["bool"]["minimum_should_match"] = 1

    # Add filters
    if search_query.genres:
        query["bool"]["filter"].append({"terms": {"genres": search_query.genres}})

    if search_query.cast:
        query["bool"]["filter"].append({"terms": {"cast": search_query.cast}})

    if search_query.director:
        query["bool"]["filter"].append(
            {
                "wildcard": {
                    "director": f"*{search_query.director}*",
                }
            }
        )

    if search_query.from_year:
        query["bool"]["filter"].append(
            {
                "range": {
                    "release_date": {
                        "gte": f"{search_query.from_year}-01-01",
                        "format": "yyyy-MM-dd",
                    }
                }
            }
        )

    if search_query.to_year:
        query["bool"]["filter"].append(
            {
                "range": {
                    "release_date": {
                        "lte": f"{search_query.to_year}-12-31",
                        "format": "yyyy-MM-dd",
                    }
                }
            }
        )

    return query


def RC_search_movie(
    search_query: MovieSearchRequest, index_name: str = "movies"
) -> dict:
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

    log.info(f"Searching movies with query: {search_query.dict()}")

    if search_query.size is None:
        search_query.size = 10
    if search_query.page is None:
        search_query.page = 1

    print(search_query.dict())

    try:
        # Build the query
        base_query = build_query(search_query)

        # Sorting
        sort_field = (
            search_query.sort_by
            if search_query.sort_by in ["popularity", "release_date"]
            else None
        )
        order = search_query.order if search_query.order in ["asc", "desc"] else "desc"

        # Search request body
        query = {
            "function_score": {
                "query": base_query,
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "source": """
                                double feedback = doc['feedback'].value;
                                double result = Math.exp(feedback);
                                return result;
                                """
                            }
                        }
                    }
                ],
                "boost_mode": "sum",
                "max_boost": 100,
                "score_mode": "sum",
            }
        }

        body = {
            "query": query,
            "from": (search_query.page - 1) * search_query.size,
            "size": search_query.size,
        }

        if sort_field:
            body["sort"] = [{sort_field: {"order": order}}]

        # Execute the search
        response = es.search(index=index_name, body=body)
        hits = response["hits"]["hits"]

        # Extract the results
        results = [hit["_source"] for hit in hits]

        # Log the score
        for hit in hits:
            log.info(
                f"Movie: {hit['_source']['title']}, Score: {hit['_score']}, Feedback: {hit['_source'].get('feedback', 0)}"
            )

        return {
            "total": response["hits"]["total"]["value"],
            "results": results,
            "page": search_query.page or 1,
            "size": search_query.size or 10,
        }
    except Exception as e:
        return {"error": str(e)}


def RC_search_movie_id(id: str, index_name: str) -> dict:
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


def RC_get_all_genres(index_name: str) -> dict:
    """Get all genres from Elasticsearch.

    Args:
        index_name (str): Name of the Elasticsearch index.

    Returns:
        dict: Search results.
    """

    body = {
        "size": 0,
        "aggs": {
            "genres": {
                "terms": {
                    "field": "genres",
                    "size": 1000,
                }
            }
        },
    }

    try:
        response = es.search(index=index_name, body=body)
        genres = response["aggregations"]["genres"]["buckets"]

        return {"genres": [genre["key"] for genre in genres]}
    except Exception as e:
        return {"error": str(e)}


def RC_get_suggestions(index_name: str, query: str) -> dict:
    """Get suggestions from Elasticsearch.

    Args:
        index_name (str): Name of the Elasticsearch index.
        query (str): Search query.

    Returns:
        dict: Search results.
    """

    # Search for unique suggestions

    body = {
        "suggest": {
            "movie-suggest": {
                "prefix": query,
                "completion": {
                    "field": "title.suggest",
                    "size": 10,
                    "skip_duplicates": True,
                },
            }
        },
    }

    try:
        response = es.search(index=index_name, body=body)
        suggestions = response["suggest"]["movie-suggest"][0]["options"]

        return {
            "suggestions": [
                suggestion["_source"]["title"] for suggestion in suggestions
            ]
        }
    except Exception as e:
        return {"error": str(e)}
