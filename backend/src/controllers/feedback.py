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
