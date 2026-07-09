import streamlit as st

# Lazy import with error handling
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    # The app will still run, but chatbot features will be disabled

def get_groq_client():
    if not GROQ_AVAILABLE:
        st.error("❌ 'groq' package is not installed. Please add it to requirements.txt")
        return None
    
    import os
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        st.error("❌ GROQ_API_KEY is missing.")
        return None
        
    return Groq(api_key=api_key)

# ... rest of your chatbot code ...
