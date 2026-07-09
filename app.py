import streamlit as st

# THIS MUST BE FIRST - before any other st. commands
st.set_page_config(
    page_title="AI Supply Chain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.current_page = 'dashboard'

# Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
}
.login-header h1 {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2rem;
}
.nav-button {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 15px;
    margin: 5px 0;
    cursor: pointer;
    transition: all 0.3s;
}
.nav-button:hover {
    background-color: #334155;
    border-color: #667eea;
}
</style>
""", unsafe_allow_html=True)

# Navigation function
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# Main app
if not st.session_state.authenticated:
    st.markdown('<div class="login-header"><h1>🚀 AI Supply Chain</h1><p style="text-align:center;color:#94a3b8">Intelligent Supply Chain Management</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", " Sign Up"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
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
    
    with tab2:
        with st.form("signup_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
            with col2:
                password = st.text_input("Password", type="password")
                role = st.selectbox("I am a:", ["producer", "merchant", "customer", "admin"])
            
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if not name or not email or not password:
                    st.error("Please fill in all fields")
                else:
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
    # User is logged in - Show sidebar navigation
    user_info = st.session_state.user_info
    
    with st.sidebar:
        st.title(" Navigation")
        st.write(f" **{user_info['name']}**")
        st.write(f"🎯 Role: *{user_info['role'].title()}*")
        st.markdown("---")
        
        # Navigation based on role
        if user_info['role'] == 'producer':
            if st.button("🏭 Producer Dashboard", use_container_width=True, 
                        key="nav_producer", type="primary" if st.session_state.current_page == 'producer' else "secondary"):
                navigate_to('producer')
        elif user_info['role'] == 'merchant':
            if st.button("🛒 Merchant Dashboard", use_container_width=True,
                        key="nav_merchant", type="primary" if st.session_state.current_page == 'merchant' else "secondary"):
                navigate_to('merchant')
        elif user_info['role'] == 'customer':
            if st.button("🛍️ Customer Portal", use_container_width=True,
                        key="nav_customer", type="primary" if st.session_state.current_page == 'customer' else "secondary"):
                navigate_to('customer')
        elif user_info['role'] == 'admin':
            if st.button(" Admin Panel", use_container_width=True,
                        key="nav_admin", type="primary" if st.session_state.current_page == 'admin' else "secondary"):
                navigate_to('admin')
        
        st.markdown("---")
        if st.button(" Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_info = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Main content based on current page
    if st.session_state.current_page == 'login':
        st.title(f"Welcome, {user_info['name']}! 👋")
        st.write("Select a page from the sidebar to continue.")
    else:
        # Import and run the page
        if st.session_state.current_page == 'producer':
            import pages._1_producer as producer_page
            producer_page.run()
        elif st.session_state.current_page == 'merchant':
            import pages._2_merchant as merchant_page
            merchant_page.run()
        elif st.session_state.current_page == 'customer':
            import pages._3_customer as customer_page
            customer_page.run()
        elif st.session_state.current_page == 'admin':
            import pages._4_Admin as admin_page
            admin_page.run()
