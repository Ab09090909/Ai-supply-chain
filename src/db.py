
"""
src/db.py — Supabase Client Initialization
"""
from dotenv import load_dotenv
load_dotenv() # This loads the .env file automatically
import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """
    Creates and returns a Supabase client instance.
    Reads credentials from environment variables.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY environment variables.")
    
    return create_client(url, key)
