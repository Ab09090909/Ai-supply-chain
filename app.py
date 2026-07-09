# app.py - Main entry point
import streamlit as st
from utils.auth import initialize_session_state, render_login

# Configure page
st.set_page_config(
    page_title="Ethiopian AgriTech Supply Chain",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)
# app.py - Add this near the top
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
# Initialize session state
initialize_session_state()

# Import page modules
from pages.producer.main import render_producer_page

def main():
    """Main application entry point"""
    
    # Sidebar navigation
    st.sidebar.title("🌾 Ethiopian AgriTech")
    st.sidebar.markdown("---")
    
    # Role-based navigation
    if st.session_state.get('authenticated', False):
        user_role = st.session_state.user_info.get('role', '')
        
        st.sidebar.write(f"👤 Logged in as: **{st.session_state.user_info.get('name', 'User')}**")
        st.sidebar.write(f"🔑 Role: **{user_role.capitalize()}**")
        st.sidebar.markdown("---")
        
        # Navigation based on role
        if user_role == 'producer':
            page = st.sidebar.radio(
                "Navigate",
                ["Producer Dashboard"]
            )
            
            if page == "Producer Dashboard":
                render_producer_page()
        
        elif user_role == 'merchant':
            st.sidebar.info("🛒 Merchant features coming soon...")
            st.title("🛒 Merchant Dashboard")
            st.info("Merchant page coming soon...")
        
        elif user_role == 'customer':
            st.sidebar.info("🛍️ Customer features coming soon...")
            st.title("🛍️ Customer Dashboard")
            st.info("Customer page coming soon...")
        
        elif user_role == 'admin':
            st.sidebar.info("⚙️ Admin features coming soon...")
            st.title("⚙️ Admin Dashboard")
            st.info("Admin page coming soon...")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()
    
    else:
        # Login/Signup page
        render_login()

if __name__ == "__main__":
    main()
