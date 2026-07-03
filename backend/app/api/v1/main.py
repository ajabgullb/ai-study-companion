"""API v1 router configuration.

This module sets up the main API router and includes all sub-routers for different
endpoints like authentication and chatbot functionality.
"""

from datetime import datetime

from fastapi import (
  APIRouter, Request, status
)
from fastapi.responses import JSONResponse

from app.services.database import database_service

from app.core.logging import logger
from app.core.limiter import limiter
from app.core.config import settings
from app.api.v1.routes.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])


@api_router.get("/health")
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["health"][0])
async def health_check(request: Request) -> JSONResponse:
  """Health check endpoint with environment-specific information.

  Returns:
    JSONResponse: Health status payload, with HTTP 503 when the
    database is unreachable so load balancers can drop the instance.
  """

  logger.info("health_check_called")

  # Check database connectivity
  db_healthy = await database_service.health_check()

  response = {
    "status": "healthy" if db_healthy else "degraded",
    "version": settings.VERSION,
    "environment": settings.ENVIRONMENT.value,
    "components": {"api": "healthy", "database": "healthy" if db_healthy else "unhealthy"},
    "timestamp": datetime.now().isoformat(),
  }

  # If DB is unhealthy, set the appropriate status code
  status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
  return JSONResponse(content=response, status_code=status_code)
