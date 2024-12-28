from typing import Dict
import logging

from ..services.elastic import es
from ..models.movies import MovieSearchRequest

log = logging.getLogger(name="MovieApp")


def RC_feedback(movie_id: str, score: int, index_name: str = "movies") -> Dict:
    """
    This function is used to provide relevant search feedback on the recommended movie.

    Args:
    movie_id (str): The id of the movie that the user is providing feedback on.
    score (int, from 0-5): The score that the user is providing for the movie.

    Returns:
    Dict: A dictionary containing the status of the feedback submission.
    """

    if score < 0 or score > 5:
        return {
            "status": "error",
            "error": "Invalid score. Please provide a score between 0 and 5.",
        }

    score_adjusted: int = score - 3

    try:
        # Update script which checks if the feedback field exists and adds the score to it.
        # If the field does not exist, it creates the field and assigns the score to it.
        update_script = {
            "script": {
                "source": """
                    if (ctx._source.feedback == null) {
                        ctx._source.feedback = params.adjustment
                    } else {
                        ctx._source.feedback += params.adjustment
                    }
                """,
                "params": {"adjustment": score_adjusted},
            },
            "query": {"term": {"id": movie_id}},
        }

        # Apply the update script to the movie document.
        es.update_by_query(index=index_name, body=update_script)

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def RC_reset_feedback(movie_id: str, index_name: str = "movies") -> Dict:
    """
    This function is used to reset the feedback score for a specific movie.

    Args:
    movie_id (str): The id of the movie to reset the feedback score for.
    index_name (str): The name of the index to reset the feedback score for.

    Returns:
    Dict: A dictionary containing the status of the feedback reset operation.
    """

    try:
        total_slices = 100

        for slice_id in range(total_slices):
            update_script = {
                "script": {
                    "source": "ctx._source.feedback = 0",
                },
                "query": {
                    "bool": {
                        "must_not": {"term": {"feedback": 0}},
                    }
                },
                "slice": {
                    "id": slice_id,
                    "max": total_slices,
                },
            }

            es.update_by_query(
                index=index_name,
                body=update_script,
                conflicts="proceed",
                wait_for_completion=False,
            )

            log.info(f"Resetting feedback for slice {slice_id}.")

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def RC_reset_all_feedback(index_name: str = "movies") -> Dict:
    """
    This function is used to reset all feedback scores for all movies.

    Args:
    index_name (str): The name of the index to reset the feedback scores for.

    Returns:
    Dict: A dictionary containing the status of the feedback reset operation.
    """

    try:
        # Update script which resets the feedback field to 0.
        update_script = {
            "script": {
                "source": "ctx._source.feedback = 0",
            },
            "query": {"match_all": {}},
        }

        # Apply the update script to all movie documents.
        es.update_by_query(index=index_name, body=update_script)

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
