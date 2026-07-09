"""Merchant Dashboard."""
import sys
import os
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
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Merchant Dashboard",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
try:
    from utils.theme import inject_theme
    from utils.shared_ui import render_hamburger_menu
    from utils.constants import REGIONS, SECTORS
    from utils.db_helpers import supabase, cached_query, clear_data_cache, send_notification
    from utils.verification import check_verification_status, render_document_upload
    from utils.pdf_generator import generate_agreement_pdf, generate_agreement_preview_html
    from src.demand_engine import forecast_demand
    from src.fraud_engine import check_fraud_risk
    from src.price_engine import recommend_price
    from src.recommendation_engine import get_recommendations
except ImportError as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "initialized_merchant" not in st.session_state:
    st.session_state.initialized_merchant = True
    st.session_state.m_forecast_result = None
    st.session_state.m_forecast_params = None
    st.session_state.match_results = None
    st.session_state.show_profile_editor = False

# ─────────────────────────────────────────────
# THEME + MENU
# ─────────────────────────────────────────────
inject_theme()

# Merchant-specific accent overrides (blue)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.dash-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f1117 60%, #16213e 100%);
    border: 1px solid #2a2a5a;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
    flex-wrap: wrap;
}
.dash-header h1 { margin: 0; font-size: 26px; font-weight: 700; color: #f1f5f9; }
.dash-header p  { margin: 4px 0 0; font-size: 13px; color: #64748b; }
.dash-badge {
    margin-left: auto;
    background: #1e3a5f44;
    border: 1px solid #2563eb44;
    color: #60a5fa;
    font-size: 11px; font-weight: 600;
    padding: 4px 12px; border-radius: 20px;
    letter-spacing: 0.5px; text-transform: uppercase; white-space: nowrap;
}

.kpi-card {
    background: #161b27; border: 1px solid #1e2a3a;
    border-radius: 10px; padding: 20px 24px;
    transition: border-color 0.2s; height: 100%;
}
.kpi-card:hover { border-color: #2563eb55; }
.kpi-label { font-size: 11px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 700; color: #f1f5f9; font-family: 'JetBrains Mono', monospace; line-height: 1; }
.kpi-sub   { font-size: 12px; color: #64748b; margin-top: 6px; }

.section-title {
    font-size: 13px; font-weight: 700; color: #475569;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 24px 0 14px; padding-bottom: 8px;
    border-bottom: 1px solid #1e2a3a;
}

.price-tag { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; color: #60a5fa; }

.alert-box { border-radius: 8px; padding: 12px 16px; font-size: 13px; margin-bottom: 12px; border: 1px solid; }
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-info    { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }
.alert-success { background: #14532d22; border-color: #16a34a66; color: #4ade80; }
.alert-danger  { background: #7f1d1d22; border-color: #ef444466; color: #f87171; }

.confirm-box { background: #7f1d1d22; border: 1px solid #ef444455; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #fca5a5; margin-bottom: 8px; }

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%) !important;
    border-color: #2563eb !important; color: #fff !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #60a5fa !important; border-bottom-color: #2563eb !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f1117; }
::-webkit-scrollbar-thumb { background: #1e2a3a; border-radius: 3px; }

@media (max-width: 768px) {
    .dash-header { flex-direction: column !important; padding: 16px !important; text-align: center; }
    .kpi-card { padding: 12px !important; }
    div.stButton > button { width: 100%; }
}
</style>
""", unsafe_allow_html=True)

render_hamburger_menu()

# ─────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────
def check_auth() -> bool:
    if st.session_state.get("user") is None:
        st.warning("⚠️ Please sign in first.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
    profile = st.session_state.get("profile")
    if profile is None or profile.get("role") != "merchant":
        st.error("🚫 Access denied. This page is for merchants only.")
        st.page_link("app.py", label="← Go to Login", icon="🔐")
        st.stop()
    return True

check_auth()

# ─────────────────────────────────────────────
# USER DATA
# ─────────────────────────────────────────────
profile  = st.session_state.get("profile", {})
user_id  = st.session_state.user.id
now_str  = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

try:
    verif_status = check_verification_status(user_id)
except Exception:
    verif_status = {}

# Load merchant preferences once at the top so all tabs can use it
existing_pref = None
try:
    pref_res = supabase.table("merchant_preferences").select("*").eq("merchant_id", user_id).execute()
    existing_pref = pref_res.data[0] if pref_res.data else None
except Exception:
    pass

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
verif_badge = (
    '<span class="dash-badge">✓ Verified</span>'
    if verif_status.get("is_verified", False)
    else '<span class="dash-badge" style="background:#78350f44;border-color:#d9770644;color:#fbbf24;">⏳ Pending</span>'
)

name_initial = profile.get("full_name", "M")[0].upper()
avatar_html = f'<div style="width:80px;height:80px;border-radius:50%;border:3px solid #2563eb;background:#1e2a3a;display:flex;align-items:center;justify-content:center;font-size:32px;color:#f1f5f9;font-weight:700;">{name_initial}</div>'

st.markdown(f"""
<div class="dash-header">
    <div style="flex-shrink:0;">{avatar_html}</div>
    <div style="flex:1;margin-left:20px;">
        <h1>🏬 Merchant Dashboard</h1>
        <p>Welcome back, <strong>{profile.get('full_name', 'Merchant')}</strong> · 📍 {profile.get('region', 'N/A')} · {now_str}</p>
    </div>
    {verif_badge}
</div>
""", unsafe_allow_html=True)

# Quick action row (replaces hidden sidebar)
qa1, qa2, qa3 = st.columns([1, 1, 4])
with qa1:
    if st.button("🔄 Refresh", use_container_width=True):
        clear_data_cache()
        st.rerun()
with qa2:
    if verif_status.get("is_verified", False):
        st.markdown('<span class="pill pill-success">● Verified</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="pill pill-warning">● Pending</span>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VERIFICATION GATE
# ─────────────────────────────────────────────
if not verif_status.get("is_verified", False):
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "merchant")
    with tab_browse:
        st.markdown('<div class="alert-box alert-warning">⏳ Full access unlocks after account verification.</div>', unsafe_allow_html=True)
        # Browse products read-only
        products = cached_query("products", filters={"is_available": True}, limit=20)
        for p in products:
            with st.container(border=True):
                st.markdown(f"**{p.get('product_name')}** · {p.get('sector')} · {p.get('price_birr', 0):,.0f} Birr")
    st.stop()

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
(tab_overview, tab_browse_tab, tab_orders, tab_agree,
 tab_history, tab_pref, tab_ai_insights, tab_notif, tab_profile) = st.tabs([
    "📊 Overview", "🛒 Browse & Order", "📋 My Orders",
    "📄 Agreements", "📜 History", "⚙️ Preferences",
    "🤖 AI Insights", "🔔 Notifications", "👤 Profile",
])

# ══════════════════════════════════════════════
# TAB — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:
    try:
        my_orders_all = supabase.table("orders").select("*").eq("buyer_id", user_id).execute().data or []
    except Exception as e:
        logger.error(f"Order fetch error: {e}")
        my_orders_all = []

    active_ords  = [o for o in my_orders_all if o.get("status") in ("pending", "confirmed")]
    delivered    = [o for o in my_orders_all if o.get("status") in ("delivered", "completed")]
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

    if delivered:
        monthly: dict = {}
        for o in delivered:
            month = o.get("created_at", "")[:7]
            monthly[month] = monthly.get(month, 0) + float(o.get("total_price_birr") or 0)
        if monthly:
            st.markdown('<div class="section-title">Monthly Spending</div>', unsafe_allow_html=True)
            df_m = pd.DataFrame({"Month": list(monthly.keys()), "Spent": list(monthly.values())}).sort_values("Month")
            st.bar_chart(df_m.set_index("Month"), height=200, color="#2563eb")

    if my_orders_all:
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        for o in sorted(my_orders_all, key=lambda x: x.get("created_at", ""), reverse=True)[:5]:
            status = o.get("status", "pending")
            color  = {"pending": "#fbbf24", "confirmed": "#60a5fa", "delivered": "#4ade80",
                      "cancelled": "#f87171", "declined": "#f87171"}.get(status, "#94a3b8")
            ts = o.get("created_at", "")[:16].replace("T", " ")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #1e2a3a;">
                <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                <div>
                    <div style="font-size:13px;color:#94a3b8;">Order <strong style="color:#e2e8f0;">#{str(o['id'])[:8]}</strong> — {status.capitalize()} · {o.get('total_price_birr', 0):,.0f} Birr</div>
                    <div style="font-size:11px;color:#475569;">{ts}</div>
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — BROWSE & ORDER
# ══════════════════════════════════════════════
with tab_browse_tab:
    try:
        st.markdown('<div class="section-title">Browse Available Products</div>', unsafe_allow_html=True)

        bf1, bf2, bf3 = st.columns(3)
        with bf1:
            b_sector = st.selectbox("Sector", ["All"] + SECTORS, key="b_sector")
        with bf2:
            b_region = st.selectbox("Region", ["All"] + REGIONS, key="b_region")
        with bf3:
            b_search = st.text_input("🔍 Search", key="b_search", placeholder="Product name…")

        filters: dict = {"is_available": True}
        if b_sector != "All":
            filters["sector"] = b_sector
        if b_region != "All":
            filters["region"] = b_region

        products = cached_query("products", filters=filters, limit=50)

        if b_search:
            products = [p for p in products if b_search.lower() in p.get("product_name", "").lower()]

        if not products:
            st.info("No products match your filters.")
        else:
            st.caption(f"**{len(products)} product(s)** found")
            for p in products:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 2])
                    with c1:
                        st.markdown(f"**{p.get('product_name', 'Unknown')}**")
                        st.caption(f"{p.get('sector', '—')} · 📍 {p.get('region', '—')} · Stock: {p.get('quantity', 0)} {p.get('unit', '')}")
                    with c2:
                        st.markdown(f'<div class="price-tag">{p.get("price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr / {p.get("unit", "")}</div>', unsafe_allow_html=True)
                    with c3:
                        qty = st.number_input("Qty", min_value=0.1, value=1.0, step=0.5, key=f"qty_{p['id']}")
                        if st.button("🛒 Order", key=f"order_{p['id']}", type="primary", use_container_width=True):
                            try:
                                total = float(p.get("price_birr", 0)) * qty
                                supabase.table("orders").insert({
                                    "buyer_id":        user_id,
                                    "product_id":      p["id"],
                                    "quantity_ordered": qty,
                                    "total_price_birr": total,
                                    "status":          "pending",
                                    "buyer_role":      "merchant",
                                }).execute()
                                send_notification(
                                    p.get("producer_id", ""),
                                    "📦 New Order",
                                    f"A merchant placed an order for {p.get('product_name')}.",
                                    "info",
                                )
                                clear_data_cache()
                                st.success(f"✅ Order placed for {p.get('product_name')}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Order failed: {e}")
    except Exception as e:
        st.error(f"Browse error: {e}")

# ══════════════════════════════════════════════
# TAB — MY ORDERS
# ══════════════════════════════════════════════
with tab_orders:
    try:
        st.markdown('<div class="section-title">Active Orders</div>', unsafe_allow_html=True)
        try:
            my_orders = (
                supabase.table("orders")
                .select("*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id)")
                .eq("buyer_id", user_id)
                .neq("status", "delivered")
                .order("created_at", desc=True)
                .limit(50)
                .execute().data or []
            )
        except Exception as e:
            st.error(f"Could not load orders: {e}")
            my_orders = []

        of1, of2 = st.columns(2)
        with of1:
            ord_status = st.selectbox("Status", ["All", "pending", "confirmed", "cancelled"], key="mord_status")
        with of2:
            ord_search = st.text_input("🔍 Search", key="mord_search", placeholder="Product name…")

        filtered_orders = my_orders if ord_status == "All" else [o for o in my_orders if o.get("status") == ord_status]
        if ord_search:
            filtered_orders = [o for o in filtered_orders if ord_search.lower() in (o.get("products") or {}).get("product_name", "").lower()]

        STATUS_PILLS = {"pending": "pill-warning", "confirmed": "pill-info", "cancelled": "pill-danger"}

        if not filtered_orders:
            st.markdown('<div class="alert-box alert-info">📋 No active orders. Browse products to place your first order.</div>', unsafe_allow_html=True)
        else:
            st.caption(f"**{len(filtered_orders)} order(s)**")
            for o in filtered_orders:
                oid   = o["id"]
                prod  = o.get("products") or {}
                status = o.get("status", "pending")
                pill  = STATUS_PILLS.get(status, "pill-neutral")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 2, 2])
                    with c1:
                        st.markdown(f"**Order #{str(oid)[:8]}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                        st.markdown(f"**📦 {prod.get('product_name', 'Unknown')}** · {prod.get('sector', '')}")
                        st.caption(f"📍 {prod.get('region', 'N/A')} · 📅 {str(o.get('created_at', ''))[:10]}")
                    with c2:
                        st.markdown(f'<div class="price-tag" style="font-size:16px;">{o.get("quantity_ordered", 0):,.1f}</div><div style="font-size:11px;color:#64748b;">{prod.get("unit", "")}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="price-tag" style="margin-top:10px;">{o.get("total_price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
                    with c3:
                        if status == "pending":
                            if st.button("❌ Cancel", key=f"m_cancel_{oid}", use_container_width=True):
                                if st.session_state.get(f"confirm_cancel_{oid}"):
                                    try:
                                        supabase.table("orders").update({"status": "cancelled"}).eq("id", oid).execute()
                                        clear_data_cache()
                                        st.session_state.pop(f"confirm_cancel_{oid}", None)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")
                                else:
                                    st.session_state[f"confirm_cancel_{oid}"] = True
                                    st.rerun()
                            if st.session_state.get(f"confirm_cancel_{oid}"):
                                st.markdown('<div class="confirm-box">⚠️ Click Cancel again to confirm.</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Orders error: {e}")

# ══════════════════════════════════════════════
# TAB — AGREEMENTS
# ══════════════════════════════════════════════
with tab_agree:
    try:
        st.markdown('<div class="section-title">Agreement Requests from Producers</div>', unsafe_allow_html=True)
        try:
            producer_requests = (
                supabase.table("orders")
                .select("*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id)")
                .eq("buyer_id", user_id)
                .eq("producer_confirmed", True)
                .eq("merchant_confirmed", False)
                .execute().data or []
            )
        except Exception:
            producer_requests = []

        if not producer_requests:
            st.markdown('<div class="alert-box alert-info">📄 No pending agreement requests from producers.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-box alert-warning">📩 <strong>{len(producer_requests)} producer(s)</strong> have sent you supply agreement requests.</div>', unsafe_allow_html=True)
            for o in producer_requests:
                oid        = o["id"]
                prod       = o.get("products") or {}
                producer_id = prod.get("producer_id")
                qty_ord    = float(o.get("quantity_ordered") or 0)
                total_val  = float(o.get("total_price_birr") or 0)
                ppu        = float(prod.get("price_birr") or (total_val / qty_ord if qty_ord else 0))

                try:
                    prod_profile = supabase.table("profiles").select("full_name,phone,region").eq("id", producer_id).single().execute().data or {}
                except Exception:
                    prod_profile = {}

                with st.container(border=True):
                    c1, c2 = st.columns([5, 3])
                    with c1:
                        st.markdown(f"**📄 {prod.get('product_name', 'Unknown')}** &nbsp; <span class='pill pill-warning'>Awaiting Your Response</span>", unsafe_allow_html=True)
                        st.caption(f"Sector: {prod.get('sector', '')} · Grade: **{prod.get('quality_grade', '')}** · 📍 {prod.get('region', '')}")
                        st.caption(f"👤 Producer: **{prod_profile.get('full_name', 'Unknown')}** · 📞 {prod_profile.get('phone', 'N/A')}")
                        st.markdown(f'<div style="margin-top:10px;"><span class="price-tag">{qty_ord:,.1f} {prod.get("unit", "")}</span> &nbsp;&nbsp; <span class="price-tag">{total_val:,.0f} Birr</span></div>', unsafe_allow_html=True)

                        with st.expander("👁️ Preview Agreement"):
                            try:
                                preview_html = generate_agreement_preview_html(
                                    producer_name=prod_profile.get("full_name", "Producer"),
                                    producer_phone=prod_profile.get("phone", ""),
                                    producer_region=prod_profile.get("region", ""),
                                    merchant_name=profile.get("full_name", ""),
                                    merchant_phone=profile.get("phone", ""),
                                    merchant_region=profile.get("region", ""),
                                    product_name=prod.get("product_name", ""),
                                    sector=prod.get("sector", ""),
                                    quality_grade=prod.get("quality_grade", "A"),
                                    quantity=qty_ord,
                                    unit=prod.get("unit", ""),
                                    price_per_unit=ppu,
                                    total_price=total_val,
                                    delivery_date=str(o.get("created_at", ""))[:10],
                                    payment_method="Bank Transfer",
                                    producer_confirmed=True,
                                    merchant_confirmed=False,
                                    agreement_id=str(oid),
                                )
                                st.components.v1.html(preview_html, height=450, scrolling=True)
                            except Exception as ex:
                                st.caption(f"Preview error: {ex}")

                    with c2:
                        ba1, ba2 = st.columns(2)
                        with ba1:
                            if st.button("✅ Accept", key=f"m_accept_{oid}", type="primary", use_container_width=True):
                                try:
                                    supabase.table("orders").update({"merchant_confirmed": True, "status": "confirmed"}).eq("id", oid).execute()
                                    if producer_id:
                                        send_notification(producer_id, "🤝 Agreement Accepted", "Merchant accepted your supply agreement.", "success", order_id=oid)
                                    clear_data_cache()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")
                        with ba2:
                            if st.button("❌ Decline", key=f"m_decline_{oid}", use_container_width=True):
                                try:
                                    supabase.table("orders").update({
                                        "status": "declined",
                                        "declined_at": datetime.datetime.now().isoformat(),
                                        "declined_by": "merchant",
                                    }).eq("id", oid).execute()
                                    if producer_id:
                                        send_notification(producer_id, "❌ Agreement Declined", "Merchant declined your supply agreement.", "error")
                                    clear_data_cache()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")

                        try:
                            pdf_bytes = generate_agreement_pdf(
                                producer_name=prod_profile.get("full_name", "Producer"),
                                producer_phone=prod_profile.get("phone", ""),
                                producer_region=prod_profile.get("region", ""),
                                merchant_name=profile.get("full_name", ""),
                                merchant_phone=profile.get("phone", ""),
                                merchant_region=profile.get("region", ""),
                                product_name=prod.get("product_name", ""),
                                sector=prod.get("sector", ""),
                                quality_grade=prod.get("quality_grade", "A"),
                                quantity=qty_ord, unit=prod.get("unit", ""),
                                price_per_unit=ppu, total_price=total_val,
                                delivery_date=str(o.get("created_at", ""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True, merchant_confirmed=False,
                                agreement_id=str(oid),
                            )
                            st.download_button("📥 Download PDF", data=pdf_bytes,
                                file_name=f"agreement_{prod.get('product_name', '')}.pdf",
                                mime="application/pdf", key=f"m_pdf_{oid}", use_container_width=True)
                        except Exception:
                            pass

        # Confirmed agreements
        st.markdown('<div class="section-title">Confirmed Agreements</div>', unsafe_allow_html=True)
        try:
            confirmed_agrees = (
                supabase.table("orders")
                .select("*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id)")
                .eq("buyer_id", user_id).eq("merchant_confirmed", True)
                .in_("status", ["confirmed", "delivered"])
                .order("created_at", desc=True).execute().data or []
            )
        except Exception:
            confirmed_agrees = []

        if not confirmed_agrees:
            st.markdown('<div class="alert-box alert-info">No confirmed agreements yet.</div>', unsafe_allow_html=True)
        else:
            for o in confirmed_agrees:
                prod       = o.get("products") or {}
                status     = o.get("status", "confirmed")
                pill       = "pill-success" if status == "delivered" else "pill-info"
                producer_id2 = prod.get("producer_id")
                qty_ord2   = float(o.get("quantity_ordered") or 0)
                total_val2 = float(o.get("total_price_birr") or 0)
                ppu2       = float(prod.get("price_birr") or (total_val2 / qty_ord2 if qty_ord2 else 0))
                try:
                    pp2 = supabase.table("profiles").select("full_name,phone,region").eq("id", producer_id2).single().execute().data or {}
                except Exception:
                    pp2 = {}

                with st.container(border=True):
                    c1, c2 = st.columns([5, 2])
                    with c1:
                        st.markdown(f"**✅ {prod.get('product_name', 'Unknown')}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                        st.caption(f"Grade: **{prod.get('quality_grade', '')}** · {prod.get('sector', '')} · 📍 {prod.get('region', '')}")
                        st.caption(f"Qty: {qty_ord2:,.1f} {prod.get('unit', '')} · Date: {str(o.get('created_at', ''))[:10]}")
                    with c2:
                        st.markdown(f'<div class="price-tag">{total_val2:,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
                        try:
                            pdf_bytes2 = generate_agreement_pdf(
                                producer_name=pp2.get("full_name", "Producer"),
                                producer_phone=pp2.get("phone", ""),
                                producer_region=pp2.get("region", ""),
                                merchant_name=profile.get("full_name", ""),
                                merchant_phone=profile.get("phone", ""),
                                merchant_region=profile.get("region", ""),
                                product_name=prod.get("product_name", ""),
                                sector=prod.get("sector", ""),
                                quality_grade=prod.get("quality_grade", "A"),
                                quantity=qty_ord2, unit=prod.get("unit", ""),
                                price_per_unit=ppu2, total_price=total_val2,
                                delivery_date=str(o.get("created_at", ""))[:10],
                                payment_method="Bank Transfer",
                                producer_confirmed=True, merchant_confirmed=True,
                                agreement_id=str(o.get("id", "")),
                            )
                            st.download_button("📥 Download PDF", data=pdf_bytes2,
                                file_name=f"agreement_{prod.get('product_name', '')}_confirmed.pdf",
                                mime="application/pdf", key=f"m_conf_pdf_{o['id']}", use_container_width=True)
                        except Exception:
                            pass
    except Exception as e:
        st.error(f"Agreements error: {e}")

# ══════════════════════════════════════════════
# TAB — HISTORY
# ══════════════════════════════════════════════
with tab_history:
    try:
        st.markdown('<div class="section-title">Purchase History</div>', unsafe_allow_html=True)
        try:
            mh_orders = (
                supabase.table("orders")
                .select("*, products(product_name, sector, quality_grade, unit, region, producer_id)")
                .eq("buyer_id", user_id)
                .in_("status", ["delivered", "declined", "cancelled"])
                .order("created_at", desc=True).execute().data or []
            )
        except Exception:
            mh_orders = []

        hist_filter = st.selectbox("Show", ["All", "Delivered", "Declined", "Cancelled"], key="hist_filter")
        if hist_filter != "All":
            mh_orders = [o for o in mh_orders if o.get("status") == hist_filter.lower()]

        if not mh_orders:
            st.markdown('<div class="alert-box alert-info">📜 No history records yet.</div>', unsafe_allow_html=True)
        else:
            total_spent2 = sum(float(o.get("total_price_birr") or 0) for o in mh_orders if o.get("status") == "delivered")
            h1, h2 = st.columns(2)
            with h1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Purchased</div><div class="price-tag">{total_spent2:,.0f}</div><div class="kpi-sub">Birr spent</div></div>', unsafe_allow_html=True)
            with h2:
                delivered_count = len([o for o in mh_orders if o.get("status") == "delivered"])
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Completed Orders</div><div class="kpi-value">{delivered_count}</div><div class="kpi-sub">Received successfully</div></div>', unsafe_allow_html=True)

            sector_spend: dict = {}
            for o in mh_orders:
                if o.get("status") == "delivered":
                    s = (o.get("products") or {}).get("sector", "Other")
                    sector_spend[s] = sector_spend.get(s, 0) + float(o.get("total_price_birr") or 0)
            if sector_spend:
                st.markdown('<div class="section-title">Spending by Sector</div>', unsafe_allow_html=True)
                df_sec = pd.DataFrame({"Sector": list(sector_spend.keys()), "Spent (Birr)": list(sector_spend.values())})
                st.bar_chart(df_sec.set_index("Sector"), height=200, color="#2563eb")

            st.markdown('<div class="section-title">All Historical Orders</div>', unsafe_allow_html=True)
            for o in mh_orders[:20]:
                prod   = o.get("products") or {}
                status = o.get("status", "unknown")
                status_color = {"delivered": "#4ade80", "cancelled": "#f87171", "declined": "#f87171"}.get(status, "#94a3b8")
                with st.container(border=True):
                    c1, c2 = st.columns([5, 2])
                    with c1:
                        st.markdown(f"**{prod.get('product_name', 'Unknown')}** · {prod.get('sector', '')} &nbsp; <span style='color:{status_color};font-size:12px;font-weight:600;'>● {status.upper()}</span>", unsafe_allow_html=True)
                        st.caption(f"Grade: **{prod.get('quality_grade', '')}** · 📍 {prod.get('region', 'N/A')} · 📅 {str(o.get('created_at', ''))[:10]}")
                    with c2:
                        st.markdown(f'<div class="price-tag">{o.get("total_price_birr", 0):,.0f}</div><div style="font-size:11px;color:#64748b;">Birr</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"History error: {e}")

# ══════════════════════════════════════════════
# TAB — PREFERENCES
# ══════════════════════════════════════════════
with tab_pref:
    try:
        st.markdown('<div class="section-title">Buying Preferences</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-box alert-info">💡 Your preferences help the AI matching engine recommend the best products and producers.</div>', unsafe_allow_html=True)

        with st.container(border=True):
            with st.form("merchant_pref_form"):
                pc1, pc2 = st.columns(2)
                with pc1:
                    pref_sectors = st.multiselect("🏭 Preferred Sectors", SECTORS,
                        default=(existing_pref.get("preferred_sectors") or []) if existing_pref else [])
                    pref_products = st.multiselect("📦 Preferred Products",
                        ["Teff", "Coffee", "Maize", "Wheat", "Sesame", "Lentils", "Beans", "Barley", "Sorghum", "Other"],
                        default=(existing_pref.get("preferred_products") or []) if existing_pref else [])
                    pref_regions = st.multiselect("📍 Preferred Regions", REGIONS,
                        default=(existing_pref.get("preferred_regions") or []) if existing_pref else [])
                    pref_quality = st.selectbox("⭐ Minimum Quality Grade",
                        ["Any", "A", "B", "C", "Premium", "Standard"], index=0)
                with pc2:
                    max_budget = st.number_input("💰 Max Order Budget (Birr)", min_value=0.0,
                        value=float(existing_pref.get("max_budget_birr") or 50000) if existing_pref else 50000.0, step=1000.0)
                    pref_payment = st.selectbox("💳 Payment Method",
                        ["Bank Transfer", "Cash on Delivery", "Mobile Money", "Letter of Credit"])
                    needs_delivery = st.checkbox("🚚 Require Delivery Service",
                        value=bool((existing_pref or {}).get("needs_delivery", False)))

                if st.form_submit_button("💾 Save Preferences", type="primary", use_container_width=True):
                    pref_payload = {
                        "merchant_id": user_id,
                        "preferred_sectors": pref_sectors,
                        "preferred_products": pref_products,
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
                        clear_data_cache()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save failed: {e}")
    except Exception as e:
        st.error(f"Preferences error: {e}")

# ══════════════════════════════════════════════
# TAB — AI INSIGHTS
# ══════════════════════════════════════════════
with tab_ai_insights:
    try:
        st.markdown('<div class="section-title">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)
        st.markdown('<div class="alert-box alert-info">Leverage AI engines to optimize purchasing, detect fraud, and find the best deals.</div>', unsafe_allow_html=True)

        ai1, ai2, ai3 = st.columns(3)

        with ai1:
            with st.container(border=True):
                st.markdown("**🛒 Smart Recommendations**")
                st.caption("AI-recommended products based on your preferences.")
                if st.button("Get Recommendations", use_container_width=True, key="ai_rec_btn"):
                    with st.spinner("Analyzing..."):
                        try:
                            pref_products_ai = (existing_pref.get("preferred_products") or []) if existing_pref else []
                            pref_regions_ai  = (existing_pref.get("preferred_regions") or []) if existing_pref else []
                            recs = get_recommendations(
                                commodity=pref_products_ai[0] if pref_products_ai else None,
                                region=pref_regions_ai[0] if pref_regions_ai else None,
                                top_k=5,
                            )
                            if recs:
                                st.success(f"✅ Found {len(recs)} recommendations!")
                                for r in recs[:3]:
                                    st.markdown(f"- **{r.get('commodity', 'Unknown')}** — ETB {r.get('price_etb', 0):,.2f}")
                            else:
                                st.info("No recommendations yet. Update your preferences.")
                        except Exception as e:
                            st.error(f"Recommendation error: {e}")

        with ai2:
            with st.container(border=True):
                st.markdown("**🛡️ Fraud Detection**")
                st.caption("Check transactions for potential fraud risks.")
                if st.button("Run Fraud Check", use_container_width=True, key="ai_fraud_btn"):
                    with st.spinner("Scanning..."):
                        try:
                            recent_orders = (
                                supabase.table("orders")
                                .select("*, products(sector, product_name, region)")
                                .eq("buyer_id", user_id).limit(5).execute().data or []
                            )
                            if recent_orders:
                                high_risk = 0
                                for order in recent_orders:
                                    prod_f = order.get("products") or {}
                                    risk = check_fraud_risk(
                                        sector=prod_f.get("sector", "Agriculture"),
                                        product=prod_f.get("product_name", ""),
                                        region=prod_f.get("region", ""),
                                        payment_method="Bank Transfer",
                                        quantity=order.get("quantity_ordered", 1),
                                        agreed_price_birr=order.get("total_price_birr", 0),
                                        market_price_birr=None,
                                    )
                                    if risk.get("risk_level") == "High":
                                        high_risk += 1
                                if high_risk == 0:
                                    st.success("✅ All recent transactions show low fraud risk.")
                                else:
                                    st.warning(f"⚠️ {high_risk} transaction(s) flagged for review.")
                            else:
                                st.info("No recent orders to analyze.")
                        except Exception as e:
                            st.error(f"Fraud check error: {e}")

        with ai3:
            with st.container(border=True):
                st.markdown("**💰 Price Optimization**")
                st.caption("Find the best negotiation price for your purchases.")
                if st.button("Analyze Prices", use_container_width=True, key="ai_price_btn"):
                    with st.spinner("Computing..."):
                        try:
                            pref_products_pr = (existing_pref.get("preferred_products") or ["Teff"]) if existing_pref else ["Teff"]
                            price_result = recommend_price(
                                sector="Agriculture",
                                product=pref_products_pr[0],
                                region=profile.get("region", "Oromia"),
                                quality_grade="B",
                                quantity=1.0,
                            )
                            recommended = price_result.get("recommended_price_birr", 0)
                            if recommended > 0:
                                st.success(f"✅ Recommended price: ETB {recommended:.2f}")
                                st.caption(f"Season: {price_result.get('season', 'N/A')} · Confidence: {price_result.get('confidence', 0):.0%}")
                            else:
                                st.info("Price analysis complete. Check the forecast for more.")
                        except Exception as e:
                            st.error(f"Price error: {e}")

        # Demand forecast
        st.markdown('<div class="section-title">📈 Demand Forecast</div>', unsafe_allow_html=True)

        _all_prod_names: list = []
        try:
            _avail = supabase.table("products").select("product_name").eq("is_available", True).execute().data or []
            _all_prod_names = sorted(set(p["product_name"] for p in _avail if p.get("product_name")))
        except Exception:
            pass

        mfc_col1, mfc_col2, mfc_col3, mfc_col4 = st.columns([2, 2, 2, 1])
        with mfc_col1:
            mfc_product = st.selectbox("Product", ["(General / All)"] + _all_prod_names, key="mfc_product")
        with mfc_col2:
            mfc_sector  = st.selectbox("Sector", SECTORS, key="mfc_sector")
        with mfc_col3:
            mfc_region  = st.selectbox("Region", REGIONS, key="mfc_region")
        with mfc_col4:
            mfc_horizon = st.selectbox("Weeks", [4, 8, 12, 16], index=2, key="mfc_horizon")

        if st.button("📈 Run Forecast", type="primary", use_container_width=True, key="m_run_forecast"):
            with st.spinner("Running AI demand model…"):
                try:
                    _mfc_result = forecast_demand(sector=mfc_sector, region=mfc_region, horizon=mfc_horizon)
                    st.session_state.m_forecast_result = _mfc_result
                    st.session_state.m_forecast_params = (mfc_product, mfc_sector, mfc_region, mfc_horizon)
                except Exception as _e:
                    st.error(f"Forecast failed: {_e}")

        _mfc_res = st.session_state.get("m_forecast_result")
        _mfc_par = st.session_state.get("m_forecast_params")
        if _mfc_res and _mfc_par:
            _mp, _ms, _mr, _mh = _mfc_par
            _plabel = f" · {_mp}" if _mp and _mp != "(General / All)" else ""
            st.markdown(f'<div class="section-title">Forecast: {_ms}{_plabel} · {_mr} · {_mh} Weeks</div>', unsafe_allow_html=True)
            if isinstance(_mfc_res, list) and _mfc_res:
                _avg  = sum(_mfc_res) / len(_mfc_res)
                _peak = max(_mfc_res)
                _trend = "📈 Rising" if _mfc_res[-1] > _mfc_res[0] else ("📉 Falling" if _mfc_res[-1] < _mfc_res[0] else "➡️ Stable")
                _mc1, _mc2, _mc3 = st.columns(3)
                with _mc1:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Weekly Demand</div><div class="kpi-value">{_avg:,.0f}</div><div class="kpi-sub">Units / week</div></div>', unsafe_allow_html=True)
                with _mc2:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Peak Week</div><div class="kpi-value">{_peak:,.0f}</div><div class="kpi-sub">Max units</div></div>', unsafe_allow_html=True)
                with _mc3:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Trend</div><div class="kpi-value" style="font-size:20px;">{_trend}</div></div>', unsafe_allow_html=True)

                _weeks = [f"W{i+1}" for i in range(len(_mfc_res))]
                _fig_m = go.Figure()
                _fig_m.add_trace(go.Scatter(x=_weeks, y=_mfc_res, mode="lines+markers",
                    line=dict(color="#60a5fa", width=2), marker=dict(size=6, color="#2563eb"),
                    fill="tozeroy", fillcolor="rgba(96,165,250,0.08)", name="Demand"))
                _fig_m.update_layout(paper_bgcolor="#161b27", plot_bgcolor="#161b27",
                    font=dict(color="#94a3b8", family="Inter"),
                    xaxis=dict(gridcolor="#1e2a3a"), yaxis=dict(gridcolor="#1e2a3a", title="Units"),
                    margin=dict(l=40, r=20, t=20, b=40), height=280, showlegend=False)
                st.plotly_chart(_fig_m, use_container_width=True)

        # AI Readiness Score
        st.markdown('<div class="section-title">Your AI Readiness Score</div>', unsafe_allow_html=True)
        score = 40
        if existing_pref:
            if existing_pref.get("preferred_sectors"):  score += 15
            if existing_pref.get("preferred_products"): score += 15
            if existing_pref.get("preferred_regions"):  score += 15
            if existing_pref.get("max_budget_birr", 0) > 0: score += 15
        score = min(score, 100)

        fig_score = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            title={"text": "Overall AI Utilization", "font": {"color": "#94a3b8"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#94a3b8"},
                "bar": {"color": "#60a5fa"}, "bgcolor": "#1e2a3a",
                "borderwidth": 2, "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 50], "color": "#7f1d1d"},
                    {"range": [50, 80], "color": "#78350f"},
                    {"range": [80, 100], "color": "#1e3a5f"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
            },
        ))
        fig_score.update_layout(paper_bgcolor="#161b27", font={"color": "#94a3b8", "family": "Inter"}, height=300)
        st.plotly_chart(fig_score, use_container_width=True)
        st.caption("💡 Complete your preferences and use AI features to improve your score!")

    except Exception as e:
        st.error(f"AI Insights error: {e}")

# ══════════════════════════════════════════════
# TAB — NOTIFICATIONS
# ══════════════════════════════════════════════
with tab_notif:
    try:
        from utils.db_helpers import get_notifications, mark_notification_read, mark_all_notifications_read
        st.markdown('<div class="section-title">🔔 Notifications</div>', unsafe_allow_html=True)
        notifs = get_notifications(user_id, limit=20)
        if not notifs:
            st.info("No notifications yet.")
        else:
            if st.button("✅ Mark All Read", key="notif_mark_all"):
                mark_all_notifications_read(user_id)
                st.rerun()
            for n in notifs:
                is_read = n.get("is_read", False)
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    with c1:
                        st.markdown(f"{'**' if not is_read else ''}{n.get('title', '')}{'**' if not is_read else ''}")
                        st.caption(n.get("message", ""))
                        st.caption(str(n.get("created_at", ""))[:16].replace("T", " "))
                    with c2:
                        if not is_read:
                            if st.button("✓", key=f"read_{n['id']}"):
                                mark_notification_read(n["id"])
                                st.rerun()
    except Exception as e:
        st.error(f"Notifications error: {e}")

# ══════════════════════════════════════════════
# TAB — PROFILE
# ══════════════════════════════════════════════
with tab_profile:
    try:
        st.markdown('<div class="section-title">👤 Your Profile</div>', unsafe_allow_html=True)
        with st.form("merchant_profile_form"):
            pf1, pf2 = st.columns(2)
            with pf1:
                new_name  = st.text_input("Full Name",  value=profile.get("full_name", ""))
                new_phone = st.text_input("Phone",      value=profile.get("phone", "") or "")
            with pf2:
                new_region = st.selectbox("Region", REGIONS,
                    index=REGIONS.index(profile.get("region", REGIONS[0])) if profile.get("region") in REGIONS else 0)
            if st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True):
                try:
                    supabase.table("profiles").update({
                        "full_name": new_name,
                        "phone":     new_phone,
                        "region":    new_region,
                    }).eq("id", user_id).execute()
                    st.session_state.profile["full_name"] = new_name
                    st.session_state.profile["phone"]     = new_phone
                    st.session_state.profile["region"]    = new_region
                    clear_data_cache()
                    st.success("✅ Profile updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")
    except Exception as e:
        st.error(f"Profile error: {e}")

# ─────────────────────────────────────────────
# FLOATING CHATBOT (optional)
# ─────────────────────────────────────────────
try:
    from utils.chatbot import render_floating_chatbot
    render_floating_chatbot(profile)
except Exception:
    pass
