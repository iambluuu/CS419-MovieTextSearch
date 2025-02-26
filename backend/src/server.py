"""Main FastAPI application file."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from src.routes.movies import movie_router
from src.routes.es import es_router


class Server:
    def __init__(self):
        self.app = FastAPI(title="Movie Search API")

        # Add middlewares
        self.security_middleware()
        self.standard_middlewares()

        # Add routes
        self.add_routes()

    def security_middleware(self) -> None:
        """Add security middleware to the FastAPI application.

        This method adds the CORSMiddleware to the FastAPI application.
        Where the origins are the allowed origins for the application.
        """
        origins: list[str] = [
            "http://localhost",
            "http://localhost:8080",
            "http://localhost:5173",
            "http://localhost:3001",
            "*",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def standard_middlewares(self) -> None:
        """Add standard middlewares to the FastAPI application."""
        pass

    def add_routes(self) -> None:
        """Add the API routes to the FastAPI application."""

        # Add default "/" route
        @self.app.get("/")
        async def root():
            return {"message": "Hello World"}

        # Add the movie search route
        self.app.include_router(movie_router, prefix="/movies", tags=["movies"])
        self.app.include_router(es_router, prefix="/es", tags=["elasticsearch"])

        return

    def run(self):
        """Run the FastAPI application."""

        try:
            print("Starting the server")
            uvicorn.run(self.app, host="127.0.0.1", port=3001)

        except Exception as e:
            print(f"An error occurred: {e}")
