"""Admin Dashboard Page."""
import sys
import os
import base64
import datetime
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme, render_page_header
from utils.constants import REGIONS
from utils.db_helpers import supabase, cached_get_profile, send_notification, clear_data_cache

inject_theme()

if st.session_state.get("user") is None:
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "admin":
    st.error("Access denied. Admin only.")
    st.stop()

render_page_header("🛡️", "Admin Panel", "System Administration & User Management")

tab_overview, tab_users, tab_verify, tab_docs, tab_db, tab_products, tab_orders = st.tabs([
    "📊 Overview", "👥 All Users", "✅ Verify Users", "📄 Documents", "🗄️ Database", "📦 Products", "📋 Orders"
])

with tab_overview:
    st.subheader("📊 System Overview")
    try:
        total_users = supabase.table("profiles").select("*", count="exact").execute().count or 0
        total_producers = supabase.table("profiles").select("*", count="exact").eq("role", "producer").execute().count or 0
        total_merchants = supabase.table("profiles").select("*", count="exact").eq("role", "merchant").execute().count or 0
        total_customers = supabase.table("profiles").select("*", count="exact").eq("role", "customer").execute().count or 0
        total_products = supabase.table("products").select("*", count="exact").execute().count or 0
        total_orders = supabase.table("orders").select("*", count="exact").execute().count or 0
    except Exception:
        total_users = total_producers = total_merchants = total_customers = 0
        total_products = total_orders = 0
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Users", total_users)
    with m2: st.metric("Products", total_products)
    with m3: st.metric("Orders", total_orders)
    with m4: st.metric("Merchants", total_merchants)
    col1, col2, col3 = st.columns(3)
    with col1: st.info(f"🚜 **Producers:** {total_producers}")
    with col2: st.success(f"🏬 **Merchants:** {total_merchants}")
    with col3: st.warning(f"🛒 **Customers:** {total_customers}")

with tab_users:
    st.subheader("👥 User Management")
    fcol1, fcol2 = st.columns(2)
    with fcol1: filter_role = st.selectbox("Filter by Role", ["All", "producer", "merchant", "customer", "admin"], key="admin_filter_role")
    with fcol2: search_user = st.text_input("🔍 Search", key="admin_search_user")
    try:
        query = supabase.table("profiles").select("*")
        if filter_role != "All": query = query.eq("role", filter_role)
        users = query.order("created_at", desc=True).execute().data or []
        if search_user:
            kw = search_user.lower()
            users = [u for u in users if kw in u.get("full_name", "").lower()]
    except Exception:
        users = []
    st.markdown(f"**{len(users)} user(s) found**")
    for user in users:
        verified = user.get("is_verified", False)
        role_badge = {"producer": "🚜", "merchant": "🏬", "customer": "🛒", "admin": "🛡️"}.get(user.get("role"), "⚪")
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 2])
            with c1:
                st.markdown(f"**{role_badge} {user.get('full_name','Unknown')}** {'✅' if verified else '⏳'}")
                st.caption(f"📍 {user.get('region','N/A')} · 📞 {user.get('phone','N/A')}")
            with c2:
                st.metric("Role", user.get("role", "N/A").capitalize())
            with c3:
                if not verified:
                    if st.button("✅ Verify", key=f"verify_{user['id']}", use_container_width=True):
                        try:
                            supabase.table("profiles").update({"is_verified": True}).eq("id", user["id"]).execute()
                            send_notification(user["id"], "✅ Verified", "Your account is verified.", "success")
                            clear_data_cache()
                            st.rerun()
                        except Exception as _ve:
                            st.error(f"Verification failed: {_ve}")
                else:
                    st.success("Verified")

