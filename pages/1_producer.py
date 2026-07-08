"""Producer Dashboard — Working Hamburger Menu."""
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
    from utils.theme import inject_theme
    from utils.constants import REGIONS, SECTORS, UNITS
    from utils.db_helpers import supabase, cached_query, clear_data_cache, send_notification
    from utils.verification import check_verification_status, render_document_upload
    from utils.shared_ui import (
        get_grades_for_product, map_grade_to_db, render_browse_tab,
        render_notifications_tab, render_profile_editor_modal,
    )
    from utils.pdf_generator import generate_agreement_pdf, generate_agreement_preview_html
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
    st.session_state.menu_open = False

# ─────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────
inject_theme()

# ─────────────────────────────────────────────────────────────
# CSS - HIDE SIDEBAR, CUSTOM HAMBURGER MENU
# ─────────────────────────────────────────────────────────────
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

/* ─── HAMBURGER MENU CONTAINER ─── */
.hamburger-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 999997;
    background: #0f1117;
    padding: 8px 12px;
    border-bottom: 1px solid #1e2a3a;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* ─── HAMBURGER MENU BUTTON ─── */
.hamburger-btn {
    background: #1B4332;
    color: white;
    border: 2px solid #2D6A4F;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 22px;
    cursor: pointer;
    transition: all 0.2s;
}
.hamburger-btn:hover {
    background: #2D6A4F;
}

