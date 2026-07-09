import os
import streamlit as st
from supabase import create_client

@st.cache_resource
def get_client():
    """Initialize and return Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Supabase credentials not configured. Please check your environment variables.")
        return None
    
    try:
        # Remove trailing slash from URL if present
        supabase_url = supabase_url.rstrip('/')
        
        # Create client WITHOUT proxy parameter
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {str(e)}")
        return None
