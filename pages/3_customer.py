"""Customer Dashboard Page."""
import sys
import os
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme, render_page_header
from utils.db_helpers import supabase, send_notification
from utils.verification import check_verification_status, render_document_upload
from utils.shared_ui import render_browse_tab, render_notifications_tab, render_profile_edit_tab

inject_theme()

if st.session_state.get("user") is None:
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "customer":
    st.error("Access denied. This page is for customers only.")
    st.stop()

user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)

render_page_header("🛒", "Customer Dashboard",
                   f"Welcome, **{profile.get('full_name', 'Customer')}**")

if not verif_status["is_verified"]:
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "customer")
    with tab_browse:
        st.info("You can only browse until verified.")
        render_browse_tab("customer", profile)
    st.stop()

tab_browse, tab_orders, tab_history, tab_notif, tab_profile = st.tabs([
    "🛒 Browse", "📋 My Orders", "📜 History", "🔔 Notifications", "👤 Profile"
])

with tab_browse:
    render_browse_tab("customer", profile)

with tab_orders:
    st.subheader("📋 My Orders")
    try:
        my_orders = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).neq("status", "delivered").order("created_at", desc=True).limit(50).execute().data or []
    except Exception:
        my_orders = []
    if not my_orders:
        st.info("No active orders yet.")
    else:
        for o in my_orders:
            prod = o.get("products") or {}
            status = o.get("status", "pending")
            status_icon = {"pending": "🟡", "confirmed": "🟢", "cancelled": "🔴"}.get(status, "⚪")
            with st.container(border=True):
                st.markdown(f"**{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                st.caption(f"📍 {prod.get('region','N/A')} · 📅 {str(o.get('created_at',''))[:10]}")
                st.caption(f"{status_icon} **{status.capitalize()}**")
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")
                if status == "pending":
                    if st.button("❌ Cancel", key=f"cust_cancel_{o['id']}", use_container_width=True):
                        try:
                            supabase.table("orders").update({"status": "cancelled"}).eq("id", o["id"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

with tab_history:
    st.subheader("📜 Purchase History")
    try:
        mh_orders = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).eq("status", "delivered").order("created_at", desc=True).limit(50).execute().data or []
    except Exception:
        mh_orders = []
    if not mh_orders:
        st.info("No delivered orders yet.")
    else:
        total_spent = sum(float(o.get("total_price_birr") or 0) for o in mh_orders)
        st.metric("Total Spent", f"{total_spent:,.0f} Birr")
        for o in mh_orders:
            prod = o.get("products") or {}
            with st.container(border=True):
                st.markdown(f"✅ **{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")

with tab_notif:
    render_notifications_tab(user_id)

with tab_profile:
    render_profile_edit_tab(profile, user_id)
