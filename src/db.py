import os
import streamlit as st

def get_client():
    """Initialize and return Supabase client"""
    try:
        from supabase import create_client
    except ImportError:
        st.error("❌ 'supabase' package is missing. Please add it to requirements.txt")
        st.stop()

    # Get credentials from .env or Streamlit Secrets
    SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY", "")

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Supabase credentials missing. Check .env or Streamlit Secrets.")
        st.stop()

    return create_client(SUPABASE_URL, SUPABASE_KEY)
