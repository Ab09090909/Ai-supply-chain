"""
app.py — Ethiopian AI Supply Chain Platform (Main Entry)
"""
import sys
import os
import streamlit as st
import logging
from dotenv import load_dotenv

# Load environment variables from .env (local development only)
load_dotenv()

# ─────────────────────────────────────────────────────────────
# STREAMLIT CLOUD SECRETS BRIDGE (SECURE)
# ─────────────────────────────────────────────────────────────
# Only set specific required environment variables from secrets
# Don't expose all secrets as environment variables
REQUIRED_SECRETS = [
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'SUPABASE_SERVICE_ROLE',
    'GROQ_API_KEY',
    'APP_SECRET_KEY'
]

# Set only required secrets as environment variables
if hasattr(st, 'secrets') and st.secrets:
    for key in REQUIRED_SECRETS:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
        else:
            # For development, try to get from .env
            if key not in os.environ:
                logging.warning(f"Missing required secret: {key}")

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# ─────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────
try:
    from utils.theme import inject_theme, render_theme_toggle
    from utils.auth import sign_in, sign_up, sign_out, forgot_password
    from utils.constants import REGIONS, SECTORS, SESSION_KEYS
    from utils.db_helpers import supabase, cached_get_profile, cached_unread_count, clear_data_cache
    from utils.verification import check_verification_status
    from utils.shared_ui import render_profile_editor_modal
except ImportError as e:
    st.error(f"⚠️ Import Error: {e}")
    st.stop()

# ═════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ═════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
def initialize_session_state():
    """Initialize all session state variables"""
    # User session
    default_keys = {
        'user': None,
        'profile': None,
        'authenticated': False,
        'user_role': None,
        'user_email': None
    }
    
    # UI state
    default_ui_keys = {
        'theme_mode': 'dark',
        'show_profile_editor': False,
        'sidebar_light_mode': False,
        'auth_redirect': False,
        'nav_clicked': False,
        'page': 'main'
    }
    
    # Initialize all keys from constants
    if 'SESSION_KEYS' in globals():
        for _k in SESSION_KEYS:
            if _k not in st.session_state:
                st.session_state[_k] = None
    
    # Initialize UI keys
    for key, default_value in default_ui_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Initialize user keys
    for key, default_value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Call initialization
initialize_session_state()

# Inject theme
inject_theme()

