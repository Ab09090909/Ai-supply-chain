"""Merchant Dashboard — Professional dark design matching Admin panel."""
import sys
import os
import datetime
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme
from utils.constants import REGIONS, SECTORS
from utils.db_helpers import supabase, cached_query, clear_data_cache, send_notification
from utils.verification import check_verification_status, render_document_upload
from utils.shared_ui import render_browse_tab, render_notifications_tab, render_profile_edit_tab
from utils.pdf_generator import generate_agreement_pdf

# ─────────────────────────────────────────────
# Page Config + CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Merchant Dashboard",
    page_icon="🏬",
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

.dash-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f1117 60%, #16213e 100%);
    border: 1px solid #2a2a5a;
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
    background: #1e3a5f44;
    border: 1px solid #2563eb44;
    color: #60a5fa;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.kpi-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s;
    height: 100%;
}
.kpi-card:hover { border-color: #2563eb55; }
.kpi-label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #f1f5f9; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.kpi-sub { font-size: 12px; color: #64748b; margin-top: 6px; }

.pill { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; letter-spacing: 0.3px; }
.pill-success { background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }
.pill-warning { background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }
.pill-danger  { background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }
.pill-info    { background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

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

.price-tag { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: #60a5fa; }

.alert-box { border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-info    { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }
.alert-success { background: #14532d22; border-color: #16a34a66; color: #4ade80; }
.alert-danger  { background: #7f1d1d22; border-color: #ef444466; color: #f87171; }

.confirm-box { background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }

[data-testid="stTabs"] > div > div > div > button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom-color: #2563eb !important;
}

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

.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
    background: #1e2a3a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
}
.stButton > button:hover { border-color: #60a5fa55 !important; color: #60a5fa !important; }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%) !important;
    border-color: #2563eb !important;
    color: #fff !important;
}
.danger-btn > button {
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}

/* Fraud risk badge colours */
.fraud-low  { color: #4ade80; font-weight: 600; font-size: 12px; }
.fraud-med  { color: #fbbf24; font-weight: 600; font-size: 12px; }
.fraud-high { color: #f87171; font-weight: 600; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Auth Guard
# ─────────────────────────────────────────────
inject_theme()

if st.session_state.get("user") is None:
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "merchant":
    st.error("Access denied. This page is for merchants only.")
    st.stop()

user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
verif_badge = '<span class="dash-badge">✓ Verified</span>' if verif_status["is_verified"] else '<span class="dash-badge" style="background:#78350f44;border-color:#d9770644;color:#fbbf24;">⏳ Pending</span>'
st.markdown(f"""
<div class="dash-header">
    <div class="dash-header-icon">🏬</div>
    <div>
        <h1>Merchant Dashboard</h1>
        <p>Welcome back, <strong>{profile.get('full_name','Merchant')}</strong> · 📍 {profile.get('region','N/A')} · {now_str}</p>
    </div>
    {verif_badge}
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏬 Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        clear_data_cache()
        st.rerun()
    st.divider()
    st.markdown("### 📌 Account Status")
    if verif_status["is_verified"]:
        st.markdown('<div class="pill pill-success">● Account Verified</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pill pill-warning">● Pending Verification</div>', unsafe_allow_html=True)
    st.divider()
    try:
        active_orders_sidebar = supabase.table("orders").select("*", count="exact").eq("buyer_id", user_id).in_("status",["pending","confirmed"]).execute().count or 0
    except Exception:
        active_orders_sidebar = 0
    st.markdown(f"**{active_orders_sidebar}** active orders")
    st.divider()
    st.caption(f"**{profile.get('full_name','Merchant')}**")
    st.caption(f"Merchant · {profile.get('region','')}")

# ─────────────────────────────────────────────
# Verification Gate
# ─────────────────────────────────────────────
if not verif_status["is_verified"]:
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "merchant")
    with tab_browse:
        st.markdown('<div class="alert-box alert-warning">⏳ Full access unlocks after account verification.</div>', unsafe_allow_html=True)
        render_browse_tab("merchant", profile)
    st.stop()

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
(tab_overview, tab_browse_tab, tab_orders, tab_agree,
 tab_history, tab_pref, tab_notif, tab_profile) = st.tabs([
    "📊 Overview", "🛒 Browse & Order", "📋 My Orders",
    "📄 Agreements", "📜 History", "⚙️ Preferences",
    "🔔 Notifications", "👤 Profile",
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
    pending_agree = sum(1 for o in my_orders_all if o.get("producer_confirmed") and not o.get("merchant_confirmed"))

    if pending_agree > 0:
        st.markdown(f'<div class="alert-box alert-warning">📄 <strong>{pending_agree} agreement(s)</strong> from producers are waiting for your response.</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Active Orders</div><div class="kpi-value">{len(active_ords)}</div><div class="kpi-sub">Pending & confirmed</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Completed</div><div class="kpi-value">{len(delivered)}</div><div class="kpi-sub">Delivered orders</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Spent</div><div class="kpi-value">{total_spent:,.0f}</div><div class="kpi-sub">Birr purchased</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Pending Agreements</div><div class="kpi-value">{pending_agree}</div><div class="kpi-sub">Awaiting your response</div></div>', unsafe_allow_html=True)

    # Monthly spending chart
    if delivered:
        monthly = {}
        for o in delivered:
            month = o.get("created_at","")[:7]
            monthly[month] = monthly.get(month, 0) + float(o.get("total_price_birr") or 0)
        if monthly:
            st.markdown('<div class="section-title">Monthly Spending</div>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Month": list(monthly.keys()), "Spent": list(monthly.values())}).sort_values("Month")
            st.bar_chart(df_m.set_index("Month"), height=200, color="#2563eb")

    # Recent activity
    if my_orders_all:
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        for o in sorted(my_orders_all, key=lambda x: x.get("created_at",""), reverse=True)[:5]:
            status = o.get("status","pending")
            color = {"pending":"#fbbf24","confirmed":"#60a5fa","delivered":"#4ade80","cancelled":"#f87171"}.get(status,"#94a3b8")
            ts = o.get("created_at","")[:16].replace("T"," ")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #1e2a3a;">
                <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;margin-top:2px;"></div>
                <div>
                    <div style="font-size:13px;color:#94a3b8;">Order <strong style="color:#e2e8f0;">#{str(o['id'])[:8]}</strong> — {status.capitalize()} · {o.get('total_price_birr',0):,.0f} Birr</div>
                    <div style="font-size:11px;color:#475569;">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — BROWSE & ORDER
# ══════════════════════════════════════════════
with tab_browse_tab:
    render_browse_tab("merchant", profile)

# ══════════════════════════════════════════════
# TAB — MY ORDERS
# ══════════════════════════════════════════════
with tab_orders:
    st.markdown('<div class="section-title">Active Orders</div>', unsafe_allow_html=True)
    try:
        my_orders = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)"
        ).eq("buyer_id", user_id).neq("status","delivered").order("created_at", desc=True).limit(50).execute().data or []
    except Exception as e:
        st.error(f"Could not load orders: {e}")
        my_orders = []

    # Filters
    of1, of2 = st.columns(2)
    with of1:
        ord_status = st.selectbox("Status", ["All","pending","confirmed","cancelled"], key="mord_status")
    with of2:
        ord_search = st.text_input("🔍 Search", key="mord_search", placeholder="Product name…")

    filtered_orders = my_orders if ord_status == "All" else [o for o in my_orders if o.get("status") == ord_status]
    if ord_search:
        filtered_orders = [o for o in filtered_orders if ord_search.lower() in (o.get("products") or {}).get("product_name","").lower()]

    if not filtered_orders:
        st.markdown('<div class="alert-box alert-info">📋 No active orders. Browse products to place your first order.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"**{len(filtered_orders)} order(s)**")
        STATUS_PILLS = {"pending":"pill-warning","confirmed":"pill-info","cancelled":"pill-danger"}
        for o in filtered_orders:
            oid   = o["id"]
            prod  = o.get("products") or {}
            status = o.get("status","pending")
            pill   = STATUS_PILLS.get(status,"pill-neutral")
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 2, 2])
                with c1:
                    st.markdown(f"**Order #{str(oid)[:8]}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**📦 {prod.get('product_name','Unknown')}** · {prod.get('sector','')} · Grade **{prod.get('quality_grade','')}**")
                    st.caption(f"📍 {prod.get('region','N/A')} · 📅 {str(o.get('created_at',''))[:10]}")
                with c2:
                    st.markdown(f'<div class="price-tag" style="font-size:16px;">{o.get("quantity_ordered",0):,.1f}</div><div style="font-size:11px;color:#64748b;">{prod.get("unit","")}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="price-tag" style="margin-top:10px;">{o.get("total_price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr total</div>', unsafe_allow_html=True)
                with c3:
                    if status == "pending":
                        if st.button("❌ Cancel Order", key=f"m_cancel_{oid}", use_container_width=True):
                            if st.session_state.get(f"confirm_cancel_mord_{oid}"):
                                try:
                                    supabase.table("orders").update({"status":"cancelled"}).eq("id", oid).execute()
                                    clear_data_cache()
                                    st.session_state.pop(f"confirm_cancel_mord_{oid}", None)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")
                            else:
                                st.session_state[f"confirm_cancel_mord_{oid}"] = True
                                st.rerun()
                        if st.session_state.get(f"confirm_cancel_mord_{oid}"):
                            st.markdown('<div class="confirm-box">⚠️ Cancel this order?</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — AGREEMENTS
# ══════════════════════════════════════════════
with tab_agree:
    st.markdown('<div class="section-title">Agreement Requests from Producers</div>', unsafe_allow_html=True)
    try:
        producer_requests = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)"
        ).eq("buyer_id", user_id).eq("producer_confirmed", True).eq("merchant_confirmed", False).execute().data or []
    except Exception:
        producer_requests = []

    if not producer_requests:
        st.markdown('<div class="alert-box alert-info">📄 No pending agreement requests from producers.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-box alert-warning">📩 <strong>{len(producer_requests)} producer(s)</strong> have sent you supply agreement requests.</div>', unsafe_allow_html=True)
        for o in producer_requests:
            oid  = o["id"]
            prod = o.get("products") or {}
            producer_id = prod.get("producer_id")
            with st.container(border=True):
                c1, c2 = st.columns([5, 3])
                with c1:
                    st.markdown(f"**📄 {prod.get('product_name','Unknown')}** &nbsp; <span class='pill pill-warning'>Awaiting Response</span>", unsafe_allow_html=True)
                    st.caption(f"Sector: {prod.get('sector','')} · Grade: **{prod.get('quality_grade','')}** · 📍 {prod.get('region','')}")
                    st.markdown(f'<div style="margin-top:10px;"><span class="price-tag">{o.get("quantity_ordered",0):,.1f} {prod.get("unit","")}</span> &nbsp;&nbsp; <span class="price-tag">{o.get("total_price_birr",0):,.0f} Birr</span></div>', unsafe_allow_html=True)
                with c2:
                    ba1, ba2 = st.columns(2)
                    with ba1:
                        if st.button("✅ Accept", key=f"m_accept_{oid}", type="primary", use_container_width=True):
                            try:
                                supabase.table("orders").update({"merchant_confirmed": True, "status": "confirmed"}).eq("id", oid).execute()
                                if producer_id:
                                    send_notification(producer_id, "🤝 Agreement Accepted", f"Merchant accepted your supply agreement.", "success", order_id=oid)
                                clear_data_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {e}")
                    with ba2:
                        if st.button("❌ Decline", key=f"m_decline_{oid}", use_container_width=True):
                            try:
                                supabase.table("orders").update({"status":"cancelled"}).eq("id", oid).execute()
                                if producer_id:
                                    send_notification(producer_id, "❌ Agreement Declined", "Merchant declined your supply agreement.", "error")
                                clear_data_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {e}")

                    # Preview PDF
                    try:
                        pdf_bytes = generate_agreement_pdf(
                            producer_name="Producer",
                            merchant_name=profile.get("full_name",""),
                            product_name=prod.get("product_name",""),
                            quantity=o.get("quantity_ordered",0),
                            unit=prod.get("unit",""),
                            price=o.get("total_price_birr",0),
                            region=prod.get("region",""),
                        )
                        st.download_button("📥 Preview PDF", data=pdf_bytes,
                            file_name=f"agreement_{prod.get('product_name','')}.pdf",
                            mime="application/pdf", key=f"m_pdf_{oid}")
                    except Exception:
                        pass

    # Confirmed agreements
    st.markdown('<div class="section-title">Confirmed Agreements</div>', unsafe_allow_html=True)
    try:
        confirmed_agrees = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region)"
        ).eq("buyer_id", user_id).eq("merchant_confirmed", True).in_("status",["confirmed","delivered"]).order("created_at", desc=True).execute().data or []
    except Exception:
        confirmed_agrees = []

    if not confirmed_agrees:
        st.markdown('<div class="alert-box alert-info">No confirmed agreements yet.</div>', unsafe_allow_html=True)
    else:
        for o in confirmed_agrees:
            prod   = o.get("products") or {}
            status = o.get("status","confirmed")
            pill   = "pill-success" if status == "delivered" else "pill-info"
            with st.container(border=True):
                c1, c2 = st.columns([5, 2])
                with c1:
                    st.markdown(f"**✅ {prod.get('product_name','Unknown')}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                    st.caption(f"Grade: **{prod.get('quality_grade','')}** · Sector: {prod.get('sector','')} · 📍 {prod.get('region','')}")
                    st.caption(f"Qty: {o.get('quantity_ordered',0):,.1f} {prod.get('unit','')} · Date: {str(o.get('created_at',''))[:10]}")
                with c2:
                    st.markdown(f'<div class="price-tag">{o.get("total_price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — HISTORY
# ══════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-title">Purchase History</div>', unsafe_allow_html=True)
    try:
        mh_orders = supabase.table("orders").select(
            "*, products(product_name, sector, quality_grade, unit, region, producer_id)"
        ).eq("buyer_id", user_id).eq("status","delivered").order("created_at", desc=True).execute().data or []
    except Exception:
        mh_orders = []

    if not mh_orders:
        st.markdown('<div class="alert-box alert-info">📜 No delivered orders yet.</div>', unsafe_allow_html=True)
    else:
        total_spent2 = sum(float(o.get("total_price_birr") or 0) for o in mh_orders)
        h1, h2 = st.columns(2)
        with h1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Purchased</div><div class="price-tag">{total_spent2:,.0f}</div><div class="kpi-sub">Birr spent</div></div>', unsafe_allow_html=True)
        with h2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Completed Orders</div><div class="kpi-value">{len(mh_orders)}</div><div class="kpi-sub">Received successfully</div></div>', unsafe_allow_html=True)
        st.markdown("")

        # Sector breakdown
        sector_spend = {}
        for o in mh_orders:
            s = (o.get("products") or {}).get("sector","Other")
            sector_spend[s] = sector_spend.get(s, 0) + float(o.get("total_price_birr") or 0)
        if sector_spend:
            st.markdown('<div class="section-title">Spending by Sector</div>', unsafe_allow_html=True)
            df_sec = pd.DataFrame({"Sector": list(sector_spend.keys()), "Spent (Birr)": list(sector_spend.values())})
            st.bar_chart(df_sec.set_index("Sector"), height=200, color="#2563eb")

        st.markdown('<div class="section-title">All Delivered Orders</div>', unsafe_allow_html=True)
        for o in mh_orders:
            prod = o.get("products") or {}
            with st.container(border=True):
                c1, c2 = st.columns([5, 2])
                with c1:
                    st.markdown(f"✅ **{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                    st.caption(f"Grade: **{prod.get('quality_grade','')}** · 📍 {prod.get('region','N/A')} · 📅 {str(o.get('created_at',''))[:10]}")
                    st.caption(f"Qty: {o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                with c2:
                    st.markdown(f'<div class="price-tag">{o.get("total_price_birr",0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — PREFERENCES
# ══════════════════════════════════════════════
with tab_pref:
    st.markdown('<div class="section-title">Buying Preferences</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">💡 Your preferences help the AI matching engine recommend the best products and producers for your business.</div>', unsafe_allow_html=True)

    try:
        pref_res = supabase.table("merchant_preferences").select("*").eq("merchant_id", user_id).execute()
        existing_pref = pref_res.data[0] if pref_res.data else None
    except Exception:
        existing_pref = None

    with st.container(border=True):
        with st.form("merchant_pref_form"):
            pc1, pc2 = st.columns(2)
            with pc1:
                pref_sectors = st.multiselect(
                    "🏭 Preferred Sectors",
                    SECTORS,
                    default=(existing_pref.get("preferred_sectors") or []) if existing_pref else [],
                    help="Select the agricultural sectors you primarily source from."
                )
                pref_regions = st.multiselect(
                    "📍 Preferred Regions",
                    REGIONS,
                    default=(existing_pref.get("preferred_regions") or []) if existing_pref else [],
                    help="Regions you prefer to source from."
                )
                pref_quality = st.selectbox(
                    "⭐ Minimum Quality Grade",
                    ["Any","A","B","C","Premium","Standard"],
                    index=0,
                    help="Minimum acceptable quality."
                )
            with pc2:
                max_budget = st.number_input(
                    "💰 Max Order Budget (Birr)",
                    min_value=0.0,
                    value=float(existing_pref.get("max_budget_birr") or 50000) if existing_pref else 50000.0,
                    step=1000.0,
                    help="Maximum you'd spend on a single order."
                )
                pref_payment = st.selectbox(
                    "💳 Preferred Payment Method",
                    ["Bank Transfer","Cash on Delivery","Mobile Money","Letter of Credit"],
                    index=["Bank Transfer","Cash on Delivery","Mobile Money","Letter of Credit"].index(existing_pref.get("preferred_payment","Bank Transfer")) if existing_pref and existing_pref.get("preferred_payment") in ["Bank Transfer","Cash on Delivery","Mobile Money","Letter of Credit"] else 0
                )
                needs_delivery = st.checkbox(
                    "🚚 Require Delivery Service",
                    value=bool((existing_pref or {}).get("needs_delivery", False)),
                    help="Show only products with delivery available."
                )

            submitted_pref = st.form_submit_button("💾 Save Preferences", type="primary", use_container_width=True)
            if submitted_pref:
                pref_payload = {
                    "merchant_id": user_id,
                    "preferred_sectors": pref_sectors,
                    "preferred_regions": pref_regions,
                    "max_budget_birr": max_budget,
                    "preferred_payment": pref_payment,
                    "preferred_quality": pref_quality,
                    "needs_delivery": needs_delivery,
                }
                try:
                    if existing_pref:
                        supabase.table("merchant_preferences").update(pref_payload).eq("merchant_id", user_id).execute()
                    else:
                        supabase.table("merchant_preferences").insert(pref_payload).execute()
                    st.success("✅ Preferences saved! AI matching will now use these to recommend products.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")

# ── NOTIFICATIONS & PROFILE ──
with tab_notif:
    render_notifications_tab(user_id)

with tab_profile:
    render_profile_edit_tab(profile, user_id)
