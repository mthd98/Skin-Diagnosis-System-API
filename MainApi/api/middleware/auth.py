from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.authentication import verify_token

class AuthMiddleware(BaseHTTPMiddleware):
    """Global JWT authentication middleware for all API routes."""

    async def dispatch(self, request: Request, call_next):
        # Public routes that don't require authentication
        public_routes = ["/login", "/register", "/docs", "/openapi.json"]
        if request.url.path in public_routes:
            return await call_next(request)

        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        # Validate the JWT token
        token = auth_header.split(" ")[1]
        try:
            verify_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

        return await call_next(request)
