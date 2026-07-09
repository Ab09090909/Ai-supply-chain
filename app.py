import streamlit as st

# Set page config
st.set_page_config(
    page_title="PlyChain - Login",
    page_icon="🚀",
    layout="centered",
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
</style>
""", unsafe_allow_html=True)

# ==========================================
# MAIN APP
# ==========================================
if not st.session_state.authenticated:
    st.title(" SupplyChain")
    st.markdown("### Intelligent Supply Chain Management for Ethiopia")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                if not email or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    # Import from utils.auth
                    from utils.db_helpers import login_user
                    success, msg, user = login_user(email, password)
                    if success:
                        st.success(msg)
                        st.session_state.authenticated = True
                        st.session_state.user_info = user
                        st.rerun()
                    else:
                        st.error(msg)
    
    with tab2:
        with st.form("signup_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email")
            with col2:
                password = st.text_input("Password", type="password")
                role = st.selectbox("I am a:", ["producer", "merchant", "customer", "admin"])
            
            phone = st.text_input("Phone Number (Optional)")
            company = st.text_input("Company Name (Optional)")
            
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if not name or not email or not password:
                    st.error("❌ Please fill in all required fields")
                else:
                    # Import from utils.auth
                    from utils.db_helpers import register_user
                    success, msg = register_user(
                        name=name, email=email, password=password, 
                        role=role, phone=phone, company_name=company
                    )
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
else:
    # User is logged in
    user_info = st.session_state.user_info
    
    st.title(f"Welcome back, {user_info['name']}! 👋")
    st.write(f"Role: **{user_info['role'].title()}**")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.rerun()
    
    st.markdown("---")
    st.subheader("Quick Navigation")
    
    role = user_info['role']
    if role == 'producer':
        st.page_link("pages/1_producer.py", label=" Producer Dashboard", icon="🏭")
    elif role == 'merchant':
        st.page_link("pages/2_merchant.py", label=" Merchant Dashboard", icon="🛒")
    elif role == 'customer':
        st.page_link("pages/3_customer.py", label="🛍️ Customer Portal", icon="🛍️")
    elif role == 'admin':
        st.page_link("pages/4_Admin.py", label="👑 Admin Panel", icon="👑")
