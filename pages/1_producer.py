"""Producer Dashboard — Working Hamburger Menu."""
import sys
import os
import datetime
import streamlit as st
import pandas as pd

# ─────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
try:
    from utils.theme import inject_theme
    from utils.db_helpers import supabase, cached_query, clear_data_cache
    from utils.verification import check_verification_status
    from utils.auth import sign_out
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
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# ─────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────
inject_theme()

# ─────────────────────────────────────────────────────────────
# CSS - HIDE SIDEBAR, SHOW HAMBURGER MENU
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

/* ─── METRICS ─── */
[data-testid="stMetric"] {
    background: #161b27 !important;
    border: 1px solid #1e2a3a !important;
    border-radius: 10px !important;
    padding: 16px !important;
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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HAMBURGER MENU - HTML + JavaScript
# ─────────────────────────────────────────────────────────────
def render_hamburger_menu():
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
    ''', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CUSTOM SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_custom_sidebar(profile):
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
    
    # Verification status
    try:
        verif_status = check_verification_status(st.session_state.user.id)
        if verif_status.get("is_verified", False):
            status_html = '<span class="pill pill-success">✅ Verified</span>'
        else:
            status_html = '<span class="pill pill-warning">⏳ Pending</span>'
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
            <div class="sidebar-role">🚜 Producer · {region}</div>
        </div>
        
        <hr class="sidebar-divider">
        
        <div class="sidebar-section-title">📊 Navigation</div>
        <button class="sidebar-nav-btn" onclick="window.location.href='app.py'">🏠 Home</button>
        <button class="sidebar-nav-btn" onclick="window.location.href='pages/1_producer.py'">🚜 Producer</button>
        <button class="sidebar-nav-btn" onclick="window.location.href='pages/2_merchant.py'">🏬 Merchant</button>
        <button class="sidebar-nav-btn" onclick="window.location.href='pages/3_customer.py'">🛒 Customer</button>
        <button class="sidebar-nav-btn" onclick="window.location.href='pages/4_Admin.py'">🛡️ Admin</button>
        
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
            sign_out()
            st.session_state.user = None
            st.session_state.profile = None
            st.session_state.authenticated = False
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
render_custom_sidebar(profile)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
verif_badge = '<span class="pill pill-success">✅ Verified</span>' if verif_status.get("is_verified", False) else '<span class="pill pill-warning">⏳ Pending</span>'

st.markdown(f"""
<div style="background: linear-gradient(135deg, #0d2b1e 0%, #0f1117 60%, #122010 100%);
            border: 1px solid #1a3d2b; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;">
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: #1e2a3a; 
             display: flex; align-items: center; justify-content: center; font-size: 20px; 
             color: #f1f5f9; font-weight: 700; border: 2px solid #D4A017;">
            {profile.get('full_name', 'U')[0].upper()}
        </div>
        <div style="flex: 1;">
            <h1 style="margin: 0; font-size: 20px; font-weight: 700; color: #f1f5f9;">🚜 Producer Dashboard</h1>
            <p style="margin: 2px 0 0; font-size: 13px; color: #64748b;">
                {profile.get('full_name', 'Producer')} · 📍 {profile.get('region', 'N/A')} · {now_str}
            </p>
        </div>
        <div>{verif_badge}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📦 Products", "📈 Forecast", "📬 Orders"])

# ─── TAB 1: OVERVIEW ───
with tab1:
    try:
        my_products = cached_query("products", filters={"producer_id": user_id}, limit=500)
        total_products = len(my_products)
        active_products = sum(1 for p in my_products if p.get("is_available", False))
        
        # Get orders
        product_ids = [p["id"] for p in my_products] if my_products else []
        if product_ids:
            orders_response = supabase.table("orders").select("*").in_("product_id", product_ids).execute()
            orders = orders_response.data if orders_response else []
        else:
            orders = []
        
        pending_orders = sum(1 for o in orders if o.get("status") == "pending")
        total_revenue = sum(float(o.get("total_price_birr") or 0) for o in orders if o.get("status") == "delivered")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Products", total_products, f"{active_products} active")
        c2.metric("Pending Orders", pending_orders)
        c3.metric("Total Revenue", f"{total_revenue:,.0f} Birr")
        c4.metric("Listings", total_products)
        
        if my_products:
            st.markdown("---")
            st.markdown("### 📦 Recent Products")
            for p in my_products[:5]:
                with st.container(border=True):
                    st.markdown(f"**{p.get('product_name', 'Unknown')}**")
                    st.caption(f"{p.get('sector', '—')} · {p.get('region', '—')} · {p.get('price_birr', 0):,.0f} Birr")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ─── TAB 2: PRODUCTS ───
with tab2:
    try:
        my_products = cached_query("products", filters={"producer_id": user_id}, limit=200)
        
        if not my_products:
            st.info("No products yet. Add your first product below.")
        else:
            for p in my_products:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{p.get('product_name', 'Unknown')}**")
                        st.caption(f"{p.get('sector', '—')} · {p.get('region', '—')} · Stock: {p.get('quantity', 0)} {p.get('unit', '')}")
                    with c2:
                        st.markdown(f"**{p.get('price_birr', 0):,.0f} Birr**")
                        if st.button("🗑️ Delete", key=f"del_{p['id']}"):
                            try:
                                supabase.table("products").delete().eq("id", p["id"]).execute()
                                clear_data_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        
        with st.expander("➕ Add Product"):
            with st.form("add_product"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Product Name *")
                    sector = st.selectbox("Sector", ["Agriculture", "Livestock", "Manufacturing", "Other"])
                    region = st.selectbox("Region", ["Addis Ababa", "Oromia", "Amhara", "Tigray", "Other"])
                with col2:
                    quantity = st.number_input("Quantity", min_value=0.1, value=1.0, step=0.5)
                    unit = st.selectbox("Unit", ["kg", "ton", "litre", "piece", "quintal"])
                    price = st.number_input("Price (Birr)", min_value=1.0, value=100.0, step=10.0)
                
                if st.form_submit_button("✅ Add Product", type="primary"):
                    if not name:
                        st.error("Product name is required.")
                    else:
                        try:
                            data = {
                                "producer_id": user_id,
                                "product_name": name,
                                "sector": sector,
                                "region": region,
                                "quantity": quantity,
                                "unit": unit,
                                "price_birr": price,
                                "is_available": True,
                            }
                            supabase.table("products").insert(data).execute()
                            clear_data_cache()
                            st.success(f"✅ '{name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ─── TAB 3: FORECAST ───
with tab3:
    try:
        st.markdown("### 📈 Demand Forecast")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fc_sector = st.selectbox("Sector", ["Agriculture", "Livestock", "Manufacturing", "Other"])
        with col2:
            fc_region = st.selectbox("Region", ["Addis Ababa", "Oromia", "Amhara", "Tigray", "Other"])
        with col3:
            fc_weeks = st.selectbox("Weeks", [4, 8, 12, 16], index=2)
        
        if st.button("📈 Run Forecast", type="primary"):
            try:
                from src.demand_engine import forecast_demand
                with st.spinner("Running forecast..."):
                    result = forecast_demand(sector=fc_sector, region=fc_region, horizon=fc_weeks)
                
                if result:
                    st.success("✅ Forecast complete!")
                    
                    # Chart
                    df = pd.DataFrame({
                        "Week": [f"W{i+1}" for i in range(len(result))],
                        "Demand": result
                    })
                    st.line_chart(df.set_index("Week"))
                    
                    # Stats
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Average Demand", f"{sum(result)/len(result):.0f}")
                    c2.metric("Peak Demand", f"{max(result):.0f}")
                    c3.metric("Trend", "📈 Rising" if result[-1] > result[0] else "📉 Falling")
            except Exception as e:
                st.error(f"Forecast error: {e}")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ─── TAB 4: ORDERS ───
with tab4:
    try:
        st.markdown("### 📬 My Orders")
        
        product_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, limit=500)]
        if not product_ids:
            st.info("Add products first to receive orders.")
        else:
            orders = supabase.table("orders").select(
                "*, products(product_name, unit, sector)"
            ).in_("product_id", product_ids).order("created_at", desc=True).execute().data or []
            
            if not orders:
                st.info("No orders yet.")
            else:
                for o in orders:
                    prod = o.get("products") or {}
                    status = o.get("status", "pending")
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"**Order #{str(o['id'])[:8]}**")
                            st.markdown(f"📦 {prod.get('product_name', 'Unknown')}")
                            st.caption(f"Status: {status.upper()} · {prod.get('sector', '')}")
                        with c2:
                            st.metric("Total", f"{o.get('total_price_birr', 0):,.0f} Birr")
                            if status == "pending":
                                if st.button("✅ Confirm", key=f"confirm_{o['id']}"):
                                    try:
                                        supabase.table("orders").update({"status": "confirmed"}).eq("id", o["id"]).execute()
                                        clear_data_cache()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("✅ Tap the ☰ button in the top-left to open the menu.")
