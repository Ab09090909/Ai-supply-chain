# app.py - Main entry point
import streamlit as st
from utils.auth import initialize_session_state, render_login
from utils.theme import initialize_theme, get_theme_css, render_theme_toggle

# Configure page
st.set_page_config(
    page_title="Ethiopian AgriTech Supply Chain",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
initialize_session_state()
initialize_theme()

# Apply theme CSS
st.markdown(f'<style>{get_theme_css()}</style>', unsafe_allow_html=True)

# Import page modules
from pages.producer.main import render_producer_page

def main():
    """Main application entry point"""
    
    # Sidebar navigation
    st.sidebar.title("🌾 Ethiopian AgriTech")
    st.sidebar.markdown("---")
    
    # Theme toggle
    render_theme_toggle()
    
    # Role-based navigation
    if st.session_state.get('authenticated', False):
        user_role = st.session_state.user_info.get('role', '')
        
        # Show user info with profile image indicator
        user_name = st.session_state.user_info.get('name', 'User')
        has_image = st.session_state.user_info.get('profile_image') and os.path.exists(st.session_state.user_info.get('profile_image', ''))
        image_indicator = "📷" if has_image else "👤"
        
        st.sidebar.write(f"{image_indicator} Logged in as: **{user_name}**")
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
