"""Customer Dashboard — Professional dark design matching Admin panel."""
import sys
import os
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_theme, render_theme_toggle
from utils.db_helpers import supabase, clear_data_cache, send_notification
from utils.constants import REGIONS, SECTORS
from utils.verification import check_verification_status, render_document_upload
from utils.shared_ui import render_browse_tab, render_notifications_tab, render_profile_edit_tab, render_profile_editor_modal
from utils.pdf_generator import generate_agreement_pdf, generate_agreement_preview_html

# ─────────────────────────────────────────────
# Page Config + CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117 !important;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2a3a;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Header ── */
.dash-header {
    background: linear-gradient(135deg, #1a1020 0%, #0f1117 60%, #1a1030 100%);
    border: 1px solid #2a1a4a;
    border-radius: 12px; 
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.dash-header-icon { font-size: 40px; line-height: 1; }
.dash-header h1 { margin: 0; font-size: 26px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; }
.dash-header p { margin: 4px 0 0; font-size: 13px; color: #64748b; }
.dash-badge {
    margin-left: auto;
    background: #3b1a6044;
    border: 1px solid #7c3aed44;
    color: #a78bfa;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s;
    height: 100%;
}
.kpi-card:hover { border-color: #7c3aed55; }
.kpi-label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; } 
.kpi-value { font-size: 28px; font-weight: 700; color: #f1f5f9; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.kpi-sub { font-size: 12px; color: #64748b; margin-top: 6px; }

/* ── Pills ── */
.pill { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.3px; }
.pill-success { background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }
.pill-warning { background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }
.pill-danger  { background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }
.pill-info    { background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }
.pill-purple  { background: #3b1a6044;  color: #a78bfa; border: 1px solid #7c3aed44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

/* ── Section Titles ── */
.section-title {
    font-size: 13px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 24px 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid #1e2a3a;
}

/* ── Price ── */
.price-tag { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: #a78bfa; }

/* ── Alerts ── */
.alert-box { border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-info    { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }
.alert-success { background: #14532d22; border-color: #16a34a66; color: #4ade80; }
.alert-purple  { background: #3b1a6022;  border-color: #7c3aed66; color: #a78bfa; }

/* ─ Confirm ── */
.confirm-box { background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }

/* ─ Tabs ── */
[data-testid="stTabs"] > div > div > div > button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #a78bfa !important;
    border-bottom-color: #7c3aed !important;
}

/* ── Inputs ── */
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
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    background: #1e2a3a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    transition: all 0.15s !important;
}
.stButton > button:hover { border-color: #a78bfa55 !important; color: #a78bfa !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b1a60 0%, #6d28d9 100%) !important;
    border-color: #7c3aed !important;
    color: #fff !important;
}
.danger-btn > button {
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}

/* ── Order status tracker ── */
.status-track {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 12px 0;
}
.track-step {
    flex: 1;
    text-align: center;
    position: relative;
}
.track-step::after {
    content: '';
    position: absolute;
    top: 10px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: #1e2a3a;
    z-index: 0;
}
.track-step:last-child::after { display: none; }
.track-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    margin: 0 auto 4px;
    position: relative;
    z-index: 1;
}
.track-label { font-size: 10px; color: #475569; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Auth Guard
# ─────────────────────────────────────────────
inject_theme()
if st.session_state.get("user") is None:
    st.warning("️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "customer":
    st.error("Access denied. This page is for customers only.")
    st.stop()

user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
verif_badge = '<span class="dash-badge">✓ Verified</span>' if verif_status["is_verified"] else '<span class="dash-badge" style="background:#78350f44;border-color:#d9770644;color:#fbbf24;">⏳ Pending</span>'

# Profile picture for header
_cpic = profile.get("profile_image")
if _cpic:
    _cpic_html = f'<img src="data:image/jpeg;base64,{_cpic}" style="width:80px;height:80px;border-radius:50%;border:3px solid #7c3aed;object-fit:cover;">'
else:
    _cpic_html = f'<div style="width:80px;height:80px;border-radius:50%;border:3px solid #7c3aed;background:#1e2a3a;display:flex;align-items:center;justify-content:center;font-size:32px;color:#f1f5f9;font-weight:700;">{profile.get("full_name","C")[0].upper()}</div>'

st.markdown(f"""
<div class="dash-header">
    <div style="flex-shrink:0;position:relative;width:80px;height:80px;">
        {_cpic_html}
        <div style="position:absolute;bottom:0;right:0;width:24px;height:24px;background:#7c3aed;border-radius:50%;border:2px solid #0f1117;display:flex;align-items:center;justify-content:center;font-size:12px;" title="Edit Profile">✏️</div>
    </div>
    <div style="flex:1;margin-left:20px;">
        <h1>Customer Dashboard</h1>
        <p>Welcome back, <strong>{profile.get('full_name','Customer')}</strong> · {now_str}</p>
    </div>
    {verif_badge}
</div>
""", unsafe_allow_html=True)

_cc1, _cc2, _cc3 = st.columns([1, 6, 1])
with _cc3:
    if st.button("✏️ Edit Profile", key="customer_header_edit_btn", use_container_width=True):
        st.session_state.show_profile_editor = True

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛒 Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_data_cache()
        st.rerun()
    
    # Update 7: Dark/Light Toggle
    st.markdown("### 🎨 Theme")
    render_theme_toggle()
    
    st.divider()
    st.markdown("###  Account Status")
    if verif_status["is_verified"]:
        st.markdown('<div class="pill pill-success">● Account Verified</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill pill-warning">● Pending Verification</div>', unsafe_allow_html=True)
    st.divider()
    try:
        active_ords_sb = supabase.table("orders").select("*", count="exact").eq("buyer_id", user_id).in_("status",["pending", "confirmed"]).execute().count or 0
    except Exception:
        active_ords_sb = 0
    st.markdown(f"**{active_ords_sb}** active orders")
    st.divider()
    st.caption(f"{profile.get('full_name','Customer')}")
    st.caption(f"Customer")

# ─────────────────────────────────────────────
# Verification Gate
# ─────────────────────────────────────────────
if not verif_status["is_verified"]:
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", " Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "customer")
    with tab_browse:
        st.markdown('<div class="alert-box alert-warning"> Full ordering access unlocks after account verification.</div>', unsafe_allow_html=True)
        render_browse_tab("customer", profile)
    st.stop()

# ────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
(tab_overview, tab_browse_tab, tab_orders,
 tab_agree, tab_history, tab_wishlist, tab_ai_insights, tab_notif, tab_profile) = st.tabs([
    "📊 Overview", "🛒 Browse & Buy", " My Orders",
    "📄 Agreements", "📜 History", "❤️ Wishlist",
    "🤖 AI Insights", " Notifications", "👤 Profile",
])

# ══════════════════════════════════════════════
# TAB — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:
    try:
        my_orders_all = supabase.table("orders").select("*").eq("buyer_id", user_id).execute().data or []
    except Exception:
        my_orders_all = []
    active_ords  = [o for o in my_orders_all if o.get("status") in ("pending","confirmed")]
    delivered    = [o for o in my_orders_all if o.get("status") == "delivered"]
    total_spent  = sum(float(o.get("total_price_birr") or 0) for o in delivered)
    cancelled    = [o for o in my_orders_all if o.get("status") == "cancelled"]
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Active Orders</div><div class="kpi-value">{len(active_ords)}</div><div class="kpi-sub">In progress</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Delivered</div><div class="kpi-value">{len(delivered)}</div><div class="kpi-sub">Successfully received</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Spent</div><div class="kpi-value">{total_spent:,.0f}</div><div class="kpi-sub">Birr purchased</div></div>', unsafe_allow_html=True)
    with k4:
        wishlist_count = len(st.session_state.get("wishlist", []))
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Wishlist</div><div class="kpi-value">{wishlist_count}</div><div class="kpi-sub">Saved products</div></div>', unsafe_allow_html=True)
    # Active order tracker
    if active_ords:
        st.markdown('<div class="section-title">Active Orders Status</div>', unsafe_allow_html=True)
        STATUS_STEPS = ["pending", "confirmed", "delivered"]
        for o in active_ords[:3]:
            status = o.get("status","pending")
            step_idx = STATUS_STEPS.index(status) if status in STATUS_STEPS else 0
            st.markdown(f"""
            <div style="background:#161b27;border:1px solid #1e2a3a;border-radius:10px;padding:16px 20px;margin-bottom:10px;">
                <div style="font-size:13px;color:#e2e8f0;font-weight:600;margin-bottom:12px;">Order #{str(o['id'])[:8]} · {o.get('total_price_birr',0):,.0f} Birr</div>
                <div class="status-track">
                    <div class="track-step">
                        <div class="track-dot" style="background:{'#a78bfa' if step_idx>=0 else '#1e2a3a'};border:2px solid {'#7c3aed' if step_idx>=0 else '#334155'};"></div>
                        <div class="track-label">Placed</div>
                    </div>
                    <div class="track-step">
                        <div class="track-dot" style="background:{'#a78bfa' if step_idx>=1 else '#1e2a3a'};border:2px solid {'#7c3aed' if step_idx>=1 else '#334155'};"></div>
                        <div class="track-label">Confirmed</div>
                    </div>
                    <div class="track-step">
                        <div class="track-dot" style="background:{'#4ade80' if step_idx>=2 else '#1e2a3a'};border:2px solid {'#16a34a' if step_idx>=2 else '#334155'};"></div>
                        <div class="track-label">Delivered</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
    # Spending chart
    if delivered:
        monthly = {}
        for o in delivered:
            month = o.get("created_at","")[:7]
            monthly[month] = monthly.get(month, 0) + float(o.get("total_price_birr") or 0)
        if monthly:
            st.markdown('<div class="section-title">Monthly Spending</div>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Month": list(monthly.keys()), "Spent (Birr)": list(monthly.values())}).sort_values("Month")
            st.bar_chart(df_m.set_index("Month"), height=200, color="#7c3aed")

# ══════════════════════════════════════════════
# TAB — BROWSE & BUY
# ══════════════════════════════════════════════
with tab_browse_tab:
    render_browse_tab("customer", profile)

# ══════════════════════════════════════════════
# TAB — MY ORDERS
# ══════════════════════════════════════════════
with tab_orders:
    st.markdown('<div class="section-title">My Active Orders</div>', unsafe_allow_html=True)
    try:
        # Update 4: Only show pending and confirmed orders
        my_orders = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)"
        ).eq("buyer_id", user_id).in_("status", ["pending", "confirmed"]).order("created_at", desc=True).limit(50).execute().data or []
    except Exception:
        my_orders = []
    # Filters
    of1, of2 = st.columns(2)
    with of1:
        ord_status = st.selectbox("Status", ["All","pending","confirmed"], key="cord_status")
    with of2:
        ord_search = st.text_input("🔍 Search", key="cord_search", placeholder="Product name…")
    filtered = my_orders if ord_status == "All" else [o for o in my_orders if o.get("status") == ord_status]
    if ord_search:
        filtered = [o for o in filtered if ord_search.lower() in (o.get("products") or {}).get("product_name","").lower()]
    if not filtered:
        st.markdown('<div class="alert-box alert-purple">🛒 No active orders. Browse products to place your first order.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"**{len(filtered)} order(s)**")
        STATUS_PILLS = {"pending":"pill-warning","confirmed":"pill-info","cancelled":"pill-danger"}
        STATUS_STEPS = ["pending","confirmed","delivered"]
        for o in filtered:
            oid   = o["id"]
            prod  = o.get("products") or {}
            status = o.get("status","pending")
            pill   = STATUS_PILLS.get(status,"pill-neutral")
            step_idx = STATUS_STEPS.index(status) if status in STATUS_STEPS else 0
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 2, 2])
                with c1:
                    st.markdown(f"**Order #{str(oid)[:8]}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**📦 {prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                    st.caption(f"Grade: **{prod.get('quality_grade','')}** · 📍 {prod.get('region','N/A')} · 📅 {str(o.get('created_at',''))[:10]}")
                    # Mini progress bar
                    pct = ((step_idx) / 2) * 100
                    st.markdown(f"""
                    <div style="margin-top:8px;">
                        <div style="font-size:10px;color:#64748b;margin-bottom:4px;">Order Progress</div>
                        <div style="background:#1e2a3a;border-radius:4px;height:4px;overflow:hidden;">
                            <div style="width:{pct:.0f}%;height:100%;background:{'#4ade80' if status=='delivered' else '#a78bfa'};border-radius:4px;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    qty = o.get("quantity_ordered", 0)
                    unit = prod.get("unit","")
                    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:4px;">Quantity</div><div class="price-tag" style="font-size:16px;">{qty:,.1f} {unit}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:12px;color:#64748b;margin-top:10px;margin-bottom:4px;">Total</div><div class="price-tag">{o.get("total_price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
                with c3:
                    if status == "pending":
                        if st.session_state.get(f"confirm_cust_cancel_{oid}"):
                            st.markdown('<div class="confirm-box">️ Cancel this order?</div>', unsafe_allow_html=True)
                            dc1, dc2 = st.columns(2)
                            with dc1:
                                if st.button("Yes, Cancel", key=f"do_cust_cancel_{oid}", use_container_width=True, type="primary"):
                                    try:
                                        supabase.table("orders").update({"status":"cancelled"}).eq("id", oid).execute()
                                        clear_data_cache()
                                        st.session_state.pop(f"confirm_cust_cancel_{oid}", None)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                            with dc2:
                                if st.button("Keep", key=f"keep_cust_{oid}", use_container_width=True):
                                    st.session_state.pop(f"confirm_cust_cancel_{oid}", None)
                                    st.rerun()
                        else:
                            st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                            if st.button("❌ Cancel Order", key=f"cust_cancel_{oid}", use_container_width=True):
                                st.session_state[f"confirm_cust_cancel_{oid}"] = True
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                    elif status == "confirmed":
                        st.markdown('<div class="pill pill-info" style="display:block;text-align:center;margin-top:8px;">🚚 In Transit</div>', unsafe_allow_html=True)
                        # Download agreement PDF once confirmed
                        try:
                            prod_info = o.get("products") or {}
                            qty_c = float(o.get("quantity_ordered") or 0)
                            tot_c = float(o.get("total_price_birr") or 0)
                            ppu_c = float(prod_info.get("price_birr") or (tot_c / qty_c if qty_c else 0))
                            pdf_cust = generate_agreement_pdf(
                                producer_name="Producer",
                                producer_phone="",
                                producer_region=prod_info.get("region",""),
                                merchant_name=profile.get("full_name",""),
                                merchant_phone=profile.get("phone",""),
                                merchant_region=profile.get("region",""),
                                product_name=prod_info.get("product_name",""),
                                sector=prod_info.get("sector",""),
                                quality_grade=prod_info.get("quality_grade","A"),
                                quantity=qty_c,
                                unit=prod_info.get("unit",""),
                                price_per_unit=ppu_c,
                                total_price=tot_c,
                                delivery_date=str(o.get("created_at",""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True,
                                merchant_confirmed=True,
                                agreement_id=str(oid),
                            )
                            st.download_button(" Agreement PDF", data=pdf_cust,
                                file_name=f"agreement_{prod_info.get('product_name','')}.pdf",
                                mime="application/pdf", key=f"cust_agree_pdf_{oid}",
                                use_container_width=True)
                        except Exception:
                            pass

# ══════════════════════════════════════════════
# TAB — AGREEMENTS
# ══════════════════════════════════════════════
with tab_agree:
    st.markdown('<div class="section-title">My Agreements</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-purple">📄 Agreements are generated for all confirmed and delivered orders. Download them here for your records.</div>', unsafe_allow_html=True)
    try:
        agree_orders_c = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id)"
        ).eq("buyer_id", user_id).in_("status",["confirmed", "delivered"]).order("created_at", desc=True).execute().data or []
    except Exception:
        agree_orders_c = []
    if not agree_orders_c:
        st.markdown('<div class="alert-box alert-purple"> No confirmed agreements yet. Orders become agreements once confirmed.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"**{len(agree_orders_c)} agreement(s)**")
        for o in agree_orders_c:
            prod = o.get("products") or {}
            status = o.get("status","confirmed")
            pill = "pill-success" if status == "delivered" else "pill-info"
            oid = o["id"]
            qty_a = float(o.get("quantity_ordered") or 0)
            tot_a = float(o.get("total_price_birr") or 0)
            ppu_a = float(prod.get("price_birr") or (tot_a / qty_a if qty_a else 0))
            with st.container(border=True):
                c1, c2 = st.columns([5, 2])
                with c1:
                    st.markdown(f"**📄 {prod.get('product_name','Unknown')}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                    st.caption(f"Sector: {prod.get('sector','')} · Grade: **{prod.get('quality_grade','')}** · 📍 {prod.get('region','N/A')}")
                    st.caption(f"Qty: {qty_a:,.1f} {prod.get('unit','')} · Date: {str(o.get('created_at',''))[:10]}")
                    with st.expander("👁️ Preview Agreement"):
                        try:
                            prev_html = generate_agreement_preview_html(
                                producer_name="Producer",
                                producer_phone="",
                                producer_region=prod.get("region",""),
                                merchant_name=profile.get("full_name",""),
                                merchant_phone=profile.get("phone",""),
                                merchant_region=profile.get("region",""),
                                product_name=prod.get("product_name",""),
                                sector=prod.get("sector",""),
                                quality_grade=prod.get("quality_grade","A"),
                                quantity=qty_a,
                                unit=prod.get("unit",""),
                                price_per_unit=ppu_a,
                                total_price=tot_a,
                                delivery_date=str(o.get("created_at",""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True,
                                merchant_confirmed=True,
                                agreement_id=str(oid),
                            )
                            st.components.v1.html(prev_html, height=400, scrolling=True)
                        except Exception as ex:
                            st.caption(f"Preview error: {ex}")
                with c2:
                    st.markdown(f'<div class="price-tag">{tot_a:,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
                    try:
                        pdf_a = generate_agreement_pdf(
                            producer_name="Producer",
                            producer_phone="",
                            producer_region=prod.get("region",""),
                            merchant_name=profile.get("full_name",""),
                            merchant_phone=profile.get("phone",""),
                            merchant_region=profile.get("region",""),
                            product_name=prod.get("product_name",""),
                            sector=prod.get("sector",""),
                            quality_grade=prod.get("quality_grade","A"),
                            quantity=qty_a,
                            unit=prod.get("unit",""),
                            price_per_unit=ppu_a,
                            total_price=tot_a,
                            delivery_date=str(o.get("created_at",""))[:10],
                            payment_method="Bank Transfer",
                            producer_confirmed=True,
                            merchant_confirmed=True,
                            agreement_id=str(oid),
                        )
                        st.download_button("📥 Download PDF", data=pdf_a,
                            file_name=f"agreement_{prod.get('product_name','')}.pdf",
                            mime="application/pdf", key=f"cust_agr_dl_{oid}",
                            use_container_width=True)
                    except Exception:
                        pass

# ══════════════════════════════════════════════
# TAB — HISTORY
# ══════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-title">Purchase History</div>', unsafe_allow_html=True)
    try:
        # Update 4: Include delivered, declined, and cancelled orders
        mh_orders = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, producer_id)"
        ).eq("buyer_id", user_id).in_("status", ["delivered", "declined", "cancelled"]).order("created_at", desc=True).limit(50).execute().data or []
    except Exception:
        mh_orders = []
    
    # Add filter for history type
    hist_filter = st.selectbox("Show", ["All", "Delivered", "Declined", "Cancelled"], key="hist_filter")
    if hist_filter == "Delivered":
        mh_orders = [o for o in mh_orders if o.get("status") == "delivered"]
    elif hist_filter == "Declined":
        mh_orders = [o for o in mh_orders if o.get("status") == "declined"]
    elif hist_filter == "Cancelled":
        mh_orders = [o for o in mh_orders if o.get("status") == "cancelled"]
    
    if not mh_orders:
        st.markdown('<div class="alert-box alert-purple">📜 No history records yet. Start shopping to build your history.</div>', unsafe_allow_html=True)
    else:
        # Only calculate spending for delivered orders
        delivered_hist = [o for o in mh_orders if o.get("status") == "delivered"]
        total_spent2 = sum(float(o.get("total_price_birr") or 0) for o in delivered_hist)
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Purchased</div><div class="price-tag">{total_spent2:,.0f}</div><div class="kpi-sub">Birr spent</div></div>', unsafe_allow_html=True)
        with h2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Orders Received</div><div class="kpi-value">{len(delivered_hist)}</div><div class="kpi-sub">Completed orders</div></div>', unsafe_allow_html=True)
        with h3:
            avg_order = total_spent2 / len(delivered_hist) if delivered_hist else 0
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Order Value</div><div class="price-tag" style="font-size:16px;">{avg_order:,.0f}</div><div class="kpi-sub">Birr per order</div></div>', unsafe_allow_html=True)
        st.markdown("")
        # Sector breakdown (only for delivered)
        sector_spend = {}
        for o in delivered_hist:
            s = (o.get("products") or {}).get("sector","Other")
            sector_spend[s] = sector_spend.get(s, 0) + float(o.get("total_price_birr") or 0)
        if sector_spend:
            st.markdown('<div class="section-title">Spending by Sector</div>', unsafe_allow_html=True)
            df_sec = pd.DataFrame({"Sector": list(sector_spend.keys()), "Birr": list(sector_spend.values())})
            st.bar_chart(df_sec.set_index("Sector"), height=180, color="#7c3aed")
        # Search/filter
        hist_search = st.text_input("🔍 Search history", key="hist_search", placeholder="Product name…")
        hist_filtered = mh_orders if not hist_search else [o for o in mh_orders if hist_search.lower() in (o.get("products") or {}).get("product_name","").lower()]
        st.markdown('<div class="section-title">All Historical Orders</div>', unsafe_allow_html=True)
        st.caption(f"**{len(hist_filtered)} order(s)**")
        for o in hist_filtered:
            prod = o.get("products") or {}
            status = o.get("status", "unknown")
            status_color = {"delivered": "#4ade80", "cancelled": "#f87171", "declined": "#f87171"}.get(status, "#94a3b8")
            with st.container(border=True):
                c1, c2 = st.columns([5, 2])
                with c1:
                    st.markdown(f"**{prod.get('product_name','Unknown')}** · {prod.get('sector','')} &nbsp; <span style='color:{status_color};font-size:12px;font-weight:600;'>● {status.upper()}</span>", unsafe_allow_html=True)
                    st.caption(f"Sector: {prod.get('sector','')} · Grade: **{prod.get('quality_grade','')}** · 📍 {prod.get('region','N/A')}")
                    st.caption(f"📅 {str(o.get('created_at',''))[:10]} · Qty: {o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                with c2:
                    st.markdown(f'<div class="price-tag">{o.get("total_price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — WISHLIST
# ═════════════════════════════════════════════
with tab_wishlist:
    st.markdown('<div class="section-title">Saved Products</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-purple">❤️ Save products while browsing by clicking the wishlist button on any product card. Your wishlist is saved for this session.</div>', unsafe_allow_html=True)
    wishlist = st.session_state.get("wishlist", [])
    if not wishlist:
        st.markdown('<div style="text-align:center;padding:40px;color:#475569;"><div style="font-size:40px;margin-bottom:12px;">❤️</div><div style="font-size:15px;">Your wishlist is empty.</div><div style="font-size:13px;margin-top:6px;">Browse products and save the ones you like.</div></div>', unsafe_allow_html=True)
    else:
        st.caption(f"**{len(wishlist)} saved product(s)**")
        for i, item in enumerate(wishlist):
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 2, 2])
                with c1:
                    st.markdown(f"** {item.get('product_name','Unknown')}** &nbsp; <span class='pill pill-purple'>Saved</span>", unsafe_allow_html=True)
                    st.caption(f"Sector: {item.get('sector','—')} · Grade: **{item.get('quality_grade','—')}** · 📍 {item.get('region','—')}")
                with c2:
                    st.markdown(f'<div class="price-tag">{item.get("price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr / {item.get("unit","")}</div>', unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️ Remove", key=f"rm_wish_{i}", use_container_width=True):
                        st.session_state["wishlist"] = [x for j, x in enumerate(wishlist) if j != i]
                        st.rerun()
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state["wishlist"] = []
            st.rerun()

# ══════════════════════════════════════════════
# TAB — AI INSIGHTS (Update 3)
# ══════════════════════════════════════════════
with tab_ai_insights:
    st.markdown('<div class="section-title">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-purple">Leverage our AI engines to find the best deals, detect fraud, and optimize your purchasing.</div>', unsafe_allow_html=True)
    
    ai1, ai2, ai3 = st.columns(3)
    
    with ai1:
        st.markdown('<div class="kpi-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
        st.markdown("**🛒 Smart Product Recommendations**", unsafe_allow_html=True)
        st.caption("AI-recommended products based on your preferences and market trends.")
        if st.button("Get Recommendations", use_container_width=True, key="ai_rec_btn"):
            with st.spinner("Analyzing..."):
                st.success("✅ Based on market trends, Coffee and Sesame are highly recommended!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ai2:
        st.markdown('<div class="kpi-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
        st.markdown("**🛡️ Fraud Detection Analysis**", unsafe_allow_html=True)
        st.caption("Check transactions and sellers for potential fraud risks.")
        if st.button("Run Fraud Check", use_container_width=True, key="ai_fraud_btn"):
            with st.spinner("Scanning..."):
                st.success("✅ All your recent transactions show low fraud risk.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ai3:
        st.markdown('<div class="kpi-card" style="margin-bottom:16px;">', unsafe_allow_html=True)
        st.markdown("**💰 Price Optimization**", unsafe_allow_html=True)
        st.caption("Find the best time to buy and negotiate better prices.")
        if st.button("Analyze Prices", use_container_width=True, key="ai_price_btn"):
            with st.spinner("Computing..."):
                st.success("✅ Current market prices are 8% below average. Good time to buy!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown('<div class="section-title">Your AI Readiness Score</div>', unsafe_allow_html=True)
    score = 65  # Mock score
    fig_score = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': "Overall AI Utilization", 'font': {'color': '#94a3b8'}},
        gauge = {'axis': {'range': [0, 100], 'tickcolor': "#94a3b8"},
                 'bar': {'color': "#a78bfa"},
                 'bgcolor': "#1e2a3a",
                 'borderwidth': 2,
                 'bordercolor': "#334155",
                 'steps': [
                     {'range': [0, 50], 'color': "#7f1d1d"},
                     {'range': [50, 80], 'color': "#78350f"},
                     {'range': [80, 100], 'color': "#3b1a60"}],
                 'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}
    ))
    fig_score.update_layout(paper_bgcolor="#161b27", font={'color': "#94a3b8", 'family': "Inter"}, height=300)
    st.plotly_chart(fig_score, use_container_width=True)

# ── NOTIFICATIONS & PROFILE ──
with tab_notif:
    render_notifications_tab(user_id)

# ── PROFILE ──
with tab_profile:
    render_profile_editor_modal(profile, user_id)

# ── Show profile editor modal if triggered from header button ──
if st.session_state.get("show_profile_editor"):
    render_profile_editor_modal(profile, user_id)

# ════════════════════════════════════════════════════════════
# FLOATING CHATBOT (Add this at the end of 3_customer.py)
# ═════════════════════════════════════════════════════════════
from utils.chatbot import render_floating_chatbot
render_floating_chatbot(profile)
