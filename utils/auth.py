# utils/auth.py
import streamlit as st
from .db_helpers import authenticate_user, initialize_session_state, logout_user as db_logout

def initialize_session_state():
    """Initialize session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.session_state.user_id = None

def login_user(email, password):
    """Login user and store session"""
    user_info, message = authenticate_user(email, password)
    
    if user_info:
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.user_id = user_info.get('id')
        st.success(f"✅ Welcome back, {user_info.get('name', 'User')}!")
        return True, "Login successful"
    else:
        st.error(f"❌ {message}")
        return False, message

def logout_user():
    """Logout user"""
    db_logout()
    st.session_state.authenticated = False
    st.session_state.user_info = {}
    st.session_state.user_id = None
    st.success("✅ Logged out successfully")

def render_login():
    """Render login form"""
    st.title("🌾 Ethiopian AgriTech")
    st.subheader("🔐 Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("❌ Please fill in all fields")
            else:
                success, message = login_user(email, password)
                if success:
                    st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 🆕 Don't have an account?
    - **Producers**: Contact admin to register your business
    - **Merchants**: Contact admin to join the platform
    - **Customers**: Ask your local merchant for access
    """)
