"""Authentication and authorization endpoints for the API.

This module provides endpoints for user registration, login, session management,
and token verification.
"""

from fastapi import (
  APIRouter, HTTPException, Request, Form
)
from fastapi.security import (
  HTTPAuthorizationCredentials, HTTPBearer
)

from app.schemas.auth import UserCreate, UserResponse, TokenResponse
from app.services.database import database_service
from app.models.user import User

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger

from app.utils.auth import create_access_token
from app.utils.sanitization import (
  sanitize_email, sanitize_string, validate_password_strength
)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["register"][0])
async def register_user (request: Request, payload: UserCreate):
  """Register a new user.

  Args:
    request: The FastAPI request object for rate limiting.
    user_data: User registration data

  Returns:
    UserResponse: The created user info
  """

  try:
    # sanitize email
    sanitized_email = sanitize_email(payload.email)

    # extract and validate password
    password = payload.password
    validate_password_strength(password)

    # check if user exists
    if await database_service.get_user_by_email(sanitized_email):
      raise HTTPException(status_code=400, detail="Email already Registered!")
    
    # sanitize optional username
    sanitized_username = sanitize_string(payload.username) if payload.username else None

    # create user
    user = await database_service.create_user(
      email=sanitized_email,
      password=User.hash_password(password),
      username=sanitized_username
    )

    # create access token
    token = create_access_token(str(user.user_id))

    return UserResponse(id=user.user_id, email=user.email, username=user.username, token=token)
  
  except ValueError as ve:
    logger.exception(f"user_registration_validation_failed: {ve}")
    raise HTTPException(status_code=422, detail=str(ve))


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["login"][0])
async def login (
  request: Request, email: str = Form(...), password: str = Form(...), grant_type: str = Form(default="password")
  ):

  """Login a user.

  Args:
    request: The FastAPI request object for rate limiting.
    email: User's email
    password: User's password
    grant_type: Must be "password"

  Returns:
    TokenResponse: Access token information

  Raises:
    HTTPException: If credentials are invalid
  """

  try:
    # Sanitize inputs
    email = sanitize_string(email)
    password = sanitize_string(password)
    grant_type = sanitize_string(grant_type)

    # Verify grant type
    if grant_type != "password":
      raise HTTPException(
        status_code=400,
        detail="Unsupported grant type. Must be 'password'",
      )
    
    user = await database_service.get_user_by_email(email)

    if not user or not user.verify_password(password):
      raise HTTPException(
        status_code=401,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
      )
    
    token = create_access_token(str(user.user_id))
    return TokenResponse(access_token=token.access_token, token_type="bearer", expires_at=token.expires_at)
  
  except ValueError as ve:
    logger.exception("Login Validation Failed", error=str(ve))
    raise HTTPException(status_code=422, detail=str(ve))

