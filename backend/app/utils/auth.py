"""This file contains the authentication utilities for the application."""

import re
from datetime import UTC, datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.core.logging import logger
from app.utils.sanitization import sanitize_string
from app.schemas.auth import Token


def create_access_token (thread_id: str, expires_delta: Optional[timedelta]= None) -> Token:
  """Create a new access token for a thread.

  Args:
    thread_id: The unique thread ID for the conversation.
    expires_delta: Optional expiration time delta.

  Returns:
    Token: The generated access token.
  """

  if expires_delta:
    expire = datetime.now(UTC) + expires_delta
  else:
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
  
  to_encode = {
    "sub": thread_id,
    "exp": expire,
    "iat": datetime.now(UTC),
    "jti": sanitize_string(f"{thread_id}-{datetime.now(UTC).timestamp()}"),  # Add unique token identifier
  }

  encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
  logger.info("Access Token Created!")

  return Token(access_token=encoded_jwt, expires_at=expire)

