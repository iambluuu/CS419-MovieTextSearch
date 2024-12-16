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
    release_year: Optional[int] = Field(None, description="Filter by release year.")
    sort_by: Optional[str] = Field(
        "popularity", description="Field to sort the results by."
    )
    order: Optional[str] = Field(
        "desc", description="Order of sorting: 'asc' or 'desc'."
    )
    page: Optional[int] = Field(1, description="Page number for pagination.")
    size: Optional[int] = Field(10, description="Number of results per page.")

class ProductionCompany(BaseModel):
    """Model for production company information."""

    name: str = Field(..., description="Name of the production company.")
    id: str = Field(..., description="ID of the production company.")

class ProductionCountry(BaseModel):
    """Model for production country information."""

    iso_3166_1: str = Field(..., description="ISO 3166-1 code of the production country.")
    name: str = Field(..., description="Name of the production country.")

class Language(BaseModel):
    """Model for spoken language information."""

    iso_639_1: str = Field(..., description="ISO 639-1 code of the spoken language.")
    name: str = Field(..., description="Name of the spoken language.")

class CrewMember(BaseModel):
    """Model for crew member information."""

    name: str = Field(..., description="Name of the crew member.")
    gender : int = Field(..., ge=0, le=2, description = "Gender of the crew member. 0 for Unknown. 1 for Female. 2 for Male")
    department: str = Field(..., description="Department of the crew member.")
    job: str = Field(..., description="Job of the crew member.")

class MovieInfo(BaseModel):
    """Model for movie information."""

    # index	budget	genres	homepage	id	keywords	original_language	original_title	overview	popularity	production_companies	production_countries	release_date	revenue	runtime	spoken_languages	status	tagline	title	vote_average	vote_count	cast	crew	director
    index: str = Field(..., description="Index name.")
    budget: int = Field(..., ge=0, description="Budget of the movie in USD.")
    genres: str = Field(..., description="Genres of the movie separated by space.")
    homepage: str = Field(..., description="Homepage URL of the movie.", examples="http://movies.disney.com/john-carter")
    id: int = Field(..., ge=0, description="ID of the movie.")
    keywords: str = Field(..., description="Keywords of the movie separated by space.")
    original_language: str = Field(..., description="Original language of the movie in ISO 639-1 format.", examples="en")
    original_title: str = Field(..., description="Original title of the movie.", examples="John Carter")
    overview: str = Field(..., description="Overview of the movie.")
    popularity: float = Field(..., ge=0, description="Popularity score of the movie.")
    production_companies: List[ProductionCompany] = Field(..., description="Production companies with name and id.", examples=[{"name": "Walt Disney Pictures", "id": "2"}])
    production_countries: List[ProductionCountry] = Field(..., description="Production countries with ISO 3166-1 code and name.", examples=[{"iso_3166_1": "US", "name": "United States of America"}])
    release_date: str = Field(..., description="Release date of the movie in M/d/yyyy format.", examples="3/7/2012")
    revenue: int = Field(..., ge=0, description="Revenue of the movie in USD.")
    runtime: int = Field(..., ge=0, description="Runtime of the movie in minutes.")
    spoken_languages: List[Language] = Field(..., description="Spoken languages with ISO 639-1 code and name.", examples=[{"iso_639_1": "en", "name": "English"}])
    status: str = Field(..., description="Status of the movie.", examples="Released | Post Production")
    tagline: str = Field(..., description="Tagline of the movie.")
    title: str = Field(..., description="Title of the movie.", examples="John Carter")
    vote_average: float = Field(..., ge=0, le=10, description="Average vote of the movie.")
    vote_count: int = Field(..., ge=0, description="Number of votes for the movie.")
    cast: str = Field(..., description="List of cast members separeted by space.")


