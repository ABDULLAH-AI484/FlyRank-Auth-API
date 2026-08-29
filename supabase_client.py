"""Supabase client initialization.

This module creates and exports a single Supabase client instance
configured from environment variables.
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL", "")
supabase_key: str = os.environ.get("SUPABASE_KEY", "")

if not supabase_url or not supabase_key:
    raise ValueError(
        "Missing SUPABASE_URL or SUPABASE_KEY in .env. "
        "Copy .env.example to .env and fill in your Supabase credentials."
    )

supabase: Client = create_client(supabase_url, supabase_key)
print("✅ Supabase client initialized")
