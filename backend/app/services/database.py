"""This file contains the database service for the application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from app.core.config import settings
from app.core.logging import logger

from app.models.user import User

from sqlalchemy.ext.asyncio import (
  create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import select

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
        max_overflow= max_overflow,
        pool_timeout=30,
        pool_recycle=1800,
      )

      self.session_maker = async_sessionmaker(
        bind=self.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
      )

      logger.info("Database Intialized!")

    except SQLAlchemyError as e:
      logger.error(f"Database Initialization Error: {e}")
      raise

  async def create_user (self, email: str, password: str, username: str | None):
    """Create a new user.

    Args:
      email: User's email address
      password: Hashed password
      username: Optional display name

    Returns:
      User: The created user
    """

    async with self.get_session() as session:
      user = User(email=email, hashed_password=password, username=username)

      session.add(user)
      await session.commit()
      await session.refresh(user)

      logger.info("User Created!")
      return user

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

  @asynccontextmanager
  async def get_session (self) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session, committing on success and rolling back on error."""

    async with self.session_maker() as session:
      try:
        yield session
        await session.commit()

      except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        raise

      finally:
        await session.close()

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
    except Exception as e:
      logger.error(f"database_health_check_failed {e}")
      return False


# Create a singleton instance
database_service = DatabaseService()

