"""This file contains the database service for the application."""

from uuid import UUID

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
  AsyncSession, async_sessionmaker, create_async_engine
)

from app.core.config import settings
from app.core.logging import logger
from app.models.database import ChatSession, User

class DatabaseService:
  """Service class for database operations.

  It uses SQLModel for ORM operations and maintains a connection pool.
  """

  def __init__(self) -> None:
    """Initialize database service with connection pool."""
    try:
      # Configure environment-specific database connection pool settings
      pool_size = settings.POSTGRES_POOL_SIZE
      max_overflow = settings.POSTGRES_MAX_OVERFLOW

      connection_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
      )

      self.engine = create_async_engine(
        url=connection_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=30,
        pool_recycle=1800,
      )

      self.session_maker = async_sessionmaker(
        bind=self.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
      )

      logger.info("database_initialized")

    except SQLAlchemyError:
      logger.exception("database_initialization_failed")
      raise

  @asynccontextmanager
  async def session_scope (self) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session, committing on success and rolling back on error."""

    async with self.session_maker() as session:
      try:
        yield session
        await session.commit()

      except SQLAlchemyError:
        await session.rollback()
        logger.exception("database_session_failed")
        raise

      finally:
        await session.close()

  async def create_user (self, email: str, password: str, username: str | None):
    """Create a new user.

    Args:
      email: User's email address
      password: Hashed password
      username: Optional display name

    Returns:
      User: The created user
    """

    async with self.session_scope() as session:
      user = User(email=email, hashed_password=password, username=username)

      session.add(user)
      await session.flush()
      await session.refresh(user)

      logger.info("user_created", user_id=user.user_id)
      return user
  
  async def get_user (self, user_id: UUID) -> Optional[User]:
    """Get a user by ID.

    Args:
      user_id: The ID of the user to retrieve

    Returns:
      Optional[User]: The user if found, None otherwise
    """

    async with self.session_maker() as session:
      statement = select(User).where(User.user_id == user_id)
      result = await session.execute(statement)
      return result.scalars().first()

  async def get_user_by_email(self, email: str) -> Optional[User]:
    """Get a user by email.

    Args:
      email: The email of the user to retrieve

    Returns:
      Optional[User]: The user if found, None otherwise
    """

    async with self.session_maker() as session:
      statement = select(User).where(User.email == email)
      result = await session.execute(statement)
      return result.scalars().one_or_none()

  async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
    """Get a chat session by its session ID.

    Args:
      session_id: The UUID of the session to retrieve

    Returns:
      Optional[ChatSession]: The session if found, None otherwise
    """

    async with self.session_maker() as session:
      statement = select(ChatSession).where(ChatSession.session_id == session_id)
      result = await session.execute(statement)
      return result.scalars().first()
  
  async def create_session (
    self,
    session_id: UUID,
    user_id: UUID,
    username: str | None,
    name: str = "",
  ) -> ChatSession:
    """Create a new chat session.

    Args:
      session_id: The ID for the new session
      user_id: The ID of the user who owns the session
      username: Display name copied from the user for LLM personalization
      name: Optional name for the session (defaults to empty string)

    Returns:
      ChatSession: The created session
    """

    async with self.session_scope() as session:
      chat_session = ChatSession(
        session_id=session_id,
        user_id=user_id,
        username=username,
        name=name,
      )

      session.add(chat_session)
      await session.flush()
      await session.refresh(chat_session)

      logger.info(
        "session_created",
        session_id=chat_session.session_id,
        user_id=chat_session.user_id,
        name=chat_session.name,
      )
      return chat_session

  async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
    """Delete a chat session owned by a user.

    Args:
      session_id: The ID of the session to delete
      user_id: The ID of the user who owns the session

    Returns:
      bool: True if a session was deleted, False otherwise
    """

    async with self.session_scope() as session:
      statement = select(ChatSession).where(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id,
      )
      result = await session.execute(statement)
      chat_session = result.scalars().one_or_none()

      if chat_session is None:
        return False

      await session.delete(chat_session)
      logger.info("session_deleted", session_id=session_id, user_id=user_id)
      return True

  async def get_user_sessions(self, user_id: UUID) -> list[ChatSession]:
    """Get all chat sessions for a user.

    Args:
      user_id: The ID of the user who owns the sessions

    Returns:
      list[ChatSession]: The user's sessions ordered by newest first
    """

    async with self.session_maker() as session:
      statement = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
      )
      result = await session.execute(statement)
      return list(result.scalars().all())

  async def update_session_name(self, session_id: UUID, user_id: UUID, name: str) -> Optional[ChatSession]:
    """Update the name for a chat session owned by a user.

    Args:
      session_id: The ID of the session to update
      user_id: The ID of the user who owns the session
      name: The new session name

    Returns:
      Optional[ChatSession]: The updated session if found, None otherwise
    """

    async with self.session_scope() as session:
      statement = select(ChatSession).where(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id,
      )
      result = await session.execute(statement)
      chat_session = result.scalars().one_or_none()

      if chat_session is None:
        return None

      chat_session.name = name
      session.add(chat_session)
      await session.flush()
      await session.refresh(chat_session)

      logger.info("session_name_updated", session_id=session_id, user_id=user_id)
      return chat_session

  async def health_check(self) -> bool:
    """Check database connection health.

    Returns:
      bool: True if database is healthy, False otherwise
    """

    try:
      async with self.session_maker() as session:
        # Execute a simple query to check connection
        result = await session.execute(select(1))
        result.first()
        return True
    except Exception:
      logger.exception("database_health_check_failed")
      return False


# Create a singleton instance
database_service = DatabaseService()
