from pydantic import BaseModel, Field
from typing import List, Optional, Annotated


class MovieSearchRequest(BaseModel):
    """Request model for movie search."""

    query: Optional[str] = Field(
        None, description="Search text for the movie (e.g., title, plot)."
    )
    genres: Optional[List[str]] = Field(None, description="Filter by genres.")
    cast: Optional[List[str]] = Field(None, description="Filter by cast members.")
    director: Optional[str] = Field(None, description="Filter by director.")
    from_year: Optional[int] = Field(None, description="Filter by release year range.")
    to_year: Optional[int] = Field(None, description="Filter by release year range.")
    sort_by: Optional[str] = Field(None, description="Field to sort the results by.")
    order: Optional[str] = Field(
        "desc", description="Order of sorting: 'asc' or 'desc'."
    )
    page: Optional[int] = Field(1, description="Page number for pagination.")
    size: Optional[int] = Field(10, description="Number of results per page.")