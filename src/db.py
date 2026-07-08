"""
src/db.py — Supabase Client Initialization
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env (local development)
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# GLOBALS
# ─────────────────────────────────────────────────────────────
_supabase_client: Optional[Client] = None

# ─────────────────────────────────────────────────────────────
# CLIENT INITIALIZATION
# ─────────────────────────────────────────────────────────────

def get_supabase_client() -> Optional[Client]:
    """
    Creates and returns a Supabase client instance.
    Reads credentials from environment variables or Streamlit secrets.
    
    Returns:
        Optional[Client]: Supabase client or None if initialization fails
    """
    global _supabase_client
    
    # Return cached client if available
    if _supabase_client is not None:
        return _supabase_client
    
    try:
        # Try to get credentials from various sources
        url = None
        key = None
        
        # 1. Try Streamlit Cloud secrets first (for deployment)
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and st.secrets:
                url = st.secrets.get("SUPABASE_URL")
                key = st.secrets.get("SUPABASE_KEY")
                if url and key:
                    logger.info("Using Supabase credentials from Streamlit secrets")
        except ImportError:
            # Streamlit not available, skip
            pass
        except Exception as e:
            logger.warning(f"Error accessing Streamlit secrets: {e}")
        
        # 2. Fallback to environment variables
        if not url:
            url = os.environ.get("SUPABASE_URL")
        if not key:
            key = os.environ.get("SUPABASE_KEY")
        
        # 3. Fallback to .env file (already loaded)
        if not url:
            url = os.getenv("SUPABASE_URL")
        if not key:
            key = os.getenv("SUPABASE_KEY")
        
        # Validate credentials
        if not url or not key:
            logger.error("Supabase credentials not found in secrets, env, or .env file")
            return None
        
        # Create client
        logger.info(f"Initializing Supabase client with URL: {url[:30]}...")
        _supabase_client = create_client(url, key)
        
        # Test connection with a simple query
        try:
            # Try to fetch a single row to verify connection
            test_response = _supabase_client.table("profiles").select("id", count="exact").limit(1).execute()
            if test_response is not None:
                logger.info("Supabase connection verified successfully")
            else:
                logger.warning("Supabase connection test returned empty response")
        except Exception as e:
            logger.warning(f"Supabase connection test failed: {e}")
            # Still return the client even if test fails
        
        return _supabase_client
        
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def get_client() -> Optional[Client]:
    """
    Alias for get_supabase_client() for backward compatibility.
    """
    return get_supabase_client()

def init_supabase() -> Optional[Client]:
    """
    Initialize Supabase client and verify connection.
    This is the main entry point for the application.
    
    Returns:
        Optional[Client]: Supabase client or None if initialization fails
    """
    client = get_supabase_client()
    
    if client is None:
        logger.error("Failed to initialize Supabase client")
        return None
    
    # Try to verify connection
    try:
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        if response is not None:
            logger.info("Supabase connection established and verified")
        else:
            logger.warning("Supabase connection established but verification failed")
    except Exception as e:
        logger.error(f"Supabase verification failed: {e}")
        # Still return the client
    
    return client

# ─────────────────────────────────────────────────────────────
# CONNECTION STATUS
# ─────────────────────────────────────────────────────────────

def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    client = get_supabase_client()
    if client is None:
        return False
    
    try:
        # Try a simple query
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return response is not None
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

def get_db_status() -> dict:
    """
    Get detailed database connection status.
    
    Returns:
        dict: Status information
    """
    client = get_supabase_client()
    if client is None:
        return {
            "status": "error",
            "message": "Supabase client not initialized",
            "url": None
        }
    
    try:
        # Test connection
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return {
            "status": "connected",
            "message": "Database connection healthy",
            "has_data": bool(response and response.data),
            "url": os.environ.get("SUPABASE_URL", "Unknown")[:30] + "..."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)[:100]}",
            "url": os.environ.get("SUPABASE_URL", "Unknown")[:30] + "..."
        }

# ─────────────────────────────────────────────────────────────
# TABLE HELPERS
# ─────────────────────────────────────────────────────────────

def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        table_name: Name of the table to check
    
    Returns:
        bool: True if table exists, False otherwise
    """
    client = get_supabase_client()
    if client is None:
        return False
    
    try:
        response = client.table(table_name).select("id", count="exact").limit(1).execute()
        return response is not None
    except Exception:
        return False

def get_table_count(table_name: str) -> int:
    """
    Get the count of rows in a table.
    
    Args:
        table_name: Name of the table
    
    Returns:
        int: Number of rows or 0 if error
    """
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
# RE-EXPORT SUPABASE CLIENT (Backward Compatibility)
# ─────────────────────────────────────────────────────────────

# For backward compatibility with code that imports `supabase` directly
# Initialize the client once
supabase = init_supabase()

# Export the client and functions
__all__ = [
    'supabase',
    'get_supabase_client',
    'get_client',
    'init_supabase',
    'check_db_connection',
    'get_db_status',
    'table_exists',
    'get_table_count'
]

# ─────────────────────────────────────────────────────────────
# USAGE EXAMPLE (for testing)
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test the database connection
    client = init_supabase()
    if client:
        print("✅ Supabase client initialized successfully")
        
        # Check tables
        tables = ["profiles", "products", "orders", "notifications"]
        for table in tables:
            exists = table_exists(table)
            count = get_table_count(table) if exists else 0
            print(f"  📊 {table}: {'✓' if exists else '✗'} ({count} rows)")
        
        # Get status
        status = get_db_status()
        print(f"  🔌 Status: {status.get('status')} - {status.get('message')}")
    else:
        print("❌ Failed to initialize Supabase client")
