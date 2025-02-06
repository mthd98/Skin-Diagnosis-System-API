"""Main entry point for the Skin Diagnosis System API.

Manages API initialization, middleware, and route inclusion.

Headers:
    session_keys: Handles user sessions.
    api_keys: Manages API authentication keys.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import cases, users
import uvicorn
from api.middleware.auth import AuthMiddleware  # Import the middleware


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Creates and configures the FastAPI application.

    Returns:
        FastAPI: The initialized FastAPI app instance.
    """
    app = FastAPI(
        title="Skin Diagnosis System API",
        description="API for diagnosing skin conditions using AI.",
        version="1.0.0"
    )

    app.add_middleware(
        AuthMiddleware,
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(cases.router, prefix="/cases", tags=["Cases"])

    @app.get("/", tags=["Health"])
    def health_check() -> dict:
        """Health check endpoint to verify API is running.

        Returns:
            dict: A status message.
        """
        logger.info("Health check requested")
        return {"message": "Skin Diagnosis API is running"}

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
