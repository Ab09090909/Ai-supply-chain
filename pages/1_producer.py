"""Producer Dashboard — Using Reusable Hamburger Menu."""
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
    from utils.hamburger import render_hamburger
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
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# THEME INJECTION
# ─────────────────────────────────────────────
inject_theme()

# ─────────────────────────────────────────────
# RENDER HAMBURGER MENU
# ─────────────────────────────────────────────
render_hamburger()

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
# HEADER
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📦 Products", "📈 Forecast", "📬 Orders"])

# ─── TAB 1: OVERVIEW ───
with tab1:
    try:
        my_products = cached_query("products", filters={"producer_id": user_id}, limit=500)
        total_products = len(my_products)
        active_products = sum(1 for p in my_products if p.get("is_available", False))
        
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
                    
                    df = pd.DataFrame({
                        "Week": [f"W{i+1}" for i in range(len(result))],
                        "Demand": result
                    })
                    st.line_chart(df.set_index("Week"))
                    
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
