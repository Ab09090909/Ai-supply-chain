"""Producer Dashboard — Professional dark design with Hamburger Menu."""
import sys
import os
import base64
import datetime
import logging
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
try:
    from utils.theme import inject_theme, render_theme_toggle
    from utils.constants import REGIONS, SECTORS, UNITS
    from utils.db_helpers import supabase, cached_query, clear_data_cache, send_notification
    from utils.verification import check_verification_status, render_document_upload
    from utils.shared_ui import (
        get_grades_for_product, map_grade_to_db, render_browse_tab,
        render_notifications_tab, render_profile_editor_modal,
    )
    from utils.pdf_generator import (
        generate_agreement_pdf,
        generate_agreement_preview_html,
        build_agreement_payload,
    )
    from src.matching_engine import rank_merchants
    from src.price_engine import recommend_price
    from src.demand_engine import forecast_demand
except ImportError as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Producer Dashboard",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "initialized_producer" not in st.session_state:
    st.session_state.initialized_producer = True
    st.session_state.match_results = None
    st.session_state.match_product = None
    st.session_state.forecast_result = None
    st.session_state.forecast_params = None
    st.session_state.mobile_menu_open = False

# ─────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────
inject_theme()

# ─────────────────────────────────────────────
# CSS - HIDE SIDEBAR, SHOW HAMBURGER MENU
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ─── HIDE DEFAULT STREAMLIT SIDEBAR ─── */
[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="stSidebarContent"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ─── HIDE STREAMLIT BRANDING ─── */
#MainMenu, footer, header {
    visibility: hidden !important;
}
[data-testid="stToolbar"] {
    display: none !important;
}

/* ─── HAMBURGER MENU BUTTON ─── */
.hamburger-btn {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 999997;
    background: #1B4332;
    color: white;
    border: 2px solid #2D6A4F;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.hamburger-btn:hover {
    background: #2D6A4F;
}

/* ─── SIDEBAR OVERLAY ─── */
.mobile-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: 999998;
}
.mobile-overlay.active {
    display: block;
}

/* ─── CUSTOM SIDEBAR ─── */
.mobile-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 280px;
    height: 100%;
    background: #161b27;
    z-index: 999999;
    padding: 20px;
    overflow-y: auto;
    border-right: 1px solid #1e2a3a;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
.mobile-sidebar.open {
    transform: translateX(0);
}

/* ─── CLOSE BUTTON ─── */
.close-sidebar-btn {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-size: 24px;
    cursor: pointer;
    float: right;
    padding: 5px 10px;
}
.close-sidebar-btn:hover {
    color: #f87171;
}

/* ─── SIDEBAR PROFILE ─── */
.sidebar-profile {
    text-align: center;
    margin: 10px 0 20px 0;
}
.sidebar-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #1e2a3a;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
    font-size: 24px;
    color: #f1f5f9;
    font-weight: 700;
    border: 2px solid #D4A017;
}
.sidebar-name {
    font-size: 16px;
    font-weight: 600;
    margin-top: 8px;
    color: #e2e8f0;
}
.sidebar-role {
    font-size: 12px;
    color: #94a3b8;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid #1e2a3a;
    margin: 12px 0;
}

/* ─── SIDEBAR NAVIGATION BUTTONS ─── */
.sidebar-nav-btn {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 4px;
    background: #1e2a3a;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
}
.sidebar-nav-btn:hover {
    border-color: #D4A017;
    color: #D4A017;
}

.sidebar-nav-btn-logout {
    width: 100%;
    padding: 10px 14px;
    margin-bottom: 4px;
    background: #7f1d1d44;
    border: 1px solid #ef444455;
    border-radius: 8px;
    color: #f87171;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s;
}
.sidebar-nav-btn-logout:hover {
    background: #7f1d1d66;
    border-color: #ef4444;
}

.sidebar-section-title {
    font-weight: 600;
    color: #94a3b8;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    margin-top: 12px;
}

/* ─── PILL STYLES ─── */
.pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
    margin: 2px 0;
}
.pill-success { background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }
.pill-warning { background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }
.pill-danger { background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }
.pill-info { background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

/* ─── MAIN CONTENT ─── */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 70px !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 70px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    [data-testid="stTabs"] > div > div > div > button {
        font-size: 12px !important;
        padding: 6px 10px !important;
        white-space: nowrap !important;
    }
    [data-testid="stTabs"] > div > div {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }
    div.stButton > button {
        width: 100% !important;
    }
}

@media (min-width: 769px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 80px !important;
        padding-left: 24px !important;
        padding-right: 24px !important;
    }
}

/* ─── BUTTONS ─── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    background: #1e2a3a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    border-color: #D4A01755 !important;
    color: #D4A017 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #D4A017 0%, #F4C430 100%) !important;
    border-color: #D4A017 !important;
    color: #1B4332 !important;
}

/* ─── INPUTS ─── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #1e2a3a !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* ─── TABS ─── */
[data-testid="stTabs"] > div > div > div > button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #D4A017 !important;
    border-bottom: 2px solid #D4A017 !important;
}

