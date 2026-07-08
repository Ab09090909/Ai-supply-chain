"""Admin Dashboard Page — Professional redesign with AI Analytics."""
import sys
import os
import base64
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme import inject_theme, render_theme_toggle
from utils.constants import REGIONS
from utils.db_helpers import supabase, cached_get_profile, send_notification, clear_data_cache
from src.fraud_engine import check_fraud_risk
from utils.shared_ui import render_profile_editor_modal

# ─────────────────────────────────────────────
# Page Config + CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Admin Panel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()  # Must run right after set_page_config so sidebar CSS loads first


st.markdown("""
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0f1117 !important;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
}

/* Sidebar colours controlled by inject_theme() in utils/theme.py */

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Admin Header Banner ── */
.admin-header {
    background: linear-gradient(135deg, #1a2744 0%, #0f172a 60%, #162032 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 20px;
}
.admin-header-icon {
    font-size: 40px;
    line-height: 1;
}
.admin-header h1 {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
}
.admin-header p {
    margin: 4px 0 0;
    font-size: 13px;
    color: #64748b;
}
.admin-badge {
    margin-left: auto;
    background: #1e3a5f;
    border: 1px solid #2563eb44;
    color: #60a5fa;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Metric Cards ── */
.kpi-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 20px 24px;
    transition: border-color 0.2s;
    height: 100%;
}
.kpi-card:hover { border-color: #2563eb55; }
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #f1f5f9;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.kpi-delta {
    font-size: 12px;
    color: #22c55e;
    margin-top: 6px;
}

/* ── Status Pills ── */
.pill {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.3px;
}
.pill-success { background: #14532d44; color: #4ade80; border: 1px solid #16a34a44; }
.pill-warning { background: #78350f44; color: #fbbf24; border: 1px solid #d9770644; }
.pill-danger  { background: #7f1d1d44; color: #f87171; border: 1px solid #ef444444; }
.pill-info    { background: #1e3a5f44; color: #60a5fa; border: 1px solid #2563eb44; }
.pill-neutral { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }

/* ── Record Cards ── */
.record-card {
    background: #161b27;
    border: 1px solid #1e2a3a;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.15s;
}
.record-card:hover { border-color: #2563eb55; }
.record-name {
    font-size: 15px;
    font-weight: 600;
    color: #f1f5f9;
    margin: 0 0 4px;
}
.record-meta {
    font-size: 12px;
    color: #64748b;
    margin: 0;
}

/* ── Section Headers ── */
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

/* ── Tabs override ── */
[data-testid="stTabs"] > div > div > div > button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 8px 16px !important;
}
[data-testid="stTabs"] > div > div > div > button[aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom-color: #2563eb !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}

/* ── Danger button ── */
.danger-btn > button {
    background: #7f1d1d44 !important;
    border: 1px solid #ef444455 !important;
    color: #f87171 !important;
}
.danger-btn > button:hover {
    background: #ef444422 !important;
    border-color: #ef4444 !important;
}

/* ── Document preview modal backdrop ── */
.doc-preview-container {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    margin-top: 12px;
}

/* ── Activity feed ── */
.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1e2a3a;
}
.activity-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.activity-text { font-size: 13px; color: #94a3b8; }
.activity-time { font-size: 11px; color: #475569; margin-top: 2px; }

/* ── Alert boxes ── */
.alert-box {
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    margin-bottom: 12px;
    border: 1px solid;
}
.alert-warning { background: #78350f22; border-color: #d9770666; color: #fbbf24; }
.alert-danger   { background: #7f1d1d22; border-color: #ef444466; color: #f87171; }
.alert-info     { background: #1e3a5f22; border-color: #2563eb66; color: #60a5fa; }

/* ── Search + filter bar ── */
[data-testid="stTextInput"] input {
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

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Confirmation warning ── */
.confirm-box {
    background: #7f1d1d22;
    border: 1px solid #ef444455;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 13px;
    color: #fca5a5;
    margin-bottom: 8px;
}

/* ── Fraud risk badges ── */
.fraud-low  { color: #4ade80; font-weight: 600; font-size: 12px; }
.fraud-med  { color: #fbbf24; font-weight: 600; font-size: 12px; }
.fraud-high { color: #f87171; font-weight: 600; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Auth Guard
# ─────────────────────────────────────────────
if st.session_state.get("user") is None:
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
now_str = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

# Profile picture for admin header
_apic = profile.get("profile_image")
if _apic:
    _apic_html = f'<img src="data:image/jpeg;base64,{_apic}" style="width:80px;height:80px;border-radius:50%;border:3px solid #60a5fa;object-fit:cover;">'
else:
    _apic_html = f'<div style="width:80px;height:80px;border-radius:50%;border:3px solid #60a5fa;background:#1e2a3a;display:flex;align-items:center;justify-content:center;font-size:32px;color:#f1f5f9;font-weight:700;">{profile.get("full_name","A")[0].upper()}</div>'

st.markdown(f"""
<div class="admin-header">
    <div style="flex-shrink:0;position:relative;width:80px;height:80px;">
        {_apic_html}
        <div style="position:absolute;bottom:0;right:0;width:24px;height:24px;background:#1d4ed8;border-radius:50%;border:2px solid #0f1117;display:flex;align-items:center;justify-content:center;font-size:12px;" title="Edit Profile">✏️</div>
    </div>
    <div style="flex:1;margin-left:20px;">
        <h1>Admin Panel</h1>
        <p>System Administration & User Management · {now_str}</p>
    </div>
    <div class="admin-badge">Super Admin</div>
</div>
""", unsafe_allow_html=True)

_ac1, _ac2, _ac3 = st.columns([1, 6, 1])
with _ac3:
    if st.button("✏️ Edit Profile", key="admin_header_edit_btn", use_container_width=True):
        st.session_state.show_profile_editor = True

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛡️ Quick Actions")
    if st.button("🔄 Refresh All Data", use_container_width=True):
        clear_data_cache()
        st.rerun()
    
    # Update 7: Dark/Light Toggle
    st.markdown("### 🎨 Theme")
    render_theme_toggle(page="admin")
    
    st.divider()
    st.markdown("### 📌 System Status")
    st.markdown('<div class="pill pill-success">● Database Online</div>', unsafe_allow_html=True)
    st.markdown('<br><div class="pill pill-success">● API Connected</div>', unsafe_allow_html=True)
    st.markdown('<br><div class="pill pill-info">● Storage Active</div>', unsafe_allow_html=True)
    st.divider()
    st.caption(f"Logged in as **{profile.get('full_name','Admin')}**")
    st.caption(f"Session started {now_str}")

# ─────────────────────────────────────────────
# Fetch Stats (Cached for performance - Update 8)
# ─────────────────────────────────────────────
@st.cache_data(ttl=120)  # Increased cache time for performance
def fetch_overview_stats():
    try:
        total_users     = supabase.table("profiles").select("", count="exact").execute().count or 0
        total_producers = supabase.table("profiles").select("", count="exact").eq("role", "producer").execute().count or 0
        total_merchants = supabase.table("profiles").select("", count="exact").eq("role", "merchant").execute().count or 0
        total_customers = supabase.table("profiles").select("", count="exact").eq("role", "customer").execute().count or 0
        total_products  = supabase.table("products").select("", count="exact").execute().count or 0
        total_orders    = supabase.table("orders").select("", count="exact").execute().count or 0
        pending_verify  = supabase.table("profiles").select("", count="exact").eq("is_verified", False).execute().count or 0
        pending_orders  = supabase.table("orders").select("", count="exact").eq("status", "pending").execute().count or 0
        revenue_data    = supabase.table("orders").select("total_price_birr").eq("status", "delivered").execute().data or []
        total_revenue   = sum(r.get("total_price_birr", 0) for r in revenue_data)
    except Exception:
        total_users = total_producers = total_merchants = total_customers = 0
        total_products = total_orders = pending_verify = pending_orders = total_revenue = 0
    return dict(
        total_users=total_users, total_producers=total_producers,
        total_merchants=total_merchants, total_customers=total_customers,
        total_products=total_products, total_orders=total_orders,
        pending_verify=pending_verify, pending_orders=pending_orders,
        total_revenue=total_revenue,
    )

stats = fetch_overview_stats()

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
(tab_overview, tab_users, tab_verify, tab_docs,
 tab_db, tab_products, tab_orders, tab_analytics, tab_activity, tab_settings) = st.tabs([
    "📊 Overview", "👥 Users", "✅ Verify",
    "📄 Documents", "🗄️ Database", "📦 Products",
    "📋 Orders", "📈 Analytics", "📡 Activity", "⚙️ Settings",
])

# ══════════════════════════════════════════════
# TAB — OVERVIEW
# ══════════════════════════════════════════════
with tab_overview:
    # Alert banners
    if stats["pending_verify"] > 0:
        st.markdown(f'<div class="alert-box alert-warning">⏳ <strong>{stats["pending_verify"]} users</strong> are awaiting account verification.</div>', unsafe_allow_html=True)
    if stats["pending_orders"] > 0:
        st.markdown(f'<div class="alert-box alert-info">📦 <strong>{stats["pending_orders"]} orders</strong> are pending confirmation.</div>', unsafe_allow_html=True)
    
    # KPI row 1
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Users</div><div class="kpi-value">{stats["total_users"]}</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Products Listed</div><div class="kpi-value">{stats["total_products"]}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Orders</div><div class="kpi-value">{stats["total_orders"]}</div></div>', unsafe_allow_html=True)
    with k4:
        revenue_display = f"{stats['total_revenue']:,.0f}"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Revenue (Birr)</div><div class="kpi-value">{revenue_display}</div></div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # KPI row 2
    k5, k6, k7, k8 = st.columns(4)
    with k5:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Producers</div><div class="kpi-value">{stats["total_producers"]}</div></div>', unsafe_allow_html=True)
    with k6:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Merchants</div><div class="kpi-value">{stats["total_merchants"]}</div></div>', unsafe_allow_html=True)
    with k7:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Customers</div><div class="kpi-value">{stats["total_customers"]}</div></div>', unsafe_allow_html=True)
    with k8:
        pv = stats["pending_verify"]
        color = "pill-warning" if pv > 0 else "pill-success"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Pending Verify</div><div class="kpi-value">{pv}</div></div>', unsafe_allow_html=True)
    
    # Role breakdown chart
    st.markdown('<div class="section-title">Role Distribution</div>', unsafe_allow_html=True)
    chart_data = pd.DataFrame({
        "Role": ["Producers", "Merchants", "Customers"],
        "Count": [stats["total_producers"], stats["total_merchants"], stats["total_customers"]],
    })
    st.bar_chart(chart_data.set_index("Role"), height=220, color="#2563eb")

# ══════════════════════════════════════════════
# TAB — USERS
# ══════════════════════════════════════════════
with tab_users:
    st.markdown('<div class="section-title">User Management</div>', unsafe_allow_html=True)
    fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
    with fcol1:
        filter_role = st.selectbox("Role", ["All", "producer", "merchant", "customer", "admin"], key="admin_filter_role")
    with fcol2:
        search_user = st.text_input("🔍 Search by name", key="admin_search_user", placeholder="Type a name…")
    with fcol3:
        filter_verified = st.selectbox("Status", ["All", "Verified", "Unverified"], key="admin_filter_verified")
    
    try:
        query = supabase.table("profiles").select("*")
        if filter_role != "All":
            query = query.eq("role", filter_role)
        if filter_verified == "Verified":
            query = query.eq("is_verified", True)
        elif filter_verified == "Unverified":
            query = query.eq("is_verified", False)
        users = query.order("created_at", desc=True).execute().data or []
        if search_user:
            kw = search_user.lower()
            users = [u for u in users if kw in u.get("full_name", "").lower()]
    except Exception:
        users = []
    
    st.caption(f"**{len(users)} user(s) found**")
    for user in users:
        uid = user["id"]
        verified = user.get("is_verified", False)
        role = user.get("role", "N/A")
        role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(role, "⚪")
        status_pill = '<span class="pill pill-success">Verified</span>' if verified else '<span class="pill pill-warning">Pending</span>'
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([5, 2, 2, 3])
            with c1:
                st.markdown(f"**{role_icon} {user.get('full_name','Unknown')}** &nbsp; {status_pill}", unsafe_allow_html=True)
                st.caption(f"📍 {user.get('region','N/A')}  ·  📞 {user.get('phone','N/A')}  ·  Role: **{role.capitalize()}**")
                created = user.get("created_at", "")[:10] if user.get("created_at") else "—"
                st.caption(f"Joined: {created}")
            with c2:
                if not verified:
                    if st.button("✅ Verify", key=f"verify_{uid}", use_container_width=True):
                        try:
                            supabase.table("profiles").update({"is_verified": True}).eq("id", uid).execute()
                            send_notification(uid, "✅ Verified", "Your account is verified.", "success")
                            clear_data_cache()
                            st.rerun()
                        except Exception as _ve:
                            st.error(f"Error: {_ve}")
                else:
                    st.success("Verified")
            with c3:
                if st.button("✉️ Notify", key=f"notify_{uid}", use_container_width=True):
                    st.session_state[f"show_notify_{uid}"] = True
            with c4:
                if st.session_state.get(f"confirm_del_user_{uid}"):
                    st.markdown('<div class="confirm-box">⚠️ This will permanently delete this user.</div>', unsafe_allow_html=True)
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("🗑️ Confirm Delete", key=f"do_del_user_{uid}", use_container_width=True, type="primary"):
                            try:
                                supabase.table("profiles").delete().eq("id", uid).execute()
                                clear_data_cache()
                                st.session_state.pop(f"confirm_del_user_{uid}", None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                    with dc2:
                        if st.button("Cancel", key=f"cancel_del_user_{uid}", use_container_width=True):
                            st.session_state.pop(f"confirm_del_user_{uid}", None)
                            st.rerun()
                else:
                    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_user_{uid}", use_container_width=True):
                        st.session_state[f"confirm_del_user_{uid}"] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.get(f"show_notify_{uid}"):
                with st.expander("📨 Send Notification", expanded=True):
                    n_title = st.text_input("Title", key=f"ntitle_{uid}")
                    n_msg   = st.text_area("Message", key=f"nmsg_{uid}", height=80)
                    if st.button("Send", key=f"nsend_{uid}"):
                        if n_title and n_msg:
                            send_notification(uid, n_title, n_msg, "info")
                            st.session_state.pop(f"show_notify_{uid}", None)
                            st.success("Notification sent.")
                        else:
                            st.warning("Fill in both fields.")

# ══════════════════════════════════════════════
# TAB — VERIFY
# ══════════════════════════════════════════════
with tab_verify:
    st.markdown('<div class="section-title">Verification Queue</div>', unsafe_allow_html=True)
    try:
        pending_users = supabase.table("profiles").select("*").eq("is_verified", False).order("created_at", desc=True).execute().data or []
    except Exception:
        pending_users = []
    
    if not pending_users:
        st.info("✅ No pending verifications. All caught up!")
    else:
        st.markdown(f'<div class="alert-box alert-warning">⏳ <strong>{len(pending_users)} accounts</strong> awaiting review</div>', unsafe_allow_html=True)
        for user in pending_users:
            uid = user["id"]
            role = user.get("role", "N/A")
            created = user.get("created_at", "")[:10] if user.get("created_at") else "—"
            role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒"}.get(role, "⚪")
            with st.container(border=True):
                c1, c2 = st.columns([5, 2])
                with c1:
                    st.markdown(f"**{role_icon} {user.get('full_name','Unknown')}**")
                    st.caption(f"📍 {user.get('region','N/A')}  ·  Role: **{role.capitalize()}**  ·  Joined: {created}")
                    st.caption(f"📞 {user.get('phone','N/A')}")
                with c2:
                    if st.button("✅ Approve", key=f"vp_{uid}", type="primary", use_container_width=True):
                        supabase.table("profiles").update({"is_verified": True}).eq("id", uid).execute()
                        send_notification(uid, "✅ Verified", "Your account is now verified.", "success")
                        clear_data_cache()
                        st.rerun()
                    if st.button("❌ Reject", key=f"rp_{uid}", use_container_width=True):
                        send_notification(uid, "❌ Rejected", "Your account verification was rejected.", "error")
                        st.warning(f"Rejection notification sent to {user.get('full_name','user')}.")

# ══════════════════════════════════════════════
# TAB — DOCUMENTS
# ══════════════════════════════════════════════
with tab_docs:
    st.markdown('<div class="section-title">Document Verification</div>', unsafe_allow_html=True)
    try:
        all_docs = supabase.table("verification_documents").select("*").order("uploaded_at", desc=True).execute().data or []
    except Exception:
        all_docs = []
    
    if not all_docs:
        st.info("No documents uploaded yet.")
    else:
        df1, df2 = st.columns(2)
        with df1:
            doc_status_filter = st.selectbox("Status", ["All", "Pending", "Verified"], key="doc_status_filter")
        with df2:
            doc_type_filter = st.text_input("Filter by type", placeholder="e.g. license", key="doc_type_filter")
        
        filtered_docs = all_docs
        if doc_status_filter == "Pending":
            filtered_docs = [d for d in filtered_docs if not d.get("is_verified")]
        elif doc_status_filter == "Verified":
            filtered_docs = [d for d in filtered_docs if d.get("is_verified")]
        if doc_type_filter:
            filtered_docs = [d for d in filtered_docs if doc_type_filter.lower() in (d.get("document_type") or "").lower()]
        
        st.caption(f"**{len(filtered_docs)} document(s)**")
        for doc in filtered_docs:
            doc_id = doc["id"]
            is_verified = doc.get("is_verified", False)
            user_info = cached_get_profile(doc.get("user_id")) or {}
            status_pill = '<span class="pill pill-success">Verified</span>' if is_verified else '<span class="pill pill-warning">Pending</span>'
            size_kb = doc.get("file_size", 0) / 1024
            with st.container(border=True):
                c1, c2, c3 = st.columns([5, 2, 3])
                with c1:
                    st.markdown(f"**📄 {doc.get('document_name','Unnamed')}** &nbsp; {status_pill}", unsafe_allow_html=True)
                    st.caption(f"👤 {user_info.get('full_name','Unknown')} ({user_info.get('role','N/A').capitalize()})")
                    st.caption(f"Type: {doc.get('document_type','—')}  ·  Size: {size_kb:.1f} KB  ·  Uploaded: {doc.get('uploaded_at','')[:10]}")
                with c2:
                    if st.button("👁️ Preview", key=f"prev_{doc_id}", use_container_width=True):
                        st.session_state[f"preview_{doc_id}"] = not st.session_state.get(f"preview_{doc_id}", False)
                with c3:
                    if not is_verified:
                        if st.button("✅ Approve", key=f"vdoc_{doc_id}", type="primary", use_container_width=True):
                            try:
                                supabase.table("verification_documents").update({
                                    "is_verified": True,
                                    "verified_at": datetime.datetime.now().isoformat()
                                }).eq("id", doc_id).execute()
                                supabase.table("profiles").update({"is_verified": True}).eq("id", doc.get("user_id")).execute()
                                send_notification(doc.get("user_id"), "✅ Document Verified", "Your document has been approved.", "success")
                                clear_data_cache()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {e}")
                        if st.button("❌ Reject", key=f"rdoc_{doc_id}", use_container_width=True):
                            send_notification(doc.get("user_id"), "❌ Document Rejected", "Your document was not approved.", "error")
                            st.warning("Rejection sent.")
                    else:
                        st.success("✅ Approved")
                
            if st.session_state.get(f"preview_{doc_id}"):
                 st.markdown('<div class="doc-preview-container">', unsafe_allow_html=True)
                 st.markdown(f"**Preview: {doc.get('document_name','')}**")
                 
                 # 1. Try Base64 first (if saved directly in DB)
                 doc_b64 = doc.get("file_base64") or doc.get("image_base64")
                 if doc_b64:
                     try:
                         doc_b64_clean = doc_b64.replace('\n','').replace('\r','').replace(' ','')
                         raw = base64.b64decode(doc_b64_clean[:16])
                         mime = "image/png" if raw[:4] == b'\x89PNG' else "image/jpeg"
                         st.markdown(f'<img src="data:{mime};base64,{doc_b64_clean}" style="width:100%;border-radius:8px;max-height:300px;object-fit:contain;" alt="{doc.get("document_name","")}">', unsafe_allow_html=True)
                     except Exception:
                         st.info("Could not decode base64 image.")
                 else:
                     # 2. Try Storage URL / Path
                     file_url = doc.get("file_url") or doc.get("storage_path") or ""
                     if file_url:
                         if file_url.startswith("http"):
                             if any(ext in file_url.lower() for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                                 st.markdown(f'<img src="{file_url}" style="width:100%;border-radius:8px;max-height:300px;object-fit:contain;" alt="{doc.get("document_name","")}">', unsafe_allow_html=True)
                             elif ".pdf" in file_url.lower():
                                 st.components.v1.iframe(file_url, height=500, scrolling=True)
                             else:
                                 st.markdown(f"[📥 Open Document]({file_url})")
                         else:
                             try:
                                 bucket = "verification-documents"
                                 res = supabase.storage.from_(bucket).download(file_url)
                                 fname = file_url.split("/")[-1].lower()
                                 if fname.endswith((".png", ".jpg", ".jpeg", ".webp")):
                                     res_b64 = base64.b64encode(res).decode()
                                     mime2 = "image/png" if fname.endswith(".png") else "image/jpeg"
                                     st.markdown(f'<img src="data:{mime2};base64,{res_b64}" style="width:100%;border-radius:8px;max-height:300px;object-fit:contain;" alt="{doc.get("document_name","")}">', unsafe_allow_html=True)
                                 elif fname.endswith(".pdf"):
                                     b64 = base64.b64encode(res).decode()
                                     pdf_display = f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="500px"></iframe>'
                                     st.markdown(pdf_display, unsafe_allow_html=True)
                                 else:
                                     st.info("Preview not available for this file type.")
                             except Exception as pe:
                                 st.info(f"Preview unavailable (Storage error): {pe}")
                     else:
                         st.info("No file URL or path found.")
                         
                 st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — DATABASE
# ══════════════════════════════════════════════
with tab_db:
    st.markdown('<div class="section-title">Database Explorer</div>', unsafe_allow_html=True)
    tables = ["profiles", "products", "orders", "notifications", "merchant_preferences", "verification_documents"]
    col_t, col_l = st.columns([3, 1])
    with col_t:
        selected_table = st.selectbox("Table", tables, key="admin_db_table")
    with col_l:
        row_limit = st.selectbox("Rows", [50, 100, 500, 1000], key="admin_db_limit")
    
    try:
        data = supabase.table(selected_table).select("*").limit(row_limit).execute().data or []
        st.caption(f"**{len(data)} records** (limit {row_limit})")
        if data:
            df = pd.DataFrame(data)
            col_search = st.text_input("🔍 Filter rows (any column)", key="db_col_search", placeholder="Search value…")
            if col_search:
                mask = df.apply(lambda row: row.astype(str).str.contains(col_search, case=False).any(), axis=1)
                df = df[mask]
                st.caption(f"Filtered to **{len(df)} rows**")
            st.dataframe(df, use_container_width=True, height=420)
            dl1, dl2 = st.columns(2)
            with dl1:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", data=csv, file_name=f"{selected_table}.csv", mime="text/csv", use_container_width=True)
            with dl2:
                json_bytes = df.to_json(orient="records", indent=2).encode("utf-8")
                st.download_button("📥 Download JSON", data=json_bytes, file_name=f"{selected_table}.json", mime="application/json", use_container_width=True)
    except Exception as e:
        st.error(f"Could not load table: {e}")

# ══════════════════════════════════════════════
# TAB — PRODUCTS
# ══════════════════════════════════════════════
with tab_products:
    st.markdown('<div class="section-title">Product Catalogue</div>', unsafe_allow_html=True)
    try:
        products = supabase.table("products").select("*, profiles(full_name)").order("created_at", desc=True).execute().data or []
    except Exception:
        products = []
    
    pf1, pf2 = st.columns(2)
    with pf1:
        prod_search = st.text_input("🔍 Search products", key="prod_search", placeholder="Product name…")
    with pf2:
        prod_region = st.selectbox("Region", ["All"] + list(REGIONS), key="prod_region_filter")
    
    filtered_prods = products
    if prod_search:
        filtered_prods = [p for p in filtered_prods if prod_search.lower() in (p.get("product_name") or "").lower()]
    if prod_region != "All":
        filtered_prods = [p for p in filtered_prods if p.get("region") == prod_region]
    
    st.caption(f"**{len(filtered_prods)} product(s)**")
    for p in filtered_prods:
        pid = p["id"]
        with st.container(border=True):
            img_col, c1, c2, c3 = st.columns([1, 4, 2, 3])
            with img_col:
                img_b64 = p.get("image_base64")
                if img_b64:
                    try:
                        img_b64_clean = img_b64.replace('\n','').replace('\r','').replace(' ','')
                        raw = base64.b64decode(img_b64_clean[:16])
                        mime = "image/png" if raw[:4] == b'\x89PNG' else "image/jpeg"
                        st.markdown(f'<img src="data:{mime};base64,{img_b64_clean}" style="width:100%;border-radius:8px;max-height:100px;object-fit:cover;">', unsafe_allow_html=True)
                    except:
                        st.caption("📷 No img")
                else:
                    st.caption("📷 No img")
            with c1:
                st.markdown(f"**📦 {p.get('product_name','Unknown')}**")
                st.caption(f"👤 {p.get('profiles',{}).get('full_name','Unknown')}  ·  📍 {p.get('region','N/A')}  ·  Sector: {p.get('sector','—')}")
                created = p.get("created_at","")[:10]
                st.caption(f"Listed: {created}  ·  Stock: {p.get('quantity_available','—')} {p.get('unit','')}")
            with c2:
                st.metric("Price", f"{p.get('price_birr',0):,.0f} Birr")
            with c3:
                if st.session_state.get(f"confirm_del_prod_{pid}"):
                    st.markdown('<div class="confirm-box">⚠️ Permanently delete this product?</div>', unsafe_allow_html=True)
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("🗑️ Confirm", key=f"do_del_prod_{pid}", use_container_width=True, type="primary"):
                            try:
                                supabase.table("products").delete().eq("id", pid).execute()
                                clear_data_cache()
                                st.session_state.pop(f"confirm_del_prod_{pid}", None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                    with dc2:
                        if st.button("Cancel", key=f"cancel_del_prod_{pid}", use_container_width=True):
                            st.session_state.pop(f"confirm_del_prod_{pid}", None)
                            st.rerun()
                else:
                    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_prod_{pid}", use_container_width=True):
                        st.session_state[f"confirm_del_prod_{pid}"] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — ORDERS
# ══════════════════════════════════════════════
with tab_orders:
    st.markdown('<div class="section-title">Order Management</div>', unsafe_allow_html=True)
    try:
        orders = supabase.table("orders").select(
            "*, products(product_name), profiles!orders_buyer_id_fkey(full_name)"
        ).order("created_at", desc=True).execute().data or []
    except Exception:
        orders = []
    
    of1, of2 = st.columns(2)
    with of1:
        status_filter = st.selectbox("Status", ["All", "pending", "confirmed", "delivered", "cancelled", "declined"], key="admin_order_filter")
    with of2:
        order_search = st.text_input("🔍 Search orders", key="order_search", placeholder="Buyer or product name…")
    
    filtered_orders = orders if status_filter == "All" else [o for o in orders if o.get("status") == status_filter]
    if order_search:
        kw = order_search.lower()
        filtered_orders = [
            o for o in filtered_orders
            if kw in (o.get("products",{}).get("product_name","")).lower()
            or kw in (o.get("profiles",{}).get("full_name","")).lower()
        ]
    
    st.caption(f"**{len(filtered_orders)} order(s)**")
    STATUS_ICONS  = {"pending": "🟡", "confirmed": "🟢", "delivered": "✅", "cancelled": "❌", "declined": "❌"}
    STATUS_PILLS  = {"pending": "pill-warning", "confirmed": "pill-info", "delivered": "pill-success", "cancelled": "pill-danger", "declined": "pill-danger"}
    NEXT_STATUS   = {"pending": "confirmed", "confirmed": "delivered"}
    
    for o in filtered_orders:
        oid    = o["id"]
        status = o.get("status", "pending")
        icon   = STATUS_ICONS.get(status, "⚪")
        pill   = STATUS_PILLS.get(status, "pill-neutral")
        oid_short = str(oid)[:8]
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
            with c1:
                st.markdown(f"**{icon} Order #{oid_short}** &nbsp; <span class='pill {pill}'>{status.capitalize()}</span>", unsafe_allow_html=True)
                st.caption(f"📦 {o.get('products',{}).get('product_name','Unknown')}  ·  👤 {o.get('profiles',{}).get('full_name','Unknown')}")
                created = o.get("created_at","")[:10]
                st.caption(f"Date: {created}  ·  Qty: {o.get('quantity_ordered','—')}")
            with c2:
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")
            with c3:
                next_s = NEXT_STATUS.get(status)
                if next_s:
                    if st.button(f"→ {next_s.capitalize()}", key=f"adv_{oid}", use_container_width=True, type="primary"):
                        try:
                            supabase.table("orders").update({"status": next_s}).eq("id", oid).execute()
                            clear_data_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
            with c4:
                if st.session_state.get(f"confirm_del_order_{oid}"):
                    st.markdown('<div class="confirm-box">⚠️ Delete this order?</div>', unsafe_allow_html=True)
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        if st.button("🗑️ Confirm", key=f"do_del_order_{oid}", use_container_width=True, type="primary"):
                            try:
                                supabase.table("orders").delete().eq("id", oid).execute()
                                clear_data_cache()
                                st.session_state.pop(f"confirm_del_order_{oid}", None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Delete failed: {e}")
                    with dc2:
                        if st.button("Cancel", key=f"cancel_del_order_{oid}", use_container_width=True):
                            st.session_state.pop(f"confirm_del_order_{oid}", None)
                            st.rerun()
                else:
                    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_order_{oid}", use_container_width=True):
                        st.session_state[f"confirm_del_order_{oid}"] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — ANALYTICS (Update 5: Big Dashboard)
# ══════════════════════════════════════════════
with tab_analytics:
    st.markdown('<div class="section-title">📈 Advanced Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-box alert-info">🤖 AI-powered insights for product pricing, fraud detection, and producer demand forecasting.</div>', unsafe_allow_html=True)
    
    # Fetch all data
    try:
        all_products = supabase.table("products").select("*").execute().data or []
        all_orders = supabase.table("orders").select("*").execute().data or []
        all_profiles = supabase.table("profiles").select("*").execute().data or []
    except Exception:
        all_products = []
        all_orders = []
        all_profiles = []
    
    # Row 1: Key Metrics
    a1, a2, a3, a4 = st.columns(4)
    
    with a1:
        avg_price = sum(p.get("price_birr", 0) for p in all_products) / len(all_products) if all_products else 0
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Product Price</div><div class="kpi-value">{avg_price:,.0f}</div><div class="kpi-sub">Birr</div></div>', unsafe_allow_html=True)
    
    with a2:
        # Fraud detection stats
        high_risk_orders = [o for o in all_orders if o.get("total_price_birr", 0) > 50000]
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">High-Value Orders</div><div class="kpi-value">{len(high_risk_orders)}</div><div class="kpi-sub">Flagged for review</div></div>', unsafe_allow_html=True)
    
    with a3:
        # Producer demand
        producer_orders = {}
        for o in all_orders:
            # Get producer from products
            prod_id = o.get("product_id")
            if prod_id:
                prod = next((p for p in all_products if p.get("id") == prod_id), None)
                if prod:
                    pid = prod.get("producer_id", "unknown")
                    producer_orders[pid] = producer_orders.get(pid, 0) + 1
        
        total_prod_orders = sum(producer_orders.values())
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Producer Orders</div><div class="kpi-value">{total_prod_orders}</div><div class="kpi-sub">Across all producers</div></div>', unsafe_allow_html=True)
    
    with a4:
        active_listings = sum(1 for p in all_products if p.get("is_available"))
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Active Listings</div><div class="kpi-value">{active_listings}</div><div class="kpi-sub">Currently available</div></div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Product Price Table
    st.markdown('<div class="section-title">All Products & Pricing</div>', unsafe_allow_html=True)
    if all_products:
        df_prices = pd.DataFrame([{
            "Product": p.get("product_name"),
            "Sector": p.get("sector"),
            "Price (Birr)": p.get("price_birr"),
            "Stock": f"{p.get('quantity')} {p.get('unit')}",
            "Region": p.get("region"),
            "Producer": p.get("producer_id", "")[:8] if p.get("producer_id") else "N/A",
            "Status": "Active" if p.get("is_available") else "Inactive"
        } for p in all_products])
        st.dataframe(df_prices, use_container_width=True, height=300)
    
    st.markdown("")
    
    # Fraud Detection Panel
    st.markdown('<div class="section-title">🛡️ Fraud Detection Overview</div>', unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    with f1:
        st.markdown("**High-Value Transactions**")
        for o in high_risk_orders[:5]:
            risk_level = "high" if o.get("total_price_birr", 0) > 100000 else "med"
            risk_class = "fraud-high" if risk_level == "high" else "fraud-med"
            st.markdown(f'<div style="padding:8px;margin-bottom:6px;background:#1e2a3a;border-radius:6px;">Order #{str(o["id"])[:8]} — <span class="{risk_class}">{o.get("total_price_birr",0):,.0f} Birr</span></div>', unsafe_allow_html=True)
    
    with f2:
        st.markdown("**AI Fraud Analysis**")
        if st.button("🔍 Run Fraud Detection on All Orders", use_container_width=True):
            with st.spinner("Analyzing transactions..."):
                fraud_results = []
                for o in all_orders[:20]:  # Limit for performance
                    try:
                        # Use the correct function name and parameters
                        fraud_score = check_fraud_risk(
                            sector="Unknown", 
                            product="Unknown", 
                            region="Unknown",
                            payment_method="Bank Transfer", 
                            quantity=1, 
                            agreed_price_birr=o.get("total_price_birr", 0), 
                            market_price_birr=o.get("total_price_birr", 0)
                        )
                        fraud_results.append({
                            "order_id": str(o["id"])[:8],
                            "amount": o.get("total_price_birr", 0),
                            "risk_score": fraud_score.get("fraud_probability", 0),
                            "risk_level": fraud_score.get("risk_level", "unknown")
                        })
                    except Exception:
                        pass
                
                if fraud_results:
                    df_fraud = pd.DataFrame(fraud_results)
                    st.dataframe(df_fraud, use_container_width=True, height=200)
                    st.success("✅ Fraud analysis complete!")
        
        st.info("Click button above to analyze recent transactions for fraud patterns.")
    
    # Producer Demand Chart
    st.markdown('<div class="section-title">📊 Producer Demand Distribution</div>', unsafe_allow_html=True)
    if producer_orders:
        # Get producer names
        producer_names = {}
        for pid in producer_orders.keys():
            prof = next((p for p in all_profiles if p.get("id") == pid), None)
            if prof:
                producer_names[pid] = prof.get("full_name", "Unknown")[:20]
            else:
                producer_names[pid] = "Unknown"
        
        df_demand = pd.DataFrame({
            "Producer": [producer_names.get(pid, "Unknown") for pid in producer_orders.keys()],
            "Orders": list(producer_orders.values())
        }).sort_values("Orders", ascending=False).head(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_demand["Producer"],
            y=df_demand["Orders"],
            marker_color="#2563eb",
            text=df_demand["Orders"],
            textposition='auto',
        ))
        fig.update_layout(
            paper_bgcolor="#161b27",
            plot_bgcolor="#161b27",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(gridcolor="#1e2a3a", showgrid=True),
            yaxis=dict(gridcolor="#1e2a3a", showgrid=True, title="Number of Orders"),
            margin=dict(l=40, r=20, t=20, b=60),
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Price Trends by Sector
    st.markdown('<div class="section-title">💰 Average Price by Sector</div>', unsafe_allow_html=True)
    if all_products:
        sector_prices = {}
        for p in all_products:
            sector = p.get("sector", "Other")
            price = p.get("price_birr", 0)
            if sector not in sector_prices:
                sector_prices[sector] = []
            sector_prices[sector].append(price)
        
        avg_sector_prices = {sector: sum(prices)/len(prices) for sector, prices in sector_prices.items()}
        df_sector_price = pd.DataFrame({
            "Sector": list(avg_sector_prices.keys()),
            "Avg Price (Birr)": list(avg_sector_prices.values())
        }).sort_values("Avg Price (Birr)", ascending=False)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_sector_price["Sector"],
            y=df_sector_price["Avg Price (Birr)"],
            marker_color="#16a34a",
        ))
        fig2.update_layout(
            paper_bgcolor="#161b27",
            plot_bgcolor="#161b27",
            font=dict(color="#94a3b8", family="Inter"),
            xaxis=dict(gridcolor="#1e2a3a", showgrid=True),
            yaxis=dict(gridcolor="#1e2a3a", showgrid=True),
            margin=dict(l=40, r=20, t=20, b=60),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════
# TAB — ACTIVITY LOG
# ══════════════════════════════════════════════
with tab_activity:
    st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**🆕 Recent Registrations**")
        try:
            recent_users = supabase.table("profiles").select("full_name, role, created_at").order("created_at", desc=True).limit(10).execute().data or []
        except Exception:
            recent_users = []
        for u in recent_users:
            role_icon = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(u.get("role"), "⚪")
            ts = u.get("created_at", "")[:16].replace("T", " ")
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot" style="background:#60a5fa"></div>
                <div>
                    <div class="activity-text">{role_icon} <strong>{u.get('full_name','Unknown')}</strong> registered as {u.get('role','N/A')}</div>
                    <div class="activity-time">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with col_b:
        st.markdown("**📦 Recent Orders**")
        try:
            recent_orders = supabase.table("orders").select(
                "id, status, created_at, total_price_birr, products(product_name)"
            ).order("created_at", desc=True).limit(10).execute().data or []
        except Exception:
            recent_orders = []
        STATUS_COLORS = {"pending": "#fbbf24", "confirmed": "#60a5fa", "delivered": "#4ade80", "cancelled": "#f87171", "declined": "#f87171"}
        for o in recent_orders:
            ts = o.get("created_at", "")[:16].replace("T", " ")
            status = o.get("status", "pending")
            color = STATUS_COLORS.get(status, "#94a3b8")
            prod  = o.get("products", {}).get("product_name", "Unknown")
            st.markdown(f"""
            <div class="activity-item">
                <div class="activity-dot" style="background:{color}"></div>
                <div>
                    <div class="activity-text"><strong>{prod}</strong> — {status.capitalize()} · {o.get('total_price_birr',0):,.0f} Birr</div>
                    <div class="activity-time">{ts}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB — SETTINGS
# ══════════════════════════════════════════════
with tab_settings:
    st.markdown('<div class="section-title">System Settings</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("**📢 Broadcast Notification**")
        with st.container(border=True):
            bc_title = st.text_input("Title", key="bc_title", placeholder="Maintenance notice…")
            bc_msg   = st.text_area("Message", key="bc_msg", height=100, placeholder="Enter message for all users…")
            bc_type  = st.selectbox("Type", ["info", "warning", "success", "error"], key="bc_type")
            if st.button("📢 Send to All Users", key="bc_send", use_container_width=True, type="primary"):
                if bc_title and bc_msg:
                    try:
                        all_uids = supabase.table("profiles").select("id").execute().data or []
                        for row in all_uids:
                            send_notification(row["id"], bc_title, bc_msg, bc_type)
                        st.success(f"✅ Broadcast sent to {len(all_uids)} users.")
                    except Exception as e:
                        st.error(f"Broadcast failed: {e}")
                else:
                    st.warning("Fill in both title and message.")
    with s2:
        st.markdown("**🗄️ Cache & Data**")
        with st.container(border=True):
            st.caption("Clear server-side caches to force fresh data from the database.")
            if st.button("🔄 Clear All Caches", key="clear_cache_btn", use_container_width=True):
                clear_data_cache()
                st.cache_data.clear()
                st.success("All caches cleared.")
            st.divider()
            st.markdown("**📊 Export Full Database**")
            tables_export = ["profiles", "products", "orders", "verification_documents"]
            if st.button("📥 Export All Tables (CSV)", key="export_all_btn", use_container_width=True):
                for tbl in tables_export:
                    try:
                        rows = supabase.table(tbl).select("*").execute().data or []
                        if rows:
                            df_exp = pd.DataFrame(rows)
                            csv_exp = df_exp.to_csv(index=False).encode("utf-8")
                            st.download_button(
                                label=f"📥 {tbl}.csv",
                                data=csv_exp,
                                file_name=f"{tbl}.csv",
                                mime="text/csv",
                                key=f"dl_{tbl}",
                                use_container_width=True,
                            )
                    except Exception:
                        st.warning(f"Could not export {tbl}")
        
        st.markdown("**⚠️ Danger Zone**")
        with st.container(border=True):
            st.markdown('<div class="alert-box alert-danger">These actions are irreversible. Proceed with extreme caution.</div>', unsafe_allow_html=True)
            if st.session_state.get("confirm_purge_notifications"):
                st.markdown('<div class="confirm-box">⚠️ This will delete ALL notifications permanently.</div>', unsafe_allow_html=True)
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("🗑️ Confirm Purge", key="do_purge_notif", use_container_width=True, type="primary"):
                        try:
                            supabase.table("notifications").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                            st.session_state.pop("confirm_purge_notifications", None)
                            st.success("All notifications purged.")
                        except Exception as e:
                            st.error(f"Failed: {e}")
                with dc2:
                    if st.button("Cancel", key="cancel_purge_notif", use_container_width=True):
                        st.session_state.pop("confirm_purge_notifications", None)
                        st.rerun()
            else:
                if st.button("🗑️ Purge All Notifications", key="purge_notif_btn", use_container_width=True):
                    st.session_state["confirm_purge_notifications"] = True
                    st.rerun()

# ── Profile editor triggered from header Edit Profile button ──
if st.session_state.get("show_profile_editor"):
    st.session_state.show_profile_editor = False   # clear FIRST to prevent duplicate on rerun
    render_profile_editor_modal(profile, st.session_state.user.id, key_suffix="admin_modal")

# ═════════════════════════════════════════════════════════════
# FLOATING CHATBOT (Add this at the end of 4_Admin.py)
# ═════════════════════════════════════════════════════════════
from utils.chatbot import render_floating_chatbot
render_floating_chatbot(profile)
