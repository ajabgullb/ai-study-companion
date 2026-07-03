"""This file contains the schemas for the applicaiton"""

from app.schemas.auth import Token
from app.schemas.base import BaseResponse


__all__ = [
  "Token",
  "BaseResponse",
]