/* ─── KPI CARDS ─── */
.kpi-card {
    background: #161b27 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 10px;
    padding: 16px 20px;
    height: 100%;
}
.kpi-label { font-size: 11px; font-weight: 600; color: #475569 !important; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #f1f5f9 !important; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.kpi-sub { font-size: 12px; color: #64748b !important; margin-top: 6px; }

/* ─── ALERT BOXES ─── */
.alert-box { border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-danger { background: #7f1d1d22; border-color: #ef444466; color: #f87171; }
.alert-info { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }
.alert-success { background: #14532d22; border-color: #16a34a66; color: #4ade80; }

/* ─── SECTION TITLE ─── */
.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 20px 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2a3a;
}

/* ─── PRICE TAG ─── */
.price-tag { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: #D4A017 !important; }

/* ─── CONFIRM BOX ─── */
.confirm-box { background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }

/* ─── MATCH BAR ─── */
.match-bar-bg { background: #1e2a3a; border-radius: 4px; height: 6px; margin-top: 6px; overflow: hidden; }
.match-bar-fill { height: 100%; border-radius: 4px; transition: width 0.4s ease; }

/* ─── RECORD CARDS ─── */
.record-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}
.record-card:hover { border-color: #D4A01755; }

/* ─── FORECAST CONTAINER ─── */
.forecast-container {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU BUTTON
# ─────────────────────────────────────────────────────────────
def render_hamburger_button():
    """Render the hamburger menu button."""
    st.markdown('''
    <button class="hamburger-btn" onclick="
        var sidebar = document.getElementById('mobileSidebar');
        var overlay = document.getElementById('mobileOverlay');
        if (sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        } else {
            sidebar.classList.add('open');
            overlay.classList.add('active');
        }
    ">☰</button>
    <div class="mobile-overlay" id="mobileOverlay" onclick="
        document.getElementById('mobileSidebar').classList.remove('open');
        this.classList.remove('active');
    "></div>
    ''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CUSTOM SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_custom_sidebar(profile, user_id, role):
    """Render custom sidebar with hamburger menu."""
    
    if not profile:
        sidebar_html = '''
        <div class="mobile-sidebar" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="document.getElementById('mobileSidebar').classList.remove('open'); document.getElementById('mobileOverlay').classList.remove('active');">✕</button>
            <div class="sidebar-profile">
                <div class="sidebar-avatar">🔐</div>
                <div class="sidebar-name">Not Signed In</div>
                <div class="sidebar-role">Please sign in</div>
            </div>
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        </div>
        '''
        st.markdown(sidebar_html, unsafe_allow_html=True)
        return
    
    name = profile.get("full_name", "User")
    region = profile.get("region", "N/A")
    role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(role, "👤")
    
    sidebar_html = f'''
    <div class="mobile-sidebar" id="mobileSidebar">
        <button class="close-sidebar-btn" onclick="document.getElementById('mobileSidebar').classList.remove('open'); document.getElementById('mobileOverlay').classList.remove('active');">✕</button>
        
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{name[0].upper()}</div>
            <div class="sidebar-name">{name}</div>
            <div class="sidebar-role">{role_icon} {role.capitalize()} · {region}</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📊 Navigation</div>
        <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
    '''
    
    # Role-specific pages
    nav_pages = {
        "producer": ("🚜 Producer", "pages/1_producer.py"),
        "merchant": ("🏬 Merchant", "pages/2_merchant.py"),
        "customer": ("🛒 Customer", "pages/3_customer.py"),
        "admin": ("🛡️ Admin", "pages/4_Admin.py")
    }
    
    if role in nav_pages:
        label, page = nav_pages[role]
        sidebar_html += f'<button class="sidebar-nav-btn" onclick="window.location.href=\'{page}\'">{label}</button>'
    
    sidebar_html += f'''
        <hr class="sidebar-divider">
        <div class="sidebar-section-title">📌 Status</div>
    '''
    
    # Verification status
    try:
        verif_status = check_verification_status(user_id)
        if verif_status.get("is_verified", False):
            sidebar_html += '<div style="margin-bottom: 8px;"><span class="pill pill-success">✅ Verified</span></div>'
        elif verif_status.get("has_documents", False):
            sidebar_html += '<div style="margin-bottom: 8px;"><span class="pill pill-warning">⏳ Pending</span></div>'
        else:
            sidebar_html += '<div style="margin-bottom: 8px;"><span class="pill pill-info">📄 Verify</span></div>'
    except Exception:
        sidebar_html += '<div style="margin-bottom: 8px;"><span class="pill pill-neutral">⚠️ Unknown</span></div>'
    
    sidebar_html += f'''
        <hr class="sidebar-divider">
        <button class="sidebar-nav-btn-logout" onclick="document.getElementById('logoutForm').submit();">🚪 Log Out</button>
    </div>
    '''
    
    st.markdown(sidebar_html, unsafe_allow_html=True)
    
    # Logout form
    st.markdown('''
    <form id="logoutForm" method="post" action="">
        <input type="hidden" name="logout" value="true">
    </form>
    ''', unsafe_allow_html=True)
    
    if st.query_params.get("logout") == "true":
        try:
            from utils.auth import sign_out
            sign_out()
            st.session_state.user = None
            st.session_state.profile = None
            st.session_state.authenticated = False
            st.session_state.user_role = None
            clear_data_cache()
            st.query_params.clear()
            st.rerun()
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────────────────────
def check_auth():
    if st.session_state.get("user") is None:
        st.warning("⚠️ Please sign in first.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
        return False
    
    profile = st.session_state.get("profile")
    if profile is None or profile.get("role") != "producer":
        st.error("🚫 Access denied. This page is for producers only.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
        return False
    
    return True

if not check_auth():
    st.stop()

# ─────────────────────────────────────────────────────────────
# GET USER DATA
# ─────────────────────────────────────────────────────────────
profile = st.session_state.get("profile", {})
user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

# ─────────────────────────────────────────────────────────────
# RENDER HAMBURGER AND SIDEBAR
# ─────────────────────────────────────────────────────────────
render_hamburger_button()
render_custom_sidebar(profile, user_id, "producer")

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
verif_badge = '<span class="pill pill-success">✓ Verified</span>' if verif_status["is_verified"] else '<span class="pill pill-warning">⏳ Pending</span>'

profile_pic = profile.get("profile_image")
if profile_pic:
    profile_pic_html = f'<img src="data:image/jpeg;base64,{profile_pic}" style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #D4A017; object-fit: cover;">'
else:
    profile_pic_html = f'<div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; font-size: 24px; color: #f1f5f9; font-weight: 700;">{profile.get("full_name", "U")[0].upper()}</div>'

st.markdown(f"""
<div style="background: linear-gradient(135deg, #0d2b1e 0%, #0f1117 60%, #122010 100%);
            border: 1px solid #1a3d2b; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px;
            display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
    <div style="flex-shrink: 0; position: relative; width: 60px; height: 60px;">
        {profile_pic_html}
    </div>
    <div style="flex: 1;">
        <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #f1f5f9;">🚜 Producer Dashboard</h1>
        <p style="margin: 4px 0 0; font-size: 13px; color: #64748b;">
            Welcome back, <strong>{profile.get('full_name', 'Producer')}</strong> · 📍 {profile.get('region', 'N/A')} · {now_str}
        </p>
    </div>
    <div>{verif_badge}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# VERIFICATION GATE
# ─────────────────────────────────────────────────────────────
if not verif_status.get("is_verified", False):
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "producer")
    with tab_browse:
        st.markdown('<div class="alert-box alert-warning">⏳ Full access unlocks after account verification.</div>', unsafe_allow_html=True)
        render_browse_tab("producer", profile)
    st.stop()

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
(tab_overview, tab_products, tab_demand, tab_incoming,
 tab_match, tab_agree, tab_history, tab_notif, tab_profile) = st.tabs([
    "📊 Overview", "📦 My Products", "📈 Demand Forecast",
    "📬 Incoming Orders", "🤝 AI Matching", "📄 Agreements",
    "📜 History", "🔔 Notifications", "👤 Profile",
])

# ══════════════════════════════════════════════
# TAB — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:
    try:
        my_products_all = cached_query("products", filters={"producer_id": user_id}, limit=500)
        
        try:
            product_ids = [p["id"] for p in my_products_all]
            if product_ids:
                orders_response = supabase.table("orders").select(
                    "*, products!inner(producer_id)"
                ).in_("product_id", product_ids).execute()
                my_orders_all = orders_response.data if orders_response else []
            else:
                my_orders_all = []
        except Exception:
            my_orders_all = []
        
        total_val = sum(p.get("price_birr", 0) * p.get("quantity", 0) for p in my_products_all)
        active_prods = sum(1 for p in my_products_all if p.get("is_available", False))
        pending_orders_cnt = sum(1 for o in my_orders_all if o.get("status") == "pending")
        delivered_orders = [o for o in my_orders_all if o.get("status") == "delivered"]
        total_revenue = sum(float(o.get("total_price_birr") or 0) for o in delivered_orders)
        
        if pending_orders_cnt > 0:
            st.markdown(f'<div class="alert-box alert-warning">📬 You have <strong>{pending_orders_cnt} pending order(s)</strong> awaiting your confirmation.</div>', unsafe_allow_html=True)
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Products Listed</div><div class="kpi-value">{len(my_products_all)}</div><div class="kpi-sub">{active_prods} active</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Inventory Value</div><div class="kpi-value">{total_val:,.0f}</div><div class="kpi-sub">Birr estimated</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Pending Orders</div><div class="kpi-value">{pending_orders_cnt}</div><div class="kpi-sub">Awaiting confirmation</div></div>', unsafe_allow_html=True)
        with k4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Revenue</div><div class="kpi-value">{total_revenue:,.0f}</div><div class="kpi-sub">Birr delivered</div></div>', unsafe_allow_html=True)
        
        if my_products_all:
            st.markdown('<div class="section-title">Products by Sector</div>', unsafe_allow_html=True)
            sector_counts = {}
            for p in my_products_all:
                s = p.get("sector", "Other")
                sector_counts[s] = sector_counts.get(s, 0) + 1
            df_sector = pd.DataFrame({"Sector": list(sector_counts.keys()), "Count": list(sector_counts.values())})
            st.bar_chart(df_sector.set_index("Sector"), height=200, color="#D4A017")
    except Exception as e:
        st.error(f"⚠️ Error loading overview: {str(e)}")

# ─── PRODUCTS TAB ───
with tab_products:
    try:
        st.markdown('<div class="section-title">Product Listings</div>', unsafe_allow_html=True)
        my_products = cached_query("products", filters={"producer_id": user_id}, limit=200)
        
        if my_products:
            total_val2 = sum(p.get("price_birr", 0) * p.get("quantity", 0) for p in my_products)
            active2 = sum(1 for p in my_products if p.get("is_available", False))
            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Listed</div><div class="kpi-value">{len(my_products)}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Active</div><div class="kpi-value">{active2}</div></div>', unsafe_allow_html=True)
            with k3:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Inventory Value</div><div class="kpi-value">{total_val2:,.0f}</div><div class="kpi-sub">Birr</div></div>', unsafe_allow_html=True)
            st.markdown("")
        
        with st.expander("➕ Add New Product", expanded=not bool(my_products)):
            with st.form("add_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Product Name *", placeholder="e.g. Teff, Coffee Beans")
                    new_sector = st.selectbox("Sector *", SECTORS)
                    available_grades = get_grades_for_product(new_sector, new_name) if new_sector else ["A", "B", "C"]
                    new_grade_ui = st.selectbox("Quality Grade *", available_grades)
                    new_grade_db = map_grade_to_db(new_grade_ui)
                    new_region = st.selectbox("Region *", REGIONS, index=REGIONS.index(profile.get("region", REGIONS[0])) if profile.get("region") in REGIONS else 0)
                with c2:
                    new_qty = st.number_input("Quantity *", min_value=0.1, value=1.0, step=0.5)
                    new_unit = st.selectbox("Unit *", UNITS)
                    use_ai_price = st.checkbox("🤖 Auto-suggest price using AI", value=False)
                    new_price = st.number_input("Price (Birr) *", min_value=1.0, value=100.0, step=10.0)
                    new_avail = st.checkbox("List as Available", value=True)
                new_image = st.file_uploader("📷 Product Image (Recommended)", type=["jpg", "jpeg", "png"], key="prod_img_upload")
                new_image_b64 = None
                if new_image:
                    try:
                        new_image_b64 = base64.b64encode(new_image.read()).decode("utf-8")
                    except Exception:
                        st.warning("Could not process image.")
                new_desc = st.text_area("Description (optional)", height=80, placeholder="Describe quality, harvest details, storage…")
                submitted = st.form_submit_button("✅ Add Product", type="primary", use_container_width=True)
                if submitted:
                    if not new_name.strip():
                        st.error("Product name is required.")
                    else:
                        try:
                            final_price = new_price
                            if use_ai_price:
                                with st.spinner("🤖 Analyzing market data..."):
                                    try:
                                        ai_result = recommend_price(
                                            sector=new_sector,
                                            product=new_name,
                                            region=new_region,
                                            quality_grade=new_grade_db,
                                            quantity=new_qty
                                        )
                                        final_price = ai_result.get("recommended_price_birr", new_price)
                                        st.success(f"💡 AI Recommended Price: {final_price:,.0f} Birr/{new_unit}")
                                    except Exception as e:
                                        st.warning(f"AI price suggestion failed: {e}")
                            data = {
                                "producer_id": user_id,
                                "product_name": new_name.strip(),
                                "sector": new_sector,
                                "quality_grade": new_grade_db,
                                "region": new_region,
                                "quantity": new_qty,
                                "unit": new_unit,
                                "price_birr": final_price,
                                "is_available": new_avail,
                                "description": f"[{new_grade_ui}] {new_desc.strip()}" if new_desc.strip() else f"[{new_grade_ui}]",
                            }
                            if new_image_b64:
                                data["image_base64"] = new_image_b64
                            supabase.table("products").insert(data).execute()
                            clear_data_cache()
                            st.success(f"✅ '{new_name}' listed successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add product: {e}")
        
        if my_products:
            pf1, pf2 = st.columns(2)
            with pf1:
                prod_search = st.text_input("🔍 Search products", key="prod_search_inp", placeholder="Product name…")
            with pf2:
                avail_filter = st.selectbox("Availability", ["All", "Available", "Unavailable"], key="prod_avail_filter")
            filtered = my_products
            if prod_search:
                filtered = [p for p in filtered if prod_search.lower() in p.get("product_name", "").lower()]
            if avail_filter == "Available":
                filtered = [p for p in filtered if p.get("is_available", False)]
            elif avail_filter == "Unavailable":
                filtered = [p for p in filtered if not p.get("is_available", False)]
            st.caption(f"**{len(filtered)} product(s)**")
            for p in filtered:
                pid = p["id"]
                avail = p.get("is_available", False)
                status_pill = '<span class="pill pill-success">● Available</span>' if avail else '<span class="pill pill-danger">● Unavailable</span>'
                with st.container(border=True):
                    img_col, info_col = st.columns([1, 4])
                    with img_col:
                        img_b64 = p.get("image_base64")
                        if img_b64:
                            try:
                                img_b64_clean = img_b64.replace('\n', '').replace('\r', '').replace(' ', '')
                                st.image(f"data:image/jpeg;base64,{img_b64_clean}", width=120)
                            except Exception:
                                st.markdown('<div style="background:#1e2a3a;border-radius:8px;height:100px;display:flex;align-items:center;justify-content:center;border:1px dashed #334155;color:#64748b;font-size:11px;">📷 Error</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="background:#1e2a3a;border-radius:8px;height:100px;display:flex;align-items:center;justify-content:center;border:1px dashed #334155;color:#64748b;">📷 No Image</div>', unsafe_allow_html=True)
                    with info_col:
                        col1, col2, col3 = st.columns([5, 2, 3])
                        with col1:
                            st.markdown(f"**📦 {p['product_name']}** &nbsp; {status_pill}", unsafe_allow_html=True)
                            st.caption(f"Sector: {p.get('sector', '—')} · Grade: **{p.get('quality_grade', '—')}** · 📍 {p.get('region', '—')}")
                            st.caption(f"Stock: {p.get('quantity', '—')} {p.get('unit', '')} · Listed: {p.get('created_at', '')[:10]}")
                        with col2:
                            st.markdown(f'<div class="price-tag">{p.get("price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr / {p.get("unit", "")}</div>', unsafe_allow_html=True)
                        with col3:
                            if st.button("🗑️ Delete", key=f"del_prod_{pid}", use_container_width=True):
                                st.session_state[f"confirm_del_prod_{pid}"] = True
                                st.rerun()
                            if st.session_state.get(f"confirm_del_prod_{pid}"):
                                st.markdown('<div class="confirm-box">⚠️ Delete permanently?</div>', unsafe_allow_html=True)
                                if st.button("✅ Yes, Delete", key=f"do_del_prod_{pid}", use_container_width=True):
                                    try:
                                        supabase.table("products").delete().eq("id", pid).execute()
                                        clear_data_cache()
                                        st.session_state.pop(f"confirm_del_prod_{pid}", None)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Delete failed: {e}")
                                if st.button("Cancel", key=f"cancel_del_prod_{pid}", use_container_width=True):
                                    st.session_state.pop(f"confirm_del_prod_{pid}", None)
                                    st.rerun()
    except Exception as e:
        st.error(f"⚠️ Error loading products: {str(e)}")

# ─── DEMAND FORECAST TAB ───
with tab_demand:
    try:
        st.markdown('<div class="section-title">AI Demand Forecasting</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-box alert-info">🤖 The AI model analyzes historical patterns and market signals to forecast demand for your products over the next 12 weeks.</div>', unsafe_allow_html=True)
        
        _my_prods_for_fc = cached_query("products", filters={"producer_id": user_id}, limit=200)
        _prod_names = [p["product_name"] for p in _my_prods_for_fc if p.get("product_name")]
        _prod_name_options = ["(All / General)"] + sorted(set(_prod_names))
        
        fc_prod_col, fc1, fc2, fc3 = st.columns([2, 2, 2, 1])
        with fc_prod_col:
            fc_product = st.selectbox("Product", _prod_name_options, key="fc_product")
        with fc1:
            _selected_prod_obj = next((p for p in _my_prods_for_fc if p["product_name"] == fc_product), None)
            _default_sector_idx = SECTORS.index(_selected_prod_obj["sector"]) if _selected_prod_obj and _selected_prod_obj.get("sector") in SECTORS else 0
            fc_sector = st.selectbox("Sector", SECTORS, index=_default_sector_idx, key="fc_sector")
        with fc2:
            _default_region_idx = REGIONS.index(_selected_prod_obj["region"]) if _selected_prod_obj and _selected_prod_obj.get("region") in REGIONS else 0
            fc_region = st.selectbox("Region", REGIONS, index=_default_region_idx, key="fc_region")
        with fc3:
            fc_horizon = st.selectbox("Weeks", [4, 8, 12, 16], index=2, key="fc_horizon")
        
        if st.button("📈 Run Demand Forecast", type="primary", use_container_width=True, key="run_forecast"):
            with st.spinner("Running AI demand model…"):
                try:
                    forecast_result = forecast_demand(
                        sector=fc_sector,
                        region=fc_region,
                        horizon=fc_horizon,
                    )
                    st.session_state.forecast_result = forecast_result
                    st.session_state.forecast_params = (fc_product, fc_sector, fc_region, fc_horizon)
                except Exception as e:
                    st.error(f"Forecast failed: {e}")
        
        result = st.session_state.get("forecast_result")
        params = st.session_state.get("forecast_params")
        if result is not None and params:
            if len(params) == 4:
                prod_p, sector_p, region_p, horizon_p = params
            else:
                prod_p, sector_p, region_p, horizon_p = "(All)", params[0], params[1], params[2]
            _prod_label = f" · {prod_p}" if prod_p and prod_p != "(All / General)" else ""
            st.markdown(f'<div class="section-title">Forecast: {sector_p}{_prod_label} · {region_p} · {horizon_p} Weeks</div>', unsafe_allow_html=True)
            
            if isinstance(result, list) and len(result) > 0:
                avg_demand = sum(result) / len(result)
                max_demand = max(result)
                trend = "📈 Rising" if result[-1] > result[0] else "📉 Falling" if result[-1] < result[0] else "➡️ Stable"
                sm1, sm2, sm3 = st.columns(3)
                with sm1:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Weekly Demand</div><div class="kpi-value">{avg_demand:,.0f}</div><div class="kpi-sub">Units / week</div></div>', unsafe_allow_html=True)
                with sm2:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Peak Week</div><div class="kpi-value">{max_demand:,.0f}</div><div class="kpi-sub">Max units</div></div>', unsafe_allow_html=True)
                with sm3:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Trend Direction</div><div class="kpi-value" style="font-size:20px;">{trend}</div></div>', unsafe_allow_html=True)
                st.markdown("")
                weeks = [f"W{i+1}" for i in range(len(result))]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=weeks, y=result,
                    mode="lines+markers",
                    line=dict(color="#D4A017", width=2),
                    marker=dict(size=6, color="#F4C430"),
                    fill="tozeroy",
                    fillcolor="rgba(212, 160, 23, 0.08)",
                    name="Demand"
                ))
                fig.update_layout(
                    paper_bgcolor="#161b27",
                    plot_bgcolor="#161b27",
                    font=dict(color="#94a3b8", family="Inter"),
                    xaxis=dict(gridcolor="#1e2a3a", showgrid=True),
                    yaxis=dict(gridcolor="#1e2a3a", showgrid=True, title="Units"),
                    margin=dict(l=40, r=20, t=20, b=40),
                    height=300,
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Error running forecast: {str(e)}")

# ─── INCOMING ORDERS TAB ───
with tab_incoming:
    try:
        st.markdown('<div class="section-title">Incoming Orders</div>', unsafe_allow_html=True)
        prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if not prod_ids:
            st.markdown('<div class="alert-box alert-info">ℹ️ You have no products listed. Add products first to receive orders.</div>', unsafe_allow_html=True)
        else:
            try:
                orders = supabase.table("orders").select(
                    "*, products(product_name, unit, sector, quality_grade, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region, role)"
                ).in_("product_id", prod_ids).in_("status", ["pending", "confirmed"]).order("created_at", desc=True).execute().data or []
            except Exception as e:
                st.error(f"Failed to load orders: {e}")
                orders = []
            
            of1, of2 = st.columns(2)
            with of1:
                ord_status = st.selectbox("Status", ["All", "pending", "confirmed"], key="ord_status_filter")
            with of2:
                ord_search = st.text_input("🔍 Search buyer", key="ord_search", placeholder="Buyer name…")
            
            filtered_orders = orders if ord_status == "All" else [o for o in orders if o.get("status") == ord_status]
            if ord_search:
                kw = ord_search.lower()
                filtered_orders = [o for o in filtered_orders if kw in (o.get("profiles") or {}).get("full_name", " ").lower()]
            
            if not filtered_orders:
                st.info("No incoming orders match the filters.")
            else:
                st.caption(f"{len(filtered_orders)} order(s)")
                STATUS_PILLS = {"pending": "pill-warning", "confirmed": "pill-info", "cancelled": "pill-danger"}
                for o in filtered_orders:
                    oid = o["id"]
                    prod = o.get("products") or {}
                    buyer = o.get("profiles") or {}
                    status = o.get("status", "pending")
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([5, 2, 3])
                        with c1:
                            pill = STATUS_PILLS.get(status, "pill-neutral")
                            st.markdown(f"Order #{str(oid)[:8]} &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                            st.markdown(f"📦 {prod.get('product_name', 'Unknown')} · {prod.get('sector', '')} · Grade {prod.get('quality_grade', '')}")
                            st.caption(f"👤 Buyer: {buyer.get('full_name', 'Unknown')} ({buyer.get('role', '').capitalize()}) · 📞 {buyer.get('phone', 'N/A')}")
                            st.caption(f"📍 Buyer region: {buyer.get('region', 'N/A')} · Date: {str(o.get('created_at', ''))[:10]}")
                        with c2:
                            qty = o.get("quantity_ordered", 0)
                            unit = prod.get("unit", "")
                            total = o.get("total_price_birr", 0)
                            st.markdown(f'<div style="font-size:13px;color:#64748b;margin-bottom:4px;">Quantity</div><div class="price-tag" style="font-size:16px;">{qty:,.1f} {unit}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div style="font-size:13px;color:#64748b;margin-top:12px;margin-bottom:4px;">Total</div><div class="price-tag">{total:,.0f}<span style="font-size:12px;color:#64748b;">Birr</span></div>', unsafe_allow_html=True)
                        with c3:
                            if status == "pending":
                                if st.button("✅ Confirm Order", key=f"confirm_{oid}", use_container_width=True, type="primary"):
                                    try:
                                        supabase.table("orders").update({"status": "confirmed", "producer_confirmed": True}).eq("id", oid).execute()
                                        send_notification(o["buyer_id"], "✅ Order Confirmed", f"Your order for {prod.get('product_name', '')} has been confirmed.", "success", order_id=str(oid))
                                        clear_data_cache()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                                if st.button("❌ Cancel Order", key=f"cancel_{oid}", use_container_width=True):
                                    try:
                                        supabase.table("orders").update({"status": "cancelled"}).eq("id", oid).execute()
                                        send_notification(o["buyer_id"], "❌ Order Cancelled", f"Your order for {prod.get('product_name', '')} was cancelled.", "error", order_id=str(oid))
                                        clear_data_cache()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                            elif status == "confirmed":
                                if st.button("🚚 Mark as Delivered", key=f"deliver_{oid}", use_container_width=True, type="primary"):
                                    try:
                                        supabase.table("orders").update({"status": "delivered"}).eq("id", oid).execute()
                                        send_notification(o["buyer_id"], "🚚 Order Delivered", f"Your order for {prod.get('product_name', '')} has been delivered.", "success", order_id=str(oid))
                                        clear_data_cache()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
    except Exception as e:
        st.error(f"⚠️ Error loading orders: {str(e)}")

# ─── AI MATCHING TAB ───
with tab_match:
    try:
        st.markdown('<div class="section-title">AI Merchant Matching</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-box alert-info">🤖 Our ML model ranks merchants by compatibility with your product — sector preference, budget, region, quality requirements, and transaction history.</div>', unsafe_allow_html=True)
        
        my_products_m = cached_query("products", filters={"producer_id": user_id, "is_available": True}, limit=200)
        if not my_products_m:
            st.markdown('<div class="alert-box alert-warning">⚠️ No available products. Activate at least one product to use AI matching.</div>', unsafe_allow_html=True)
        else:
            product_names = [p["product_name"] for p in my_products_m]
            selected_name = st.selectbox("Select Product to Match", product_names, key="match_product_select")
            p = next((x for x in my_products_m if x["product_name"] == selected_name), None)
            if p:
                pm1, pm2, pm3 = st.columns(3)
                with pm1:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Price</div><div class="price-tag">{p["price_birr"]:,.0f}</div><div class="kpi-sub">Birr / {p["unit"]}</div></div>', unsafe_allow_html=True)
                with pm2:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Stock</div><div class="kpi-value">{p["quantity"]}</div><div class="kpi-sub">{p["unit"]}</div></div>', unsafe_allow_html=True)
                with pm3:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Grade</div><div class="kpi-value" style="font-size:18px;">{p.get("quality_grade", "—")}</div><div class="kpi-sub">{p.get("sector", " ")}</div></div>', unsafe_allow_html=True)
                st.markdown("")
                
                if st.button("🤖 Find Best Merchants", type="primary", use_container_width=True, key="run_match"):
                    with st.spinner("Running AI merchant matching model…"):
                        try:
                            merchants_raw = supabase.table("profiles").select("*").eq("role", "merchant").execute().data or []
                            if not merchants_raw:
                                st.warning("No merchants registered in the system.")
                            else:
                                listing_data = {
                                    "sector": p["sector"],
                                    "product": p["product_name"],
                                    "price_birr": p["price_birr"],
                                    "quantity": p["quantity"],
                                    "region": p["region"],
                                    "quality_grade": p["quality_grade"],
                                }
                                merchant_list = [{
                                    "id": m["id"],
                                    "name": m["full_name"],
                                    "phone": m.get("phone"),
                                    "region": m.get("region"),
                                    "preferred_sector": m.get("preferred_sector"),
                                    "preferred_product": m.get("preferred_product"),
                                    "max_budget_birr": m.get("max_budget_birr") or 0,
                                    "is_verified": m.get("is_verified", False),
                                    "avg_rating": m.get("rating") or 4.0,
                                    "completion_rate": m.get("completion_rate") or 80,
                                    "avg_delivery_days": m.get("avg_delivery_days") or 5,
                                    "years_active": m.get("years_active") or 1,
                                } for m in merchants_raw]
                                ranked = rank_merchants(listing_data, merchant_list)
                                top_matches = [r for r in ranked if r.get("match_probability", 0) > 0.1][:5]
                                st.session_state.match_results = top_matches
                                st.session_state.match_product = p
                        except Exception as e:
                            st.error(f"Matching failed: {e}")
                
                results = st.session_state.get("match_results")
                match_p = st.session_state.get("match_product")
                if results is not None and match_p and match_p["id"] == p["id"]:
                    if not results:
                        st.markdown('<div class="alert-box alert-warning">No strong merchant matches found. Try a different product or check back when more merchants register.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="section-title">Top {len(results)} Matches for {p["product_name"]}</div>', unsafe_allow_html=True)
                        for i, r in enumerate(results):
                            pct = r.get("match_probability", 0) * 100
                            if pct >= 60:
                                badge_color = "#4ade80"
                                badge_label = "🟢 Strong Match"
                            elif pct >= 30:
                                badge_color = "#fbbf24"
                                badge_label = "🟡 Good Match"
                            else:
                                badge_color = "#f87171"
                                badge_label = "🔴 Weak Match"
                            with st.container(border=True):
                                c1, c2 = st.columns([5, 2])
                                with c1:
                                    st.markdown(f"#{i+1} · {r.get('name', 'Unknown')} &nbsp; <span style='font-size:12px;color:{badge_color};'>{badge_label}</span>", unsafe_allow_html=True)
                                    st.caption(f"📍 {r.get('region', 'N/A')} · 📞 {r.get('phone') or 'N/A'}")
                                    st.markdown(f"""
                                    <div style="margin-top:8px;">
                                        <div style="font-size:11px;color:#64748b;margin-bottom:4px;">{pct:.1f}% match score</div>
                                        <div class="match-bar-bg">
                                            <div class="match-bar-fill" style="width:{min(pct,100):.0f}%;background:{badge_color};"></div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with c2:
                                    agree_key = f"agree_state_{r.get('id')}_{p['id']}"
                                    agree_state = st.session_state.get(agree_key, "idle")
                                    if agree_state == "idle":
                                        if st.button("📄 Request Agreement", key=f"req_agree_{r.get('id')}_{p['id']}", use_container_width=True, type="primary"):
                                            st.session_state[agree_key] = "preview"
                                            st.rerun()
                                    elif agree_state == "preview":
                                        st.markdown("✏️ Review & Edit")
                                        agree_qty = st.number_input("Quantity", min_value=0.1, value=float(p.get("quantity", 1)), step=0.5, key=f"aq_{r.get('id')}")
                                        agree_price = st.number_input("Price per unit (Birr)", min_value=1.0, value=float(p.get("price_birr", 0)), step=10.0, key=f"ap_{r.get('id')}")
                                        agree_delivery = st.text_input("Delivery date", placeholder="e.g. 2024-09-01", key=f"ad_{r.get('id')}")
                                        agree_payment = st.selectbox("Payment method", ["Bank Transfer", "Cash on Delivery", "Mobile Money"], key=f"apay_{r.get('id')}")
                                        agree_notes = st.text_area("Notes (optional)", height=60, key=f"an_{r.get('id')}")
                                        if st.button("📤 Send to Merchant", key=f"send_agree_{r.get('id')}_{p['id']}", type="primary", use_container_width=True):
                                            try:
                                                payload = {
                                                    "agreement_id": str(datetime.datetime.now().timestamp()),
                                                    "producer_id": user_id,
                                                    "merchant_id": r["id"],
                                                    "product_id": p["id"],
                                                    "quantity": agree_qty,
                                                    "price_per_unit": agree_price,
                                                    "total_price": agree_price * agree_qty,
                                                    "delivery_date": agree_delivery,
                                                    "payment_method": agree_payment,
                                                    "notes": agree_notes,
                                                    "producer_confirmed": True,
                                                    "merchant_confirmed": False,
                                                    "producer_name": profile.get("full_name", ""),
                                                    "producer_phone": profile.get("phone", ""),
                                                    "producer_region": profile.get("region", ""),
                                                    "merchant_name": r.get("name", ""),
                                                    "merchant_phone": r.get("phone", ""),
                                                    "merchant_region": r.get("region", ""),
                                                    "product_name": p["product_name"],
                                                    "sector": p.get("sector", ""),
                                                    "quality_grade": p.get("quality_grade", "A"),
                                                    "unit": p.get("unit", "kg"),
                                                }
                                                pdf_bytes = generate_agreement_pdf(**payload)
                                                send_notification(
                                                    r["id"], "📄 New Agreement Request",
                                                    f"{profile.get('full_name', '')} sent you a supply agreement for {p['product_name']}",
                                                    "info",
                                                )
                                                st.session_state[agree_key] = "sent"
                                                st.session_state[f"agree_pdf_{r.get('id')}_{p['id']}"] = pdf_bytes
                                                clear_data_cache()
                                                st.success("✅ Agreement sent to merchant!")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Failed: {e}")
                                        if st.button("✏️ Cancel", key=f"cancel_agree_{r.get('id')}_{p['id']}", use_container_width=True):
                                            st.session_state[agree_key] = "idle"
                                            st.rerun()
                                    elif agree_state == "sent":
                                        st.markdown('<div class="alert-box alert-success">✅ Agreement sent to merchant!</div>', unsafe_allow_html=True)
                                        saved_pdf = st.session_state.get(f"agree_pdf_{r.get('id')}_{p['id']}")
                                        if saved_pdf:
                                            st.download_button(
                                                "📥 Download PDF",
                                                data=saved_pdf,
                                                file_name=f"agreement_{p['product_name']}.pdf",
                                                mime="application/pdf",
                                                key=f"dl_agree_{r.get('id')}_{p['id']}",
                                                use_container_width=True,
                                            )
    except Exception as e:
        st.error(f"⚠️ Error in matching: {str(e)}")

# ─── AGREEMENTS TAB ───
with tab_agree:
    try:
        st.markdown('<div class="section-title">Supply Agreements</div>', unsafe_allow_html=True)
        try:
            prod_ids_agree = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
            if prod_ids_agree:
                agree_orders = supabase.table("orders").select(
                    "*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)"
                ).in_("product_id", prod_ids_agree).in_("status", ["confirmed", "delivered"]).order("created_at", desc=True).execute().data or []
            else:
                agree_orders = []
        except Exception:
            agree_orders = []
        
        if not agree_orders:
            st.markdown('<div class="alert-box alert-info">📄 No confirmed agreements yet. Use AI Matching to connect with merchants.</div>', unsafe_allow_html=True)
        else:
            st.caption(f"{len(agree_orders)} agreement(s)")
            for o in agree_orders:
                prod = o.get("products") or {}
                buyer = o.get("profiles") or {}
                status = o.get("status", "confirmed")
                pill = "pill-success" if status == "delivered" else "pill-info"
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 2, 2])
                    with c1:
                        st.markdown(f"📄 {prod.get('product_name', 'Unknown')} &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                        st.caption(f"Grade: {prod.get('quality_grade', '')} · Sector: {prod.get('sector', '')} · 📍 {prod.get('region', '')}")
                        st.caption(f"🤝 With: {buyer.get('full_name', 'Unknown')} · 📞 {buyer.get('phone', 'N/A')}")
                    with c2:
                        st.markdown(f'<div class="price-tag">{o.get("quantity_ordered", 0):,.1f}</div><div style="font-size:11px;color:#64748b;">{prod.get("unit", " ")}</div>', unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<div class="price-tag">{o.get("total_price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
                    with st.expander("👁️ Preview Agreement"):
                        try:
                            qty_ord = float(o.get("quantity_ordered") or 0)
                            total_val = float(o.get("total_price_birr") or 0)
                            ppu = float(prod.get("price_birr") or (total_val / qty_ord if qty_ord else 0))
                            preview_html = generate_agreement_preview_html(
                                producer_name=profile.get("full_name", " "),
                                producer_phone=profile.get("phone", " "),
                                producer_region=profile.get("region", " "),
                                merchant_name=buyer.get("full_name", " "),
                                merchant_phone=buyer.get("phone", " "),
                                merchant_region=buyer.get("region", " "),
                                product_name=prod.get("product_name", " "),
                                sector=prod.get("sector", " "),
                                quality_grade=prod.get("quality_grade", "A"),
                                quantity=qty_ord,
                                unit=prod.get("unit", " "),
                                price_per_unit=ppu,
                                total_price=total_val,
                                delivery_date=str(o.get("created_at", ""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True,
                                merchant_confirmed=o.get("merchant_confirmed", False),
                            )
                            st.components.v1.html(preview_html, height=400, scrolling=True)
                        except Exception as ex:
                            st.caption(f"Preview unavailable: {ex}")
                        try:
                            pdf_bytes = generate_agreement_pdf(
                                producer_name=profile.get("full_name", " "),
                                producer_phone=profile.get("phone", " "),
                                producer_region=profile.get("region", " "),
                                merchant_name=buyer.get("full_name", " "),
                                merchant_phone=buyer.get("phone", " "),
                                merchant_region=buyer.get("region", " "),
                                product_name=prod.get("product_name", " "),
                                sector=prod.get("sector", " "),
                                quality_grade=prod.get("quality_grade", "A"),
                                quantity=qty_ord,
                                unit=prod.get("unit", " "),
                                price_per_unit=ppu,
                                total_price=total_val,
                                delivery_date=str(o.get("created_at", ""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True,
                                merchant_confirmed=o.get("merchant_confirmed", False),
                            )
                            st.download_button("📥 Download PDF", data=pdf_bytes,
                                file_name=f"agreement_{prod.get('product_name', '')}.pdf",
                                mime="application/pdf", key=f"agree_pdf_{o['id']}"
                            )
                        except Exception:
                            pass
    except Exception as e:
        st.error(f"⚠️ Error loading agreements: {str(e)}")

# ─── HISTORY TAB ───
with tab_history:
    try:
        st.markdown('<div class="section-title">Delivery History</div>', unsafe_allow_html=True)
        hist_prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if not hist_prod_ids:
            st.info("No products yet.")
        else:
            try:
                hist_orders = supabase.table("orders").select(
                    "*, products(product_name, unit, sector, quality_grade, region), profiles!orders_buyer_id_fkey(full_name, phone, region)"
                ).in_("product_id", hist_prod_ids).eq("status", "delivered").order("created_at", desc=True).execute().data or []
            except Exception:
                hist_orders = []
            if not hist_orders:
                st.markdown('<div class="alert-box alert-info">📜 No delivered orders yet.</div>', unsafe_allow_html=True)
            else:
                total_rev = sum(float(o.get("total_price_birr") or 0) for o in hist_orders)
                h1, h2 = st.columns(2)
                with h1:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Revenue</div><div class="price-tag">{total_rev:,.0f}</div><div class="kpi-sub">Birr earned</div></div>', unsafe_allow_html=True)
                with h2:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Completed Orders</div><div class="kpi-value">{len(hist_orders)}</div><div class="kpi-sub">Delivered successfully</div></div>', unsafe_allow_html=True)
                st.markdown("")
                monthly = {}
                for o in hist_orders:
                    month = o.get("created_at", "")[:7]
                    monthly[month] = monthly.get(month, 0) + float(o.get("total_price_birr") or 0)
                if monthly:
                    df_monthly = pd.DataFrame({"Month": list(monthly.keys()), "Revenue": list(monthly.values())}).sort_values("Month")
                    st.markdown('<div class="section-title">Monthly Revenue</div>', unsafe_allow_html=True)
                    st.bar_chart(df_monthly.set_index("Month"), height=200, color="#D4A017")
                st.markdown('<div class="section-title">Delivered Orders</div>', unsafe_allow_html=True)
                for o in hist_orders:
                    prod = o.get("products") or {}
                    buyer = o.get("profiles") or {}
                    with st.container(border=True):
                        c1, c2 = st.columns([5, 2])
                        with c1:
                            st.markdown(f"✅ {prod.get('product_name', 'Unknown')} · {prod.get('sector', '')}")
                            st.caption(f"👤 Buyer: {buyer.get('full_name', 'Unknown')} · 📍 {buyer.get('region', 'N/A')}")
                            st.caption(f"📅 {str(o.get('created_at', ''))[:10]} · {o.get('quantity_ordered', 0):,.1f} {prod.get('unit', '')}")
                        with c2:
                            st.markdown(f'<div class="price-tag">{o.get("total_price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Error loading history: {str(e)}")

# ─── NOTIFICATIONS ───
with tab_notif:
    try:
        render_notifications_tab(user_id)
    except Exception as e:
        st.error(f"⚠️ Error loading notifications: {str(e)}")

# ─── PROFILE ───
with tab_profile:
    try:
        render_profile_editor_modal(profile, user_id, key_suffix="producer_tab")
    except Exception as e:
        st.error(f"⚠️ Error loading profile: {str(e)}")
