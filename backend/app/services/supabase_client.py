"""This file contains the Supabase client logic"""

from supabase import create_client, Client
from app.core.config import settings


supabase: Client = create_client(
  supabase_url=settings.SUPABASE_URL,
  supabase_key=settings.SUPABASE_PUBLISHABLE_KEY,
)


