"""This file contains the main application entry point."""

from fastapi import FastAPI

from app.core.config import settings



app = FastAPI(
  title=settings.PROJECT_NAME,
  version=settings.VERSION,
  description=settings.DESCRIPTION,
  # openapi_url=settings.OPENAPI_URL
)


@app.get("/")
def read_root ():
  return {"message": "Hello, Ajab!"}


