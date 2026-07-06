"""
app.py — Ethiopian AI Supply Chain Platform (Main Entry)
Handles: Landing page, Authentication, Routing
"""
import sys
import os
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from utils.theme import inject_theme, render_page_header
from utils.auth import sign_in, sign_up, sign_out, forgot_password
from utils.constants import REGIONS, SECTORS, SESSION_KEYS
from utils.db_helpers import get_supabase_client, cached_get_profile, cached_unread_count, clear_data_cache
from utils.verification import check_verification_status

# ═════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Supply Chain Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session keys
for _k in SESSION_KEYS:
    if _k not in st.session_state:
        st.session_state[_k] = None

# Initialize Supabase
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(str(e))
    st.stop()

# Inject theme
inject_theme()


# ═════════════════════════════════════════════════════════════
# SIDEBAR — Always visible
# ═════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        if st.session_state.get("user") is None:
            st.info("👈 Please sign in or register")
            return None, None
        else:
            st.title("🌾 AI Supply Chain")
            st.caption("Ethiopian Multi-Sector Commerce")
            st.divider()
            profile = st.session_state.get("profile") or cached_get_profile(st.session_state.user.id)
            st.session_state.profile = profile
            role = profile.get("role") if profile else None
            st.success(f"Welcome, {profile.get('full_name', 'User')}")
            st.caption(f'Role: {role.capitalize() if role else "N/A"}')
            st.caption(f'Region: {profile.get("region", "N/A")}')
            try:
                verif_status = check_verification_status(st.session_state.user.id)
                if not verif_status["is_verified"]:
                    if verif_status["has_documents"]:
                        st.info("⏳ Documents pending verification")
                    else:
                        st.warning("⚠️ Upload documents to verify")
            except Exception:
                pass
            unread = cached_unread_count(st.session_state.user.id)
            if unread:
                st.info(f"🔔 {unread} unread notification(s)")
            if st.button("🚪 Log Out", use_container_width=True, key="sb_logout_btn"):
                sign_out()
                st.rerun()
            return profile, role


# ═════════════════════════════════════════════════════════════
# LANDING PAGE (shown when not logged in)
# ═════════════════════════════════════════════════════════════
def show_landing():
    try:
        _n_products = supabase.table("products").select("", count="exact").eq("is_available", True).execute().count or 0
        _n_users = supabase.table("profiles").select("", count="exact").execute().count or 0
        _n_sectors = len(SECTORS)
    except Exception:
        _n_products, _n_users, _n_sectors = 0, 0, len(SECTORS)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 55%, #40916C 100%); border-radius: 20px; padding: 52px 48px 44px; margin-bottom: 36px; color: white;">
        <p style="font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#F4C430;margin-bottom:14px;">🌍 Wolaita Sodo University · Department of ECE</p>
        <h1 style="font-size: clamp(28px, 4vw, 46px); font-weight: 800; margin: 0 0 16px; color: white;">Ethiopian <span style="color: #F4C430;">AI Supply Chain</span><br>Platform</h1>
        <p style="font-size: 15px; color: rgba(255,255,255,0.82); line-height: 1.7; max-width: 560px; margin: 0 0 28px;">Connecting smallholder farmers, processing hubs, and consumers through machine-learning–powered matching, real-time price intelligence, and fraud-resistant trade agreements.</p>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <span style="background: #D4A017; border: 1px solid #F4C430; color: #1B4332; font-weight: 700; padding: 5px 14px; border-radius: 20px; font-size: 12px;">⚡ AI Price Engine</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">🤝 Smart Matchmaking</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">🛡️ Fraud Detection</span>
            <span style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22); color: #fff; padding: 5px 14px; border-radius: 20px; font-size: 12px;">📈 Demand Forecasting</span>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 32px;">
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
            reg_region = st.selectbox("Region", REGIONS, key="reg_region")
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
profile, role = render_sidebar()

if st.session_state.get("user") is None:
    show_landing()
else:
    # User is logged in — redirect to their dashboard page
    st.info("👈 Use the sidebar to navigate to your dashboard.")
    if profile is None:
        st.error("Could not load profile. Please sign out and try again.")
        if st.button("Sign Out"):
            sign_out()
            st.rerun()
    else:
        role_emoji = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(role, "👤")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
                    border-radius: 16px; padding: 40px; color: white; text-align: center;">
            <div style="font-size: 64px; margin-bottom: 16px;">{role_emoji}</div>
            <h1 style="color: white; margin: 0;">Welcome to Your Dashboard</h1>
            <p style="opacity: 0.9; margin-top: 12px; font-size: 16px;">
                Click on your dashboard in the sidebar to get started.
            </p>
        </div>
        """, unsafe_allow_html=True)
