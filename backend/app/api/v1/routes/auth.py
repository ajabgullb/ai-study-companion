"""Authentication and authorization endpoints for the API.

This module provides endpoints for user registration, login, session management,
and token verification.
"""
import uuid
from uuid import UUID

from fastapi import (
  APIRouter, HTTPException, Request, Form, Depends
)
from fastapi.security import (
  HTTPAuthorizationCredentials, HTTPBearer
)

from app.schemas.auth import UserCreate, UserResponse, TokenResponse, SessionResponse
from app.services.database import database_service

from app.models.database import ChatSession
from app.models.user import User

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging import logger, bind_context

from app.utils.auth import create_access_token, verify_token
from app.utils.sanitization import (
  sanitize_email, sanitize_string, validate_password_strength
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user (credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
  """Get the current user ID from the token.

  Args:
    credentials: The HTTP authorization credentials containing the JWT token.

  Returns:
    User: The user extracted from the token.

  Raises:
    HTTPException: If the token is invalid or missing.
  """

  try:
    # sanitize token
    token = sanitize_string(credentials.credentials)

    user_id = verify_token(token)
    if user_id is None:
      logger.error("invalid_token", token_part=token[:10] + "...")
      raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
      )

    # verify user exists in database
    parsed_user_id = UUID(user_id)
    user = await database_service.get_user(parsed_user_id)
    if user is None:
      logger.error("user_not_found", user_id=parsed_user_id)
      raise HTTPException(
        status_code=404,
        detail="User not found",
        headers={"WWW-Authenticate": "Bearer"},
      )

    # Bind user_id to logging context for all subsequent logs in this request
    bind_context(user_id=parsed_user_id)

    return user

  except ValueError as ve:
    logger.exception("token_validation_failed", error=str(ve))
    raise HTTPException(
      status_code=422,
      detail="Invalid token format",
      headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_session (
  credentials: HTTPAuthorizationCredentials = Depends(security),
) -> ChatSession:
  """Get the current session ID from the token.

  Args:
    credentials: The HTTP authorization credentials containing the JWT token.

  Returns:
    Session: The session extracted from the token.

  Raises:
    HTTPException: If the token is invalid or missing.
  """

  try:
    # Sanitize token
    token = sanitize_string(credentials.credentials)

    session_id = verify_token(token)
    if session_id is None:
      logger.error("session_id_not_found", token_part=token[:10] + "...")
      raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
      )

    # Sanitize session_id before using it
    session_id = UUID(sanitize_string(session_id))

    # Verify session exists in database
    session = await database_service.get_session(session_id)
    if session is None:
      logger.error("session_not_found", session_id=session_id)
      raise HTTPException(
        status_code=404,
        detail="Session not found",
        headers={"WWW-Authenticate": "Bearer"},
      )

    # Bind user_id to logging context for all subsequent logs in this request
    bind_context(user_id=session.user_id)

    return session
  
  except ValueError as ve:
    logger.exception("token_validation_failed", error=str(ve))
    raise HTTPException(
      status_code=422,
      detail="Invalid token format",
      headers={"WWW-Authenticate": "Bearer"},
    )


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
    logger.exception("user_registration_validation_failed", error=str(ve))
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
    logger.exception("login_validation_failed", error=str(ve))
    raise HTTPException(status_code=422, detail=str(ve))


@router.post("/session", response_model=SessionResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["session"][0])
async def create_session(request: Request, user: User = Depends(get_current_user)):
  """Create a new chat session for the authenticated user.

  Args:
    user: The authenticated user

  Returns:
    SessionResponse: The session ID, name, and access token
  """
  try:
    # Generate a unique session ID
    session_id = uuid.uuid4()

    # Create session in database, copying username for LLM personalization
    session = await database_service.create_session(session_id, user.user_id, username=user.username)
  
    # Create access token for the session
    token = create_access_token(str(session_id))

    logger.info(
      "session_created",
      session_id=session_id,
      user_id=user.user_id,
      name=session.name,
      expires_at=token.expires_at.isoformat(),
    )

    return SessionResponse(session_id=str(session_id), name=session.name, token=token)
  
  except ValueError as ve:
    logger.exception("session_creation_validation_failed", error=str(ve), user_id=user.user_id)
    raise HTTPException(status_code=422, detail=str(ve))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str, current_session: ChatSession = Depends(get_current_session)):
  """Delete a session for the authenticated user.

  Args:
    session_id: The ID of the session to delete
    current_session: The current session from auth

  Returns:
    None
  """
  try:
    # Sanitize inputs
    sanitized_session_id = sanitize_string(session_id)
    sanitized_current_session = sanitize_string(str(current_session.session_id))

    # Verify the session ID matches the authenticated session
    if sanitized_session_id != sanitized_current_session:
      raise HTTPException(status_code=403, detail="Cannot delete other sessions")

    # Delete the session
    await database_service.delete_session(sanitized_session_id, current_session.user_id)

    logger.info("session_deleted", session_id=session_id, user_id=current_session.user_id)
  
  except ValueError as ve:
    logger.exception("session_deletion_validation_failed", error=str(ve), session_id=session_id)
    raise HTTPException(status_code=422, detail=str(ve))


@router.patch("/sessions", response_model=SessionResponse)
async def get_user_sessions (user: User = Depends(get_current_user)):
  """Get all session IDs for the authenticated user.

  Args:
    user: The authenticated user

  Returns:
    List[SessionResponse]: List of session IDs
  """

  try:
    sessions = await database_service.get_user_sessions(user.user_id)

    return [
      SessionResponse(
        session_id=sanitize_string(str(session.session_id)),
        name=sanitize_string(session.name),
        token=create_access_token(str(session.session_id)),
      )

      for session in sessions
    ]

  except ValueError as ve:
    logger.exception("get_sessions_validation_failed", user_id=user.user_id, error=str(ve))
    raise HTTPException(status_code=422, detail=str(ve))


