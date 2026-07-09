import os
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """
    Initialize and return Supabase client
    This is the ONLY place where Supabase client is created
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("❌ Supabase credentials not configured")
        st.stop()
        return None
    
    try:
        # Create client WITHOUT proxy parameter
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"❌ Failed to connect to Supabase: {str(e)}")
        return None
