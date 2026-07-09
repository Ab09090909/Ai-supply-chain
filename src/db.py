"""
src/db.py — Supabase Client Initialization
"""
import os
import logging
from typing import Optional
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_supabase_client: Optional[Client] = None
_supabase_url: Optional[str] = None  # cached for status reporting

# ─────────────────────────────────────────────────────────────
# CLIENT INITIALIZATION
# ─────────────────────────────────────────────────────────────

def _get_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Resolve Supabase credentials.
    Priority:
      1. Streamlit secrets  (Streamlit Community Cloud)
      2. Environment variables (local dev / Docker)
    """
    url, key = None, None

    # 1. Streamlit secrets (preferred on Community Cloud)
    try:
        import streamlit as st
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        if url and key:
            logger.info("Supabase credentials loaded from Streamlit secrets")
            return url, key
    except Exception:
        pass  # Streamlit not running or secrets not configured

    # 2. Environment variables (local development)
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if url and key:
        logger.info("Supabase credentials loaded from environment variables")
        return url, key

    logger.error("Supabase credentials not found in st.secrets or environment variables")
    return None, None


def get_supabase_client() -> Optional[Client]:
    """
    Returns a cached Supabase client, initializing it on first call.
    """
    global _supabase_client, _supabase_url

    if _supabase_client is not None:
        return _supabase_client

    url, key = _get_credentials()
    if not url or not key:
        return None

    try:
        _supabase_url = url
        _supabase_client = create_client(url, key)
        logger.info(f"Supabase client initialized: {url[:30]}...")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


def get_client() -> Optional[Client]:
    """Alias for get_supabase_client() — backward compatibility."""
    return get_supabase_client()


def init_supabase() -> Optional[Client]:
    """
    Initialize and verify Supabase client.
    Main entry point called at module load time.
    """
    client = get_supabase_client()
    if client is None:
        logger.error("Supabase client could not be initialized")
        return None

    # Single lightweight connection test
    try:
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        if response is not None:
            logger.info("Supabase connection verified")
    except Exception as e:
        logger.warning(f"Supabase connection test failed (client still returned): {e}")

    return client

# ─────────────────────────────────────────────────────────────
# CONNECTION STATUS
# ─────────────────────────────────────────────────────────────

def check_db_connection() -> bool:
    """Returns True if the database is reachable."""
    client = get_supabase_client()
    if client is None:
        return False
    try:
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return response is not None
    except Exception as e:
        logger.error(f"DB connection check failed: {e}")
        return False


def get_db_status() -> dict:
    """Returns a dict describing the current connection status."""
    client = get_supabase_client()
    short_url = (_supabase_url[:30] + "...") if _supabase_url else "Unknown"

    if client is None:
        return {
            "status": "error",
            "message": "Supabase client not initialized",
            "url": short_url,
        }

    try:
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return {
            "status": "connected",
            "message": "Database connection healthy",
            "has_data": bool(response and response.data),
            "url": short_url,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)[:100]}",
            "url": short_url,
        }

# ─────────────────────────────────────────────────────────────
# TABLE HELPERS
# ─────────────────────────────────────────────────────────────

def table_exists(table_name: str) -> bool:
    """Returns True if the given table exists and is queryable."""
    client = get_supabase_client()
    if client is None:
        return False
    try:
        client.table(table_name).select("id", count="exact").limit(1).execute()
        return True
    except Exception:
        return False


def get_table_count(table_name: str) -> int:
    """Returns the row count for a table, or 0 on error."""
    client = get_supabase_client()
    if client is None:
        return 0
    try:
        response = client.table(table_name).select("id", count="exact").execute()
        return response.count if response else 0
    except Exception as e:
        logger.error(f"Failed to get count for {table_name}: {e}")
        return 0

# ─────────────────────────────────────────────────────────────
# MODULE-LEVEL CLIENT (backward compatibility)
# ─────────────────────────────────────────────────────────────

supabase = init_supabase()

__all__ = [
    "supabase",
    "get_supabase_client",
    "get_client",
    "init_supabase",
    "check_db_connection",
    "get_db_status",
    "table_exists",
    "get_table_count",
]

# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    client = init_supabase()
    if client:
        print("✅ Supabase client initialized successfully")
        tables = ["profiles", "products", "orders", "notifications"]
        for table in tables:
            exists = table_exists(table)
            count = get_table_count(table) if exists else 0
            print(f"  📊 {table}: {'✓' if exists else '✗'} ({count} rows)")
        status = get_db_status()
        print(f"  🔌 Status: {status['status']} — {status['message']}")
    else:
        print("❌ Failed to initialize Supabase client")
