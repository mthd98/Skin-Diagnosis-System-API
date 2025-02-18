from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.authentication import verify_token
import os
import logging

# Configure logger
logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """Global JWT authentication middleware for all API routes."""

    async def dispatch(self, request: Request, call_next):
        try:
            # Skip authentication if running in testing mode
            if os.getenv("TESTING") == "true":
                logger.info("Skipping authentication (TESTING mode enabled).")
                return await call_next(request)

            # Public routes that don't require authentication
            public_routes = ["/users/register-doctor", "/users/login", "/docs", "/openapi.json", "/redoc"]
            if request.url.path in public_routes:
                logger.info(f"Skipping authentication for public route: {request.url.path}")
                return await call_next(request)

            # Check Authorization header
            auth_header = request.headers.get("Authorization")
            logger.info(f"Checking Authorization header for {request.url.path}")

            if not auth_header or not auth_header.startswith("Bearer "):
                logger.warning(f"Missing or invalid Authorization header on {request.url.path}")
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

            # Validate the JWT token
            token = auth_header.split(" ")[1]
            verify_token(token)
            logger.info(f"Valid token received for {request.url.path}")

            return await call_next(request)

        except HTTPException as http_err:
            logger.error(f"HTTPException on {request.url.path}: {http_err.detail}")
            return JSONResponse(status_code=http_err.status_code, content={"detail": http_err.detail})

        except Exception as e:
            logger.exception(f"Unexpected error during authentication for {request.url.path}: {str(e)}")
            return JSONResponse(status_code=500, content={"detail": "Internal server error during authentication."})