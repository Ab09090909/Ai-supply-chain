"""Producer Dashboard — Using Streamlit Native Components."""
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
    initial_sidebar_state="expanded",  # Keep sidebar expanded by default
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

# ─────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# GET USER DATA
# ─────────────────────────────────────────────
profile = st.session_state.get("profile", {})
user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

# ─────────────────────────────────────────────
# SIDEBAR - Using Streamlit Native
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 AI Supply Chain")
    st.markdown("---")
    
    # Profile
    st.markdown(f"""
    <div style="text-align: center; margin: 10px 0;">
        <div style="width: 60px; height: 60px; border-radius: 50%; background: #1e2a3a; 
             display: flex; align-items: center; justify-content: center; margin: 0 auto; 
             font-size: 24px; color: #f1f5f9; font-weight: 700; border: 2px solid #D4A017;">
            {profile.get('full_name', 'U')[0].upper()}
        </div>
        <div style="font-size: 16px; font-weight: 600; margin-top: 8px; color: #e2e8f0;">
            {profile.get('full_name', 'User')}
        </div>
        <div style="font-size: 12px; color: #94a3b8;">
            🚜 Producer · {profile.get('region', 'N/A')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 📊 Navigation")
    
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.switch_page("app.py")
    
    if st.button("🚜 Producer", key="nav_producer", use_container_width=True):
        st.switch_page("pages/1_producer.py")
    
    if st.button("🏬 Merchant", key="nav_merchant", use_container_width=True):
        st.switch_page("pages/2_merchant.py")
    
    if st.button("🛒 Customer", key="nav_customer", use_container_width=True):
        st.switch_page("pages/3_customer.py")
    
    if st.button("🛡️ Admin", key="nav_admin", use_container_width=True):
        st.switch_page("pages/4_Admin.py")
    
    st.markdown("---")
    
    # Status
    st.markdown("### 📌 Status")
    if verif_status.get("is_verified", False):
        st.markdown('<span class="pill pill-success">✅ Verified</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-warning">⏳ Pending</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Logout
    if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
        try:
            from utils.auth import sign_out
            sign_out()
            st.session_state.user = None
            st.session_state.profile = None
            st.session_state.authenticated = False
            clear_data_cache()
            st.rerun()
        except Exception as e:
            st.error(f"Logout error: {e}")

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown(f"""
<div style="background: linear-gradient(135deg, #0d2b1e 0%, #0f1117 60%, #122010 100%);
            border: 1px solid #1a3d2b; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px;">
    <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #f1f5f9;">🚜 Producer Dashboard</h1>
    <p style="margin: 4px 0 0; font-size: 13px; color: #64748b;">
        Welcome back, <strong>{profile.get('full_name', 'Producer')}</strong> · 📍 {profile.get('region', 'N/A')} · {now_str}
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📦 Products", "📈 Forecast"])

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
        c1.metric("Products", total_products, f"{active_products} active")
        c2.metric("Pending Orders", pending_orders)
        c3.metric("Revenue", f"{total_revenue:,.0f} Birr")
        c4.metric("Listings", total_products)
        
        if my_products:
            st.markdown("---")
            st.markdown("### Recent Products")
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
                        if st.button("🗑️", key=f"del_{p['id']}"):
                            supabase.table("products").delete().eq("id", p["id"]).execute()
                            clear_data_cache()
                            st.rerun()
        
        with st.expander("➕ Add Product"):
            with st.form("add_product"):
                name = st.text_input("Product Name")
                sector = st.selectbox("Sector", ["Agriculture", "Livestock", "Manufacturing", "Other"])
                region = st.selectbox("Region", ["Addis Ababa", "Oromia", "Amhara", "Tigray", "Other"])
                quantity = st.number_input("Quantity", min_value=0.1, value=1.0)
                unit = st.selectbox("Unit", ["kg", "ton", "litre", "piece"])
                price = st.number_input("Price (Birr)", min_value=1.0, value=100.0)
                
                if st.form_submit_button("Add Product", type="primary"):
                    if name:
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
                        st.success(f"✅ '{name}' added!")
                        st.rerun()
                    else:
                        st.error("Product name is required.")
                        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ─── TAB 3: FORECAST ───
with tab3:
    try:
        st.markdown("### 📈 Demand Forecast")
        
        fc_sector = st.selectbox("Sector", ["Agriculture", "Livestock", "Manufacturing", "Other"])
        fc_region = st.selectbox("Region", ["Addis Ababa", "Oromia", "Amhara", "Tigray", "Other"])
        fc_weeks = st.selectbox("Weeks", [4, 8, 12, 16], index=2)
        
        if st.button("Run Forecast", type="primary"):
            try:
                from src.demand_engine import forecast_demand
                result = forecast_demand(sector=fc_sector, region=fc_region, horizon=fc_weeks)
                
                if result:
                    st.success("✅ Forecast complete!")
                    st.line_chart(result)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Average", f"{sum(result)/len(result):.0f}")
                    c2.metric("Peak", f"{max(result):.0f}")
                    c3.metric("Trend", "📈 Rising" if result[-1] > result[0] else "📉 Falling")
            except Exception as e:
                st.error(f"Forecast error: {e}")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("✅ If you can see this page, the sidebar is working!")
