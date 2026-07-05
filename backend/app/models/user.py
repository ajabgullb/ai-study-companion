"""This file contains the user model for the application."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional, List, TYPE_CHECKING

import bcrypt
from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
  from app.models.session import Session


class UserBase (SQLModel):
  """Base User for User Class"""

  created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column=Column(DateTime(timezone=True), nullable=False)
  )
  email: EmailStr = Field(unique=True, index=True, max_length=250)
  is_active: bool = True
  is_superuser: bool = False
  full_name: str | None = Field(default=None, max_length=255)
  

class User(UserBase, table=True):
  """User model for storing user accounts.

  Attributes:
    id: The primary key
    email: User's email (unique)
    hashed_password: Bcrypt hashed password
    username: Optional display name for the user
    created_at: When the user was created
    sessions: Relationship to user's chat sessions
  """

  __tablename__ = "users"  # type: ignore[assignment]

  user_id: UUID = Field(default_factory=uuid4, primary_key=True)
  email: str = Field(unique=True, index=True)
  hashed_password: str
  username: Optional[str] = Field(default=None, index=False)
  sessions: List["Session"] = Relationship(back_populates="user")

  def verify_password(self, password: str) -> bool:
    """Verify if the provided password matches the hash."""

    return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password.encode("utf-8"))

  @staticmethod
  def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""

    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# Avoid circular imports
from app.models.session import Session