# ═════════════════════════════════════════════════════════════
# SIDEBAR RENDERER
# ═════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Theme toggle at top
        render_theme_toggle()
        st.divider()
        
        if st.session_state.get("user") is None:
            st.info("👈 Use the main page to Log In or Sign Up")
            return None, None
        else:
            st.title("🌾 AI Supply Chain")
            st.caption("Ethiopian Multi-Sector Commerce")
            st.divider()
            
            # Get profile
            profile = st.session_state.get("profile")
            if profile is None:
                try:
                    profile = cached_get_profile(st.session_state.user.id)
                    if profile:
                        st.session_state.profile = profile
                except Exception as e:
                    logger.error(f"Profile fetch error: {e}")
            
            # Try to create profile if it doesn't exist
            if profile is None:
                try:
                    default_name = st.session_state.user.email.split('@')[0] if st.session_state.user.email else "User"
                    supabase.table("profiles").insert({
                        "id": st.session_state.user.id,
                        "full_name": default_name,
                        "role": "customer",
                        "is_verified": False,
                        "documents_uploaded": False
                    }).execute()
                    profile = cached_get_profile(st.session_state.user.id)
                    if profile:
                        st.session_state.profile = profile
                except Exception as e:
                    logger.error(f"Profile creation error: {e}")
                    st.error(f"⚠️ Profile creation failed: {str(e)}")
                    if st.button("Sign Out", key="sb_logout_error_btn"):
                        sign_out()
                        st.rerun()
                    st.stop()
            
            if profile is None:
                st.warning("⚠️ Could not load profile. Please sign out and try again.")
                if st.button("Sign Out", key="sb_logout_profile_error"):
                    sign_out()
                    st.rerun()
                return None, None
            
            role = profile.get("role", "customer")
            st.session_state.user_role = role
            
            # Profile picture section
            profile_pic = profile.get("profile_image")
            if profile_pic:
                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/jpeg;base64,{profile_pic}" 
                         style="width: 90px; height: 90px; border-radius: 50%; border: 3px solid #D4A017; object-fit: cover;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; margin: 20px 0;">
                    <div style="width: 90px; height: 90px; border-radius: 50%; border: 3px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 36px; color: #f1f5f9; font-weight: 700;">
                        {profile.get("full_name", "U")[0].upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Edit button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✏️ Edit Profile", key="edit_profile_btn_sidebar", use_container_width=True):
                    st.session_state.show_profile_editor = True
                    st.rerun()
            
            # Show name
            st.markdown(f"""
            <div style="text-align: center; margin: 15px 0;">
                <div style="font-size: 22px; font-weight: 700; color: #f1f5f9;">{profile.get('full_name', 'User')}</div>
                <div style="font-size: 13px; color: #64748b; margin-top: 6px;">{role.capitalize() if role else 'N/A'}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.caption(f'📍 {profile.get("region", "N/A")}')
            
            # Verification status
            try:
                verif_status = check_verification_status(st.session_state.user.id)
                if verif_status and not verif_status.get("is_verified", False):
                    if verif_status.get("has_documents", False):
                        st.info("⏳ Documents pending verification")
                    else:
                        st.warning("⚠️ Upload documents to verify")
            except Exception as e:
                logger.error(f"Verification check error: {e}")
                st.caption("⚠️ Verification check failed")
            
            # Notifications
            try:
                unread = cached_unread_count(st.session_state.user.id)
                if unread and unread > 0:
                    st.info(f"🔔 {unread} unread notification(s)")
            except Exception as e:
                logger.error(f"Notification count error: {e}")
            
            st.divider()
            
            # Quick navigation links
            nav_mapping = {
                "producer": ("🚜 Producer Dashboard", "1_producer.py"),
                "merchant": ("🏬 Merchant Dashboard", "2_merchant.py"),
                "customer": ("🛒 Customer Dashboard", "3_customer.py"),
                "admin": ("🛡️ Admin Dashboard", "4_Admin.py")
            }
            
            if role in nav_mapping:
                label, page = nav_mapping[role]
                st.markdown("**Quick Links**")
                if st.button(label, key=f"nav_{role}", use_container_width=True):
                    try:
                        st.switch_page(page)
                    except Exception as e:
                        logger.error(f"Navigation error: {e}")
                        st.warning(f"⚠️ Page '{page}' not found. Please check if the file exists.")
            
            st.divider()
            
            if st.button("🚪 Log Out", use_container_width=True, key="sb_logout_btn"):
                try:
                    sign_out()
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.session_state.profile = None
                    st.rerun()
                except Exception as e:
                    logger.error(f"Logout error: {e}")
                    st.error(f"Logout error: {str(e)}")
            
            return profile, role

# ═════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════
def show_landing():
    try:
        _n_products = supabase.table("products").select("", count="exact").eq("is_available", True).execute().count or 0
    except Exception:
        _n_products = 0
    
    try:
        _n_users = supabase.table("profiles").select("", count="exact").execute().count or 0
    except Exception:
        _n_users = 0
    
    _n_sectors = len(SECTORS) if 'SECTORS' in globals() else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 55%, #40916C 100%); border-radius: 20px; padding: 52px 48px 44px; margin-bottom: 36px; color: white;">
        <p style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#F4C430;margin-bottom:14px;">🌍 Wolaita Sodo University · Department of ECE</p>
        <h1 style="font-size: clamp(28px, 4vw, 46px); font-weight: 800; margin: 0 0 16px; color: white;">Ethiopian <span style="color: #F4C430;">AI Supply Chain</span><br>Platform</h1>
        <p style="font-size: 15px; color: rgba(255,255,255,0.82); line-height: 1.7; max-width: 560px; margin: 0 0 28px;">Connecting smallholder farmers, processing hubs, and consumers through machine-learning–powered matching, real-time price intelligence, and fraud-resistant trade agreements.</p>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <span style="background: #D4A017; border: 1px solid #F4C430; color: #1B4332; font-weight: 700; padding: 5px 14px; border-radius: 20px; font-size: 12px;">🤖 AI Price Engine</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">🤝 Smart Matchmaking</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">🛡️ Fraud Detection</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">📈 Demand Forecasting</span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 32px;">
        <div style="background: #fff; border: 1px solid #e8ede9; border-radius: 14px; padding: 22px 20px; text-align: center;">
            <span style="font-size: 28px; font-weight: 800; color: #1B4332; display: block;">{_n_products}</span>
            <span style="font-size: 12px; color: #6b7c6e; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; display: block;">Active Listings</span>
        </div>
        <div style="background: #fff; border: 1px solid #e8ede9; border-radius: 14px; padding: 22px 20px; text-align: center;">
            <span style="font-size: 28px; font-weight: 800; color: #1B4332; display: block;">{_n_users}</span>
            <span style="font-size: 12px; color: #6b7c6e; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; display: block;">Registered Users</span>
        </div>
        <div style="background: #fff; border: 1px solid #e8ede9; border-radius: 14px; padding: 22px 20px; text-align: center;">
            <span style="font-size: 28px; font-weight: 800; color: #1B4332; display: block;">{_n_sectors}</span>
            <span style="font-size: 12px; color: #6b7c6e; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; display: block;">Trade Sectors</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="background: #fff; border: 1px solid #dde8de; border-radius: 20px; padding: 32px 30px 28px; box-shadow: 0 4px 24px rgba(27,67,50,0.08); margin-top: 20px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 20px; font-weight: 700; color: #1B4332; margin-bottom: 4px;">Access Your Account</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: #7a8c7c; margin-bottom: 24px;">Sign in to your dashboard or register a new entity below.</div>', unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Register"])
    
    with tab_login:
        email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
        if st.button("Sign In →", use_container_width=True, type="primary", key="login_btn"):
            if not email or not password:
                st.warning("Please enter your email and password.")
            else:
                with st.spinner("Authenticating…"):
                    ok, msg = sign_in(email, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.auth_redirect = True
                    st.rerun()
                else:
                    st.error(msg)
        
        st.divider()
        with st.expander("🔑 Forgot Password?"):
            reset_email = st.text_input("Enter your registered email", key="reset_email", placeholder="you@example.com")
            if st.button("📧 Send Reset Link", key="reset_btn", use_container_width=True):
                if not reset_email:
                    st.warning("Please enter your email address.")
                else:
                    with st.spinner("Sending reset email…"):
                        ok, msg = forgot_password(reset_email)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
    
    with tab_register:
        reg_name = st.text_input("Full Name", key="reg_name", placeholder="Abebe Girma")
        reg_email = st.text_input("Email Address", key="reg_email", placeholder="abebe@example.com")
        reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min. 8 characters")
        col_r, col_reg = st.columns(2)
        with col_r:
            reg_role = st.selectbox("I am a…", ["producer", "merchant", "customer"], key="reg_role")
        with col_reg:
            reg_region = st.selectbox("Region", REGIONS if 'REGIONS' in globals() else ["Addis Ababa"], key="reg_region")
        reg_phone = st.text_input("Phone (optional)", key="reg_phone", placeholder="+251 9xx xxx xxx")
        
        if st.button("Create Account →", use_container_width=True, type="primary", key="reg_btn"):
            if not all([reg_name, reg_email, reg_password]):
                st.warning("Name, email, and password are required.")
            else:
                with st.spinner("Creating your account…"):
                    ok, msg = sign_up(reg_email, reg_password, reg_name, reg_role, reg_region, reg_phone)
                if ok:
                    st.success(msg)
                    st.info("Account created — please go to Sign In to continue.")
                else:
                    st.error(msg)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 11px; color: #9aab9c; padding: 24px 0 8px;">Ethiopian AI Supply Chain Platform · Wolaita Sodo University, Dept. of ECE</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════
# MAIN ROUTER
# ═════════════════════════════════════════════════════════════
def main():
    """Main application entry point"""
    
    # Render sidebar
    profile, role = render_sidebar()
    
    # Profile editor modal
    if st.session_state.get("show_profile_editor") and profile:
        st.markdown("""
        <style>
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        @media (max-width: 768px) {
            .modal-overlay {
                padding: 10px;
                align-items: flex-start;
                padding-top: 40px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="modal-overlay">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            render_profile_editor_modal(profile, st.session_state.user.id)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # Auto-redirect after login
    if st.session_state.get("authenticated") and st.session_state.get("auth_redirect"):
        st.session_state.auth_redirect = False
        
        # Get profile if not already loaded
        if profile is None and st.session_state.get("user"):
            try:
                profile = cached_get_profile(st.session_state.user.id)
                if profile:
                    st.session_state.profile = profile
            except Exception as e:
                logger.error(f"Profile fetch for redirect error: {e}")
        
        if profile:
            role = profile.get("role")
            page_mapping = {
                "producer": "1_producer.py",
                "merchant": "2_merchant.py",
                "customer": "3_customer.py",
                "admin": "4_Admin.py"
            }
            
            if role in page_mapping:
                try:
                    st.switch_page(page_mapping[role])
                except Exception as e:
                    logger.error(f"Switch page error: {e}")
                    # Stay on main page if navigation fails
                    st.session_state.auth_redirect = False
    
    # Show landing or dashboard
    if st.session_state.get("user") is None or not st.session_state.get("authenticated"):
        show_landing()
    else:
        if profile is None:
            st.error("Could not load profile. Please sign out and try again.")
            if st.button("Sign Out", key="main_signout_error"):
                try:
                    sign_out()
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.session_state.profile = None
                    st.rerun()
                except Exception as e:
                    logger.error(f"Signout error: {e}")
        else:
            role_emoji = {
                "producer": "🚜", 
                "merchant": "🏬", 
                "customer": "🛒", 
                "admin": "🛡️"
            }.get(role, "👤")
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                        border-radius: 16px; padding: 40px; color: white; text-align: center;">
                <div style="font-size: 64px; margin-bottom: 16px;">{role_emoji}</div>
                <h1 style="color: white; margin: 0;">Welcome to Your Dashboard</h1>
                <p style="opacity: 0.9; margin-top: 12px; font-size: 16px;">
                    👈 Use the sidebar navigation to go to your dashboard.
                </p>
            </div>
            """, unsafe_allow_html=True)

# Run main app
if __name__ == "__main__":
    main()
