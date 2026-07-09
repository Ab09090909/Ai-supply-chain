import streamlit as st
from utils.auth import initialize_session_state

# Initialize
initialize_session_state()

# Auth check
if not st.session_state.authenticated:
    st.error("Please login")
    st.stop()

if st.session_state.user_info['role'] != 'producer':
    st.error("Producer access only")
    st.stop()

st.title("🏭 Producer Dashboard")
st.write("Testing modular structure...")

# Try importing
try:
    from producer.profile import render_profile
    st.success("✅ Imports working!")
    
    # Show profile
    render_profile(st.session_state.user_info)
    
    # Simple tabs
    tab1, tab2 = st.tabs(["Dashboard", "Inventory"])
    
    with tab1:
        st.write("Dashboard tab works!")
    
    with tab2:
        st.write("Inventory tab works!")
        
except ImportError as e:
    st.error(f" Import failed: {e}")
    st.error("Check that producer/__init__.py exists")
