"""This file contains the thread model for the application."""

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Thread(SQLModel):
  """Thread model for storing conversation threads.

  Attributes:
    id: The primary key
    created_at: When the thread was created
    messages: Relationship to messages in this thread
  """

  thread_id: UUID = Field(default_factory=uuid4, primary_key=True)

