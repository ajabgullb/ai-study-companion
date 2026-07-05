"""This file contains the session model for the application."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
  from app.models.user import User


class Session(SQLModel, table=True):
  """Session model for storing chat sessions.

  Attributes:
    id: The primary key
    user_id: Foreign key to the user
    name: Name of the session (defaults to empty string)
    username: Display name copied from the user at session creation
    created_at: When the session was created
    messages: Relationship to session messages
    user: Relationship to the session owner
  """

  __tablename__ = "sessions"  # type: ignore[assignment]

  created_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column=Column(DateTime(timezone=True), nullable=False)
  )
  session_id: UUID = Field(default_factory=uuid4, primary_key=True)
  user_id: UUID = Field(foreign_key="users.user_id")
  name: str = Field(default="")
  username: Optional[str] = Field(default=None)
  user: "User" = Relationship(back_populates="sessions")

