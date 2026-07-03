"""This file contains the main application entry point."""

from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import (
  FastAPI, Request, status
)

from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from asgi_correlation_id import CorrelationIdMiddleware

from app.api.v1.main import api_router
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger

from app.services.database import database_service


app = FastAPI(
  title=settings.PROJECT_NAME,
  version=settings.VERSION,
  description=settings.DESCRIPTION,
  openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.ALLOWED_ORIGINS,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["root"][0])
async def root(request: Request):
  """Root endpoint returning basic API information."""
  logger.info("root_endpoint_called")
  return {
    "name": settings.PROJECT_NAME,
    "version": settings.VERSION,
    "status": "healthy",
    "environment": settings.ENVIRONMENT.value,
    "swagger_url": "/docs",
    "redoc_url": "/redoc",
  }

