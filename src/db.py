import os
import streamlit as st

def get_client():
    """Initialize and return Supabase client"""
    try:
        from supabase import create_client
    except ImportError:
        st.error("❌ 'supabase' package is missing. Please add it to requirements.txt")
        st.stop()

    # 1. Get credentials from .env (Local) or Streamlit Secrets (Cloud)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Fallback to Streamlit Secrets if env vars are empty
    if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
    if not SUPABASE_KEY and "SUPABASE_KEY" in st.secrets:
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    # 2. Strict Validation BEFORE calling create_client
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error(" **Supabase Credentials Missing!**")
        st.error("Please set `SUPABASE_URL` and `SUPABASE_KEY` in your Streamlit Secrets.")
        st.stop()
    
    if not SUPABASE_URL.startswith("https://"):
        st.error("❌ **Invalid Supabase URL!**")
        st.error("Your URL must start with `https://`. Please check your secrets.")
        st.stop()

    # 3. Initialize Client
    try:
        # Remove trailing slash if it exists (httpx sometimes hates it)
        SUPABASE_URL = SUPABASE_URL.rstrip('/')
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"❌ **Failed to connect to Supabase:** {str(e)}")
        st.stop()
