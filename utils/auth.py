# utils/auth.py
import streamlit as st
from datetime import datetime
from .db_helpers import authenticate_user, initialize_session_state, logout_user as db_logout, get_supabase_client

def initialize_session_state():
    """Initialize session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.session_state.user_id = None
        st.session_state.show_signup = False
        st.session_state.show_forgot_password = False

def login_user(email, password):
    """Login user and store session"""
    user_info, message = authenticate_user(email, password)
    
    if user_info:
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        st.session_state.user_id = user_info.get('id')
        st.session_state.show_signup = False
        st.session_state.show_forgot_password = False
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
    st.session_state.show_signup = False
    st.session_state.show_forgot_password = False
    st.success("✅ Logged out successfully")

def signup_user(email, password, name, phone, company_name, address, region, role):
    """Sign up a new user"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False, "Database connection failed"
        
        # Check if user already exists
        existing_user = supabase.table('users')\
            .select('email')\
            .eq('email', email)\
            .execute()
        
        if existing_user.data:
            return False, "User with this email already exists"
        
        # Create user in Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                return False, "Failed to create account"
            
            user_id = auth_response.user.id
            
        except Exception as e:
            error_msg = str(e)
            if "User already registered" in error_msg:
                return False, "User with this email already exists"
            elif "password" in error_msg.lower():
                return False, "Password must be at least 6 characters"
            else:
                return False, f"Authentication error: {error_msg}"
        
        # Create user profile in users table - only include columns that exist
        user_data = {
            'id': user_id,
            'email': email,
            'name': name,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        # Add optional fields if they exist in the table
        if phone:
            user_data['phone'] = phone
        if company_name:
            user_data['company_name'] = company_name
        if address:
            user_data['address'] = address
        if region:
            user_data['region'] = region
        
        response = supabase.table('users')\
            .insert(user_data)\
            .execute()
        
        if response.data:
            return True, "Account created successfully! Please login."
        else:
            # Clean up auth user if profile creation fails
            try:
                supabase.auth.admin.delete_user(user_id)
            except:
                pass
            return False, "Failed to create user profile"
            
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            return False, "User with this email already exists"
        else:
            return False, f"Sign up error: {error_msg}"

def reset_password(email):
    """Send password reset email"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            return False, "Database connection failed"
        
        # Check if user exists
        user = supabase.table('users')\
            .select('email')\
            .eq('email', email)\
            .execute()
        
        if not user.data:
            return False, "No account found with this email"
        
        # Send password reset email
        supabase.auth.reset_password_for_email(email)
        
        return True, "Password reset link sent to your email!"
        
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower():
            return False, "Invalid email address"
        else:
            return False, f"Error sending reset email: {error_msg}"

def render_login():
    """Render login form with sign up and forgot password toggles"""
    
    # Check if showing signup
    if st.session_state.get('show_signup', False):
        render_signup()
        return
    
    # Check if showing forgot password
    if st.session_state.get('show_forgot_password', False):
        render_forgot_password()
        return
    
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
    
    # Sign up and Forgot Password links
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 Sign Up", use_container_width=True):
            st.session_state.show_signup = True
            st.rerun()
    with col2:
        if st.button("🔑 Forgot Password?", use_container_width=True):
            st.session_state.show_forgot_password = True
            st.rerun()

def render_signup():
    """Render sign up form"""
    
    st.title("🌾 Ethiopian AgriTech")
    st.subheader("📝 Create Your Account")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Full Name *", placeholder="John Doe")
            email = st.text_input("📧 Email *", placeholder="your@email.com")
            password = st.text_input("🔑 Password *", type="password", placeholder="Min 6 characters")
            confirm_password = st.text_input("🔑 Confirm Password *", type="password", placeholder="Re-enter password")
        
        with col2:
            phone = st.text_input("📞 Phone Number", placeholder="09XX XXX XXX")
            company_name = st.text_input("🏢 Company/Business Name", placeholder="Your business name")
            address = st.text_input("📍 Address", placeholder="Your business address")
            
            regions = ["Addis Ababa", "Oromia", "Amhara", "Tigray", "SNNP", "Sidama", 
                      "Afar", "Benishangul-Gumuz", "Gambella", "Harari", "Dire Dawa", "Somali"]
            region = st.selectbox("🌍 Region", regions)
            
            role = st.selectbox(
                "👔 I want to register as *", 
                ["producer", "merchant", "customer"],
                format_func=lambda x: x.capitalize()
            )
        
        st.markdown("---")
        st.caption("📝 * Required fields")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("🚀 Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not name or not email or not password or not confirm_password:
                st.error("❌ Please fill in all required fields (*)")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                with st.spinner("Creating your account..."):
                    success, message = signup_user(
                        email=email,
                        password=password,
                        name=name,
                        phone=phone,
                        company_name=company_name,
                        address=address,
                        region=region,
                        role=role
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    st.markdown("---")
    
    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Back to Login", use_container_width=True):
            st.session_state.show_signup = False
            st.rerun()

def render_forgot_password():
    """Render forgot password form"""
    
    st.title("🌾 Ethiopian AgriTech")
    st.subheader("🔑 Reset Your Password")
    st.info("Enter your email address and we'll send you a link to reset your password.")
    
    with st.form("forgot_password_form"):
        email = st.text_input("📧 Email Address", placeholder="your@email.com")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button("📧 Send Reset Link", use_container_width=True, type="primary")
        
        if submit:
            if not email:
                st.error("❌ Please enter your email address")
            else:
                with st.spinner("Sending reset link..."):
                    success, message = reset_password(email)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("📧 Please check your email for the password reset link.")
                        if st.button("🔙 Back to Login"):
                            st.session_state.show_forgot_password = False
                            st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    st.markdown("---")
    
    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Back to Login", use_container_width=True):
            st.session_state.show_forgot_password = False
            st.rerun()
