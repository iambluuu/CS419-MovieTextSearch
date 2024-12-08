from ..services.elastic import es


def RC_get_status(index_name: str = "movies") -> dict:
    """Get Elasticsearch status.

    Args:
        index_name (str): Name of the Elasticsearch index.

    Returns:
        dict: Elasticsearch status.
    """

    try:
        # Check if the index exists
        if not es.indices.exists(index=index_name):
            return {"error": f"Index '{index_name}' does not exist."}

        # Get the index health and statistics
        health = es.cluster.health(index=index_name)
        stats = es.indices.stats(index=index_name)

        return {
            "index": index_name,
            "health": health["status"],
            "document_count": stats["_all"]["primaries"]["docs"]["count"],
            "storage_size": stats["_all"]["primaries"]["store"]["size_in_bytes"],
        }

    except Exception as e:
        return {"error": str(e)}
