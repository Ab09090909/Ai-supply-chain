import streamlit as st

# Set page config FIRST (before any other streamlit commands)
st.set_page_config(
    page_title="AI Supply Chain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
}
.login-header h1 {
    text-align: center;
    color: #667eea;
}
</style>
""", unsafe_allow_html=True)

# Main app
if not st.session_state.authenticated:
    st.markdown('<div class="login-header"><h1>🚀 AI Supply Chain</h1></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    # Try to login
                    try:
                        from utils.auth import login_user
                        success, msg, user = login_user(email, password)
                        if success:
                            st.success(msg)
                            st.session_state.authenticated = True
                            st.session_state.user_info = user
                            st.rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"Login error: {str(e)}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("I am a:", ["producer", "merchant", "customer", "admin"])
            submit = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit:
                if name and email and password:
                    try:
                        from utils.auth import register_user
                        success, msg = register_user(name, email, password, role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"Registration error: {str(e)}")
                else:
                    st.error("Please fill in all fields")
else:
    # User is logged in
    st.title(f"Welcome, {st.session_state.user_info['name']}! 👋")
    st.write(f"Role: **{st.session_state.user_info['role']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📊 Navigate using the sidebar")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.rerun()
    
    # Show navigation based on role
    st.markdown("---")
    st.subheader("Quick Navigation")
    
    if st.session_state.user_info['role'] == 'producer':
        st.page_link("pages/1_producer.py", label="🏭 Producer Dashboard", icon="🏭")
    elif st.session_state.user_info['role'] == 'merchant':
        st.page_link("pages/2_merchant.py", label="🛒 Merchant Dashboard", icon="🛒")
    elif st.session_state.user_info['role'] == 'customer':
        st.page_link("pages/3_customer.py", label="️ Customer Portal", icon="️")
    elif st.session_state.user_info['role'] == 'admin':
        st.page_link("pages/4_Admin.py", label="️ Admin Panel", icon="️")