with tab_verify:
    st.subheader("✅ Verification Queue")
    try:
        pending_users = supabase.table("profiles").select("*").eq("is_verified", False).order("created_at", desc=True).execute().data or []
    except Exception:
        pending_users = []
    if not pending_users:
        st.info("No pending verifications.")
    else:
        st.warning(f"⏳ {len(pending_users)} awaiting verification")
        for user in pending_users:
            with st.container(border=True):
                st.markdown(f"**{user.get('full_name','Unknown')}**")
                st.caption(f"📍 {user.get('region','N/A')} · Role: **{user.get('role','N/A').capitalize()}**")
                if st.button("✅ Verify", key=f"vp_{user['id']}", type="primary", use_container_width=True):
                    supabase.table("profiles").update({"is_verified": True}).eq("id", user["id"]).execute()
                    send_notification(user["id"], "✅ Verified", "Your account is verified.", "success")
                    clear_data_cache()
                    st.rerun()

with tab_docs:
    st.subheader("📄 Document Verification")
    try:
        all_docs = supabase.table("verification_documents").select("*").order("uploaded_at", desc=True).execute().data or []
    except Exception:
        all_docs = []
    if not all_docs:
        st.info("No documents uploaded yet.")
    else:
        for doc in all_docs:
            status_icon = "✅" if doc.get("is_verified") else "⏳"
            user_info = cached_get_profile(doc.get("user_id")) or {}
            with st.container(border=True):
                st.markdown(f"**{status_icon} {doc.get('document_name')}**")
                st.caption(f"👤 {user_info.get('full_name', 'Unknown')} ({user_info.get('role', 'N/A')})")
                st.caption(f"Type: {doc.get('document_type')} · {doc.get('file_size', 0) / 1024:.1f} KB")
                if not doc.get("is_verified"):
                    if st.button("✅ Verify", key=f"vdoc_{doc['id']}", type="primary"):
                        try:
                            supabase.table("verification_documents").update({"is_verified": True, "verified_at": datetime.datetime.now().isoformat()}).eq("id", doc["id"]).execute()
                            supabase.table("profiles").update({"is_verified": True}).eq("id", doc.get("user_id")).execute()
                            send_notification(doc.get("user_id"), "✅ Document Verified", "Your document is approved.", "success")
                            clear_data_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")

with tab_db:
    st.subheader("🗄️ Database")
    tables = ["profiles", "products", "orders", "notifications", "merchant_preferences", "verification_documents"]
    selected_table = st.selectbox("Select Table", tables, key="admin_db_table")
    try:
        data = supabase.table(selected_table).select("*").execute().data or []
        st.markdown(f"**{len(data)} records**")
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Download CSV", data=csv, file_name=f"{selected_table}.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Could not load: {e}")

with tab_products:
    st.subheader("📦 All Products")
    try:
        products = supabase.table("products").select("*, profiles(full_name)").order("created_at", desc=True).execute().data or []
    except Exception:
        products = []
    st.markdown(f"**{len(products)} product(s)**")
    for p in products:
        with st.container(border=True):
            st.markdown(f"**{p.get('product_name','Unknown')}** · {p.get('sector','')}")
            st.caption(f"👤 {p.get('profiles',{}).get('full_name','Unknown')} · 📍 {p.get('region','N/A')}")
            st.metric("Price", f"{p.get('price_birr',0):,.0f} Birr")

with tab_orders:
    st.subheader("📋 All Orders")
    try:
        orders = supabase.table("orders").select("*, products(product_name), profiles!orders_buyer_id_fkey(full_name)").order("created_at", desc=True).execute().data or []
    except Exception:
        orders = []
    status_filter = st.selectbox("Filter", ["All", "pending", "confirmed", "delivered", "cancelled"], key="admin_order_filter")
    filtered_orders = orders if status_filter == "All" else [o for o in orders if o.get("status") == status_filter]
    st.markdown(f"**{len(filtered_orders)} order(s)**")
    for o in filtered_orders:
        status_icon = {"pending": "🟡", "confirmed": "🟢", "delivered": "✅", "cancelled": "❌"}.get(o.get("status"), "⚪")
        with st.container(border=True):
            st.markdown(f"**{status_icon} Order #{str(o.get('id',''))[:8]}**")
            st.caption(f"📦 {o.get('products',{}).get('product_name','Unknown')} · 👤 {o.get('profiles',{}).get('full_name','Unknown')}")
            st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")
