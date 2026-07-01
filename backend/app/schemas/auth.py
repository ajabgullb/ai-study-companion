"""This file contains all of the schemas for auth"""

import json

from app.services.supabase_client import supabase
from app.models.user import User
from app.utils.sanitization import (
  sanitize_email, sanitize_string, validate_password_strength
)

class Auth:
  """Auth class for authentication"""

  async def create_user (self, email, full_name, password, username):
    sanitized_email = sanitize_email (email=email)
    sanitized_name = sanitize_string (full_name)
    sanitized_username = sanitize_string (username)

    if not validate_password_strength(password):
      raise ValueError(
        "Password must be at least 8 characters and include "
        "uppercase, lowercase, a digit, and a special character."
      )

    hashed_password = User.hash_password(password=password)

    user = User(
      email=sanitized_email,
      full_name=sanitized_name,
      hashed_password=hashed_password,
      username=sanitized_username
    )

    json_user = json.dumps(user.__dict__, indent=4)

    try:
      response = await (
        supabase.table("users")
        .insert(json_user)
        .execute()
      )

    except Exception as exc:
      raise ValueError(
        f"Database insert failed: {exc}"
      ) from exc

