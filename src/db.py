import os
import streamlit as st

# Import supabase safely
try:
    from supabase import create_client, Client
except ImportError:
    st.error("❌ Missing 'supabase' package. Please add 'supabase' to your requirements.txt")
    st.stop()

def get_client():
    """Returns the Supabase client instance"""
    # Get credentials from .env (local) or Streamlit Secrets (cloud)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Fallback to Streamlit Secrets if env vars are empty
    if not SUPABASE_URL and "SUPABASE_URL" in st.secrets:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
    if not SUPABASE_KEY and "SUPABASE_KEY" in st.secrets:
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Supabase URL and Key are missing. Check your .env file or Streamlit Secrets.")
        st.stop()

    return create_client(SUPABASE_URL, SUPABASE_KEY)