/* ─── HAMBURGER TITLE ─── */
.hamburger-title {
    color: #e2e8f0;
    font-size: 16px;
    font-weight: 600;
    margin-left: 8px;
}
.hamburger-title span {
    color: #D4A017;
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
    font-size: 22px;
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
    padding-top: 60px !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
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

/* ─── RESPONSIVE ─── */
@media (max-width: 768px) {
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 60px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
    }
    .hamburger-title {
        font-size: 14px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU - HTML + JavaScript
# ─────────────────────────────────────────────────────────────
def render_hamburger_menu():
    """Render the hamburger menu bar."""
    
    # Get profile
    profile = st.session_state.get("profile", {})
    name = profile.get("full_name", "User") if profile else "User"
    
    # HTML for hamburger bar
    st.markdown(f'''
    <div class="hamburger-container">
        <button class="hamburger-btn" onclick="
            var sidebar = document.getElementById('mobileSidebar');
            var overlay = document.getElementById('mobileOverlay');
            if (sidebar.classList.contains('open')) {{
                sidebar.classList.remove('open');
                overlay.classList.remove('active');
            }} else {{
                sidebar.classList.add('open');
                overlay.classList.add('active');
            }}
        ">☰</button>
        <div class="hamburger-title">🌾 <span>AI Supply Chain</span> · {name}</div>
    </div>
    ''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CUSTOM SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_custom_sidebar(profile, user_id, role):
    """Render custom sidebar."""
    
    if not profile:
        st.markdown('''
        <div class="mobile-sidebar" id="mobileSidebar">
            <button class="close-sidebar-btn" onclick="
                document.getElementById('mobileSidebar').classList.remove('open');
                document.getElementById('mobileOverlay').classList.remove('active');
            ">✕</button>
            <div class="sidebar-profile">
                <div class="sidebar-avatar">🔐</div>
                <div class="sidebar-name">Not Signed In</div>
                <div class="sidebar-role">Please sign in</div>
            </div>
            <hr class="sidebar-divider">
            <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        </div>
        <div class="mobile-overlay" id="mobileOverlay" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            this.classList.remove('active');
        "></div>
        ''', unsafe_allow_html=True)
        return
    
    name = profile.get("full_name", "User")
    region = profile.get("region", "N/A")
    role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(role, "👤")
    
    # Verification status
    try:
        verif_status = check_verification_status(user_id)
        if verif_status.get("is_verified", False):
            status_html = '<span class="pill pill-success">✅ Verified</span>'
        elif verif_status.get("has_documents", False):
            status_html = '<span class="pill pill-warning">⏳ Pending</span>'
        else:
            status_html = '<span class="pill pill-info">📄 Verify</span>'
    except Exception:
        status_html = '<span class="pill pill-neutral">⚠️ Unknown</span>'
    
    sidebar_html = f'''
    <div class="mobile-sidebar" id="mobileSidebar">
        <button class="close-sidebar-btn" onclick="
            document.getElementById('mobileSidebar').classList.remove('open');
            document.getElementById('mobileOverlay').classList.remove('active');
        ">✕</button>
        
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{name[0].upper()}</div>
            <div class="sidebar-name">{name}</div>
            <div class="sidebar-role">{role_icon} {role.capitalize()} · {region}</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📊 Navigation</div>
        <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
    '''
    
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
        <div style="margin-bottom: 8px;">{status_html}</div>
        <hr class="sidebar-divider">
        <button class="sidebar-nav-btn-logout" onclick="window.location.href = window.location.pathname + '?logout=true';">🚪 Log Out</button>
    </div>
    <div class="mobile-overlay" id="mobileOverlay" onclick="
        document.getElementById('mobileSidebar').classList.remove('open');
        this.classList.remove('active');
    "></div>
    '''
    
    st.markdown(sidebar_html, unsafe_allow_html=True)
    
    # Handle logout
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
# RENDER HAMBURGER MENU AND SIDEBAR
# ─────────────────────────────────────────────────────────────
render_hamburger_menu()
render_custom_sidebar(profile, user_id, "producer")

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
verif_badge = '<span class="pill pill-success">✓ Verified</span>' if verif_status["is_verified"] else '<span class="pill pill-warning">⏳ Pending</span>'

profile_pic = profile.get("profile_image")
if profile_pic:
    profile_pic_html = f'<img src="data:image/jpeg;base64,{profile_pic}" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4A017; object-fit: cover;">'
else:
    profile_pic_html = f'<div style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; font-size: 20px; color: #f1f5f9; font-weight: 700;">{profile.get("full_name", "U")[0].upper()}</div>'

st.markdown(f"""
<div style="background: #161b27; border: 1px solid #1e2a3a; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px;
            display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
    <div style="flex-shrink: 0;">{profile_pic_html}</div>
    <div style="flex: 1; min-width: 120px;">
        <h1 style="margin: 0; font-size: 18px; font-weight: 700; color: #f1f5f9;">🚜 Producer Dashboard</h1>
        <p style="margin: 2px 0 0; font-size: 12px; color: #64748b;">
            {profile.get('full_name', 'Producer')} · 📍 {profile.get('region', 'N/A')} · {now_str}
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
    "📊 Overview", "📦 Products", "📈 Forecast",
    "📬 Orders", "🤝 Match", "📄 Agreements",
    "📜 History", "🔔 Notif", "👤 Profile",
])

# ══════════════════════════════════════════════
# TAB — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:
    try:
        my_products_all = cached_query("products", filters={"producer_id": user_id}, limit=500)
        
        product_ids = [p["id"] for p in my_products_all] if my_products_all else []
        if product_ids:
            orders_response = supabase.table("orders").select(
                "*, products!inner(producer_id)"
            ).in_("product_id", product_ids).execute()
            my_orders_all = orders_response.data if orders_response else []
        else:
            my_orders_all = []
        
        total_val = sum(p.get("price_birr", 0) * p.get("quantity", 0) for p in my_products_all)
        active_prods = sum(1 for p in my_products_all if p.get("is_available", False))
        pending_orders_cnt = sum(1 for o in my_orders_all if o.get("status") == "pending")
        delivered_orders = [o for o in my_orders_all if o.get("status") == "delivered"]
        total_revenue = sum(float(o.get("total_price_birr") or 0) for o in delivered_orders)
        
        if pending_orders_cnt > 0:
            st.warning(f"📬 You have {pending_orders_cnt} pending order(s)")
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Products Listed", len(my_products_all), f"{active_prods} active")
        with k2:
            st.metric("Inventory Value", f"{total_val:,.0f} Birr")
        with k3:
            st.metric("Pending Orders", pending_orders_cnt)
        with k4:
            st.metric("Total Revenue", f"{total_revenue:,.0f} Birr")
        
        if my_products_all:
            st.markdown("---")
            st.markdown("### Products by Sector")
            sector_counts = {}
            for p in my_products_all:
                s = p.get("sector", "Other")
                sector_counts[s] = sector_counts.get(s, 0) + 1
            df_sector = pd.DataFrame({"Sector": list(sector_counts.keys()), "Count": list(sector_counts.values())})
            st.bar_chart(df_sector.set_index("Sector"), height=200)
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── PRODUCTS TAB ───
with tab_products:
    try:
        st.markdown("### 📦 My Products")
        my_products = cached_query("products", filters={"producer_id": user_id}, limit=200)
        
        if my_products:
            total_val2 = sum(p.get("price_birr", 0) * p.get("quantity", 0) for p in my_products)
            active2 = sum(1 for p in my_products if p.get("is_available", False))
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Listed", len(my_products))
            c2.metric("Active", active2)
            c3.metric("Inventory Value", f"{total_val2:,.0f} Birr")
        
        with st.expander("➕ Add New Product", expanded=not bool(my_products)):
            with st.form("add_product_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Product Name *", placeholder="e.g. Teff")
                    new_sector = st.selectbox("Sector *", SECTORS)
                    available_grades = get_grades_for_product(new_sector, new_name) if new_sector else ["A", "B", "C"]
                    new_grade_ui = st.selectbox("Quality Grade *", available_grades)
                    new_grade_db = map_grade_to_db(new_grade_ui)
                    new_region = st.selectbox("Region *", REGIONS)
                with c2:
                    new_qty = st.number_input("Quantity *", min_value=0.1, value=1.0, step=0.5)
                    new_unit = st.selectbox("Unit *", UNITS)
                    new_price = st.number_input("Price (Birr) *", min_value=1.0, value=100.0, step=10.0)
                    new_avail = st.checkbox("List as Available", value=True)
                
                new_image = st.file_uploader("📷 Image", type=["jpg", "jpeg", "png"], key="prod_img_upload")
                new_desc = st.text_area("Description", height=60)
                submitted = st.form_submit_button("✅ Add Product", type="primary")
                
                if submitted:
                    if not new_name.strip():
                        st.error("Product name is required.")
                    else:
                        try:
                            data = {
                                "producer_id": user_id,
                                "product_name": new_name.strip(),
                                "sector": new_sector,
                                "quality_grade": new_grade_db,
                                "region": new_region,
                                "quantity": new_qty,
                                "unit": new_unit,
                                "price_birr": new_price,
                                "is_available": new_avail,
                                "description": new_desc.strip() or None,
                            }
                            if new_image:
                                data["image_base64"] = base64.b64encode(new_image.read()).decode("utf-8")
                            supabase.table("products").insert(data).execute()
                            clear_data_cache()
                            st.success(f"✅ '{new_name}' listed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        if my_products:
            for p in my_products:
                with st.container(border=True):
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        if p.get("image_base64"):
                            st.image(f"data:image/jpeg;base64,{p['image_base64']}", width=100)
                        else:
                            st.markdown("📷 No Image")
                    with c2:
                        st.markdown(f"**{p['product_name']}**")
                        st.caption(f"{p.get('sector', '—')} · Grade {p.get('quality_grade', '—')} · {p.get('region', '—')}")
                        st.caption(f"Stock: {p.get('quantity', 0)} {p.get('unit', '')} · Price: {p.get('price_birr', 0):,.0f} Birr")
                        if st.button("🗑️ Delete", key=f"del_{p['id']}"):
                            if st.button("✅ Confirm Delete", key=f"confirm_del_{p['id']}"):
                                supabase.table("products").delete().eq("id", p["id"]).execute()
                                clear_data_cache()
                                st.rerun()
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── DEMAND FORECAST ───
with tab_demand:
    try:
        st.markdown("### 📈 Demand Forecast")
        
        _my_prods = cached_query("products", filters={"producer_id": user_id}, limit=200)
        _prod_names = [p["product_name"] for p in _my_prods if p.get("product_name")]
        _prod_options = ["(All)"] + sorted(set(_prod_names))
        
        fc_prod = st.selectbox("Product", _prod_options, key="fc_prod")
        fc_sector = st.selectbox("Sector", SECTORS, key="fc_sector")
        fc_region = st.selectbox("Region", REGIONS, key="fc_region")
        fc_horizon = st.selectbox("Weeks", [4, 8, 12, 16], index=2, key="fc_horizon")
        
        if st.button("📈 Run Forecast", type="primary"):
            with st.spinner("Running..."):
                result = forecast_demand(sector=fc_sector, region=fc_region, horizon=fc_horizon)
                st.session_state.forecast_result = result
                st.session_state.forecast_params = (fc_prod, fc_sector, fc_region, fc_horizon)
        
        if st.session_state.get("forecast_result"):
            result = st.session_state.forecast_result
            if isinstance(result, list) and result:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[f"W{i+1}" for i in range(len(result))],
                    y=result,
                    mode="lines+markers",
                    line=dict(color="#D4A017", width=2),
                    marker=dict(size=6, color="#F4C430")
                ))
                fig.update_layout(
                    paper_bgcolor="#161b27",
                    plot_bgcolor="#161b27",
                    font=dict(color="#94a3b8"),
                    height=300,
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)
                c1, c2, c3 = st.columns(3)
                c1.metric("Average", f"{sum(result)/len(result):.0f}")
                c2.metric("Peak", f"{max(result):.0f}")
                c3.metric("Trend", "📈 Rising" if result[-1] > result[0] else "📉 Falling")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── INCOMING ORDERS ───
with tab_incoming:
    try:
        st.markdown("### 📬 Incoming Orders")
        
        prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if not prod_ids:
            st.info("Add products first to receive orders.")
        else:
            orders = supabase.table("orders").select(
                "*, products(product_name, unit, sector, region), profiles!orders_buyer_id_fkey(full_name, phone)"
            ).in_("product_id", prod_ids).in_("status", ["pending", "confirmed"]).order("created_at", desc=True).execute().data or []
            
            if not orders:
                st.info("No incoming orders.")
            else:
                for o in orders:
                    prod = o.get("products") or {}
                    buyer = o.get("profiles") or {}
                    status = o.get("status", "pending")
                    with st.container(border=True):
                        c1, c2 = st.columns([2, 1])
                        with c1:
                            st.markdown(f"**Order #{str(o['id'])[:8]}** · {status.upper()}")
                            st.markdown(f"📦 {prod.get('product_name', 'Unknown')} · {prod.get('sector', '')}")
                            st.caption(f"Buyer: {buyer.get('full_name', 'Unknown')} · {buyer.get('phone', '')}")
                        with c2:
                            st.metric("Total", f"{o.get('total_price_birr', 0):,.0f} Birr")
                            if status == "pending":
                                if st.button("✅ Confirm", key=f"confirm_{o['id']}"):
                                    supabase.table("orders").update({"status": "confirmed"}).eq("id", o["id"]).execute()
                                    send_notification(o["buyer_id"], "✅ Order Confirmed", "Your order has been confirmed.")
                                    clear_data_cache()
                                    st.rerun()
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── AI MATCHING ───
with tab_match:
    try:
        st.markdown("### 🤝 AI Merchant Matching")
        
        my_products_m = cached_query("products", filters={"producer_id": user_id, "is_available": True}, limit=200)
        if not my_products_m:
            st.warning("No available products.")
        else:
            selected = st.selectbox("Select Product", [p["product_name"] for p in my_products_m])
            p = next((x for x in my_products_m if x["product_name"] == selected), None)
            
            if p and st.button("🔍 Find Matches", type="primary"):
                with st.spinner("Matching..."):
                    merchants = supabase.table("profiles").select("*").eq("role", "merchant").execute().data or []
                    listing = {"sector": p["sector"], "product": p["product_name"], "price_birr": p["price_birr"], "quantity": p["quantity"], "region": p["region"]}
                    merchant_list = [{"id": m["id"], "name": m["full_name"], "phone": m.get("phone"), "region": m.get("region")} for m in merchants]
                    results = rank_merchants(listing, merchant_list)
                    st.session_state.match_results = results[:5]
            
            if st.session_state.get("match_results"):
                for i, r in enumerate(st.session_state.match_results):
                    pct = r.get("match_probability", 0) * 100
                    with st.container(border=True):
                        st.markdown(f"#{i+1} **{r.get('name', 'Unknown')}** · {pct:.0f}% match")
                        st.caption(f"📍 {r.get('region', 'N/A')} · 📞 {r.get('phone', 'N/A')}")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── AGREEMENTS ───
with tab_agree:
    try:
        st.markdown("### 📄 Agreements")
        prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if prod_ids:
            agreements = supabase.table("orders").select(
                "*, products(product_name, unit), profiles!orders_buyer_id_fkey(full_name)"
            ).in_("product_id", prod_ids).in_("status", ["confirmed", "delivered"]).execute().data or []
            
            if not agreements:
                st.info("No agreements yet.")
            else:
                for o in agreements:
                    prod = o.get("products") or {}
                    buyer = o.get("profiles") or {}
                    with st.container(border=True):
                        st.markdown(f"**{prod.get('product_name', 'Unknown')}** · {o.get('status', '').upper()}")
                        st.caption(f"Buyer: {buyer.get('full_name', 'Unknown')} · {o.get('total_price_birr', 0):,.0f} Birr")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── HISTORY ───
with tab_history:
    try:
        st.markdown("### 📜 History")
        prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if prod_ids:
            history = supabase.table("orders").select(
                "*, products(product_name), profiles!orders_buyer_id_fkey(full_name)"
            ).in_("product_id", prod_ids).eq("status", "delivered").execute().data or []
            
            if not history:
                st.info("No delivery history.")
            else:
                total = sum(o.get("total_price_birr", 0) for o in history)
                st.metric("Total Revenue", f"{total:,.0f} Birr")
                for o in history:
                    prod = o.get("products") or {}
                    buyer = o.get("profiles") or {}
                    st.caption(f"✅ {prod.get('product_name', 'Unknown')} · {buyer.get('full_name', 'Unknown')} · {o.get('total_price_birr', 0):,.0f} Birr")
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")

# ─── NOTIFICATIONS ───
with tab_notif:
    render_notifications_tab(user_id)

# ─── PROFILE ───
with tab_profile:
    render_profile_editor_modal(profile, user_id, key_suffix="producer_tab")
