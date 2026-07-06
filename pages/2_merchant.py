"""Merchant Dashboard Page."""
import sys
import os
import datetime
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme, render_page_header
from utils.constants import REGIONS, SECTORS
from utils.db_helpers import supabase, cached_query, clear_data_cache, send_notification
from utils.verification import check_verification_status, render_document_upload
from utils.shared_ui import render_browse_tab, render_notifications_tab, render_profile_edit_tab
from utils.pdf_generator import generate_agreement_pdf

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

render_page_header("🏬", "Merchant Dashboard",
                   f"Welcome, **{profile.get('full_name', 'Merchant')}** · 📍 {profile.get('region', 'N/A')}")

if not verif_status["is_verified"]:
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "merchant")
    with tab_browse:
        st.info("You can only browse products until verified.")
        render_browse_tab("merchant", profile)
    st.stop()

tab_browse, tab_orders, tab_agree, tab_history, tab_pref, tab_notif, tab_profile = st.tabs([
    "🛒 Browse Products", "📋 My Orders", "📄 Agreements",
    "📜 History", "⚙️ Preferences", "🔔 Notifications", "👤 Profile"
])

with tab_browse:
    render_browse_tab("merchant", profile)

with tab_orders:
    st.subheader("📋 My Orders")
    try:
        my_orders = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, price_birr, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).neq("status", "delivered").order("created_at", desc=True).limit(50).execute().data or []
    except Exception as e:
        st.error(f"Could not load orders: {e}")
        my_orders = []
    if not my_orders:
        st.info("You have not placed any orders yet.")
    else:
        for o in my_orders:
            prod = o.get("products") or {}
            status = o.get("status", "pending")
            status_icon = {"pending": "🟡", "confirmed": "🟢", "cancelled": "🔴"}.get(status, "⚪")
            with st.container(border=True):
                st.markdown(f"**{prod.get('product_name','Unknown')}** · {prod.get('sector','')} · Grade **{prod.get('quality_grade','')}**")
                st.caption(f"📍 {prod.get('region','N/A')} · 📅 {str(o.get('created_at',''))[:10]}")
                st.metric("Qty", f"{o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")
                st.caption(f"**Status:** {status_icon} {status.capitalize()}")
                if status == "pending":
                    if st.button("❌ Cancel Order", key=f"cancel_{o['id']}"):
                        try:
                            supabase.table("orders").update({"status": "cancelled"}).eq("id", o["id"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

with tab_agree:
    st.subheader("📄 Supply Agreements")
    try:
        producer_requests = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).eq("producer_confirmed", True).eq("merchant_confirmed", False).execute().data or []
    except Exception:
        producer_requests = []
    if producer_requests:
        st.markdown("### 📩 Pending Agreement Requests")
        for o in producer_requests:
            prod = o.get("products") or {}
            producer_id = prod.get("producer_id")
            with st.container(border=True):
                st.markdown(f"**{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                st.caption(f"💰 Total: {o.get('total_price_birr',0):,.0f} Birr · 📦 Qty: {o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                ba1, ba2 = st.columns(2)
                with ba1:
                    if st.button("✅ Accept", key=f"m_accept_{o['id']}", type="primary", use_container_width=True):
                        try:
                            supabase.table("orders").update({"merchant_confirmed": True, "status": "confirmed"}).eq("id", o["id"]).execute()
                            if producer_id:
                                send_notification(recipient_id=producer_id, title="Agreement Accepted", message=f"Merchant accepted your agreement.", notif_type="success", order_id=o["id"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                with ba2:
                    if st.button("❌ Decline", key=f"m_decline_{o['id']}", use_container_width=True):
                        try:
                            supabase.table("orders").update({"status": "cancelled"}).eq("id", o["id"]).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

with tab_history:
    st.subheader("📜 Purchase History")
    try:
        mh_orders = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).eq("status", "delivered").order("created_at", desc=True).execute().data or []
    except Exception:
        mh_orders = []
    if not mh_orders:
        st.info("No delivered orders yet.")
    else:
        for o in mh_orders:
            prod = o.get("products") or {}
            with st.container(border=True):
                st.markdown(f"✅ **{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                st.metric("Qty", f"{o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")

with tab_pref:
    st.subheader("⚙️ Buying Preferences")
    try:
        pref_res = supabase.table("merchant_preferences").select("*").eq("merchant_id", user_id).execute()
        existing_pref = pref_res.data[0] if pref_res.data else None
    except Exception:
        existing_pref = None
    with st.form("merchant_pref_form"):
        pc1, pc2 = st.columns(2)
        with pc1:
            pref_sectors = st.multiselect("🏭 Preferred Sectors", SECTORS, default=(existing_pref.get("preferred_sectors") or []) if existing_pref else [])
            pref_regions = st.multiselect("📍 Preferred Regions", REGIONS, default=(existing_pref.get("preferred_regions") or []) if existing_pref else [])
        with pc2:
            max_budget = st.number_input("💰 Max Budget (Birr)", min_value=0.0, value=float(existing_pref.get("max_budget_birr") or 50000) if existing_pref else 50000.0, step=1000.0)
            pref_payment = st.selectbox("💳 Payment Method", ["Bank Transfer", "Cash on Delivery", "Mobile Money", "Letter of Credit"])
        submitted = st.form_submit_button("💾 Save Preferences", type="primary", use_container_width=True)
        if submitted:
            pref_payload = {
                "merchant_id": user_id,
                "preferred_sectors": pref_sectors,
                "preferred_regions": pref_regions,
                "max_budget_birr": max_budget,
                "preferred_payment": pref_payment,
            }
            try:
                if existing_pref:
                    supabase.table("merchant_preferences").update(pref_payload).eq("merchant_id", user_id).execute()
                else:
                    supabase.table("merchant_preferences").insert(pref_payload).execute()
                st.success("✅ Preferences saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

with tab_notif:
    render_notifications_tab(user_id)

with tab_profile:
    render_profile_edit_tab(profile, user_id)
