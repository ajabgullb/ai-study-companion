"""This file contains the Base class for all Models"""

from datetime import datetime, UTC

from sqlmodel import SQLModel
from pydantic import Field


class Base (SQLModel):
  """Base class for all Models"""

  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


