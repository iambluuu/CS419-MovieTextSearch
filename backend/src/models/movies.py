from pydantic import BaseModel


class MovieSearchRequest(BaseModel):
    query: str
