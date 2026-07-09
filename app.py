# app.py - Main entry point
import streamlit as st
from utils.auth import initialize_session_state

# Configure page
st.set_page_config(
    page_title="Ethiopian AgriTech Supply Chain",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            from pages.merchant import render_merchant_page
            page = st.sidebar.radio(
                "Navigate",
                ["Merchant Dashboard"]
            )
            if page == "Merchant Dashboard":
                render_merchant_page()
        
        elif user_role == 'customer':
            from pages.customer import render_customer_page
            page = st.sidebar.radio(
                "Navigate",
                ["Customer Dashboard"]
            )
            if page == "Customer Dashboard":
                render_customer_page()
        
        elif user_role == 'admin':
            from pages.admin import render_admin_page
            page = st.sidebar.radio(
                "Navigate",
                ["Admin Dashboard"]
            )
            if page == "Admin Dashboard":
                render_admin_page()
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()
    
    else:
        # Login page
        st.sidebar.info("🔐 Please log in to access the platform")
        from utils.auth import render_login
        render_login()

if __name__ == "__main__":
    main()
