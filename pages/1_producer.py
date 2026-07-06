"""Producer Dashboard Page."""
import sys
import os
import base64
import datetime
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.theme import inject_theme, render_page_header
from utils.constants import REGIONS, SECTORS, UNITS
from utils.db_helpers import supabase, cached_query, clear_data_cache, reduce_product_stock, send_notification
from utils.verification import check_verification_status, render_document_upload
from utils.shared_ui import (
    get_grades_for_product, map_grade_to_db, render_browse_tab,
    render_notifications_tab, render_profile_edit_tab,
)
from utils.pdf_generator import generate_agreement_pdf
from src.matching_engine import rank_merchants
from src.price_engine import recommend_price
from src.demand_engine import forecast_demand
import plotly.graph_objects as go

inject_theme()

# ═════════════════════════════════════════════════════════════
# AUTH CHECK
# ═════════════════════════════════════════════════════════════
if st.session_state.get("user") is None:
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Go to Login", icon="🔐")
    st.stop()

profile = st.session_state.get("profile")
if profile is None or profile.get("role") != "producer":
    st.error("Access denied. This page is for producers only.")
    st.stop()

user_id = st.session_state.user.id
verif_status = check_verification_status(user_id)

render_page_header("🚜", "Producer Dashboard",
                   f"Welcome, **{profile.get('full_name','Producer')}** · 📍 {profile.get('region','')}")

# ═════════════════════════════════════════════════════════════
# VERIFICATION GATE
# ═════════════════════════════════════════════════════════════
if not verif_status["is_verified"]:
    tab_upload, tab_browse = st.tabs(["📄 Upload Documents", "🛒 Browse (Read Only)"])
    with tab_upload:
        render_document_upload(user_id, "producer")
    with tab_browse:
        st.info("You can only browse products until verified.")
        render_browse_tab("producer", profile)
    st.stop()

# ═════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════
tab_products, tab_demand, tab_incoming, tab_match, tab_agree, tab_history, tab_notif, tab_profile = st.tabs([
    "📦 My Products", "📈 Demand Forecast", "📬 Incoming Orders",
    "🤝 AI Matching", "📄 Agreements", "📜 History", "🔔 Notifications", "👤 Profile"
])

# ─── MY PRODUCTS ───
with tab_products:
    st.subheader("📦 My Products")
    my_products = cached_query("products", filters={"producer_id": user_id}, limit=200)

    if my_products:
        total_val = sum(p["price_birr"] * p["quantity"] for p in my_products)
        active = sum(1 for p in my_products if p.get("is_available"))
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Listed", len(my_products))
        m2.metric("Active", active)
        m3.metric("Est. Value", f"{total_val:,.0f} Birr")
        st.divider()

    with st.expander("➕ Add New Product", expanded=not bool(my_products)):
        with st.form("add_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_name = st.text_input("Product Name *", placeholder="e.g. Teff, Coffee")
                new_sector = st.selectbox("Sector *", SECTORS)
                available_grades = get_grades_for_product(new_sector, new_name)
                new_grade_ui = st.selectbox("Quality Grade *", available_grades)
                new_grade_db = map_grade_to_db(new_grade_ui)
                new_region = st.selectbox("Region *", REGIONS, index=REGIONS.index(profile.get("region", REGIONS[0])) if profile.get("region") in REGIONS else 0)
            with c2:
                new_qty = st.number_input("Quantity *", min_value=0.1, value=1.0)
                new_unit = st.selectbox("Unit *", UNITS)
                new_price = st.number_input("Price (Birr) *", min_value=1.0, value=100.0)
                new_avail = st.checkbox("Available", value=True)
            new_image = st.file_uploader("📷 Product Image (Optional)", type=["jpg", "jpeg", "png"], key="product_image_upload")
            new_image_base64 = None
            if new_image:
                try:
                    new_image_base64 = base64.b64encode(new_image.read()).decode('utf-8')
                except Exception as e:
                    st.warning(f"Could not process image: {e}")
            new_desc = st.text_area("Description", height=80)
            submitted = st.form_submit_button("✅ Add Product", type="primary", use_container_width=True)
        if submitted:
            if not new_name.strip():
                st.error("Product name required.")
            else:
                try:
                    product_data = {
                        "producer_id": user_id,
                        "product_name": new_name.strip(),
                        "sector": new_sector,
                        "quality_grade": new_grade_db,
                        "region": new_region,
                        "quantity": new_qty,
                        "unit": new_unit,
                        "price_birr": new_price,
                        "is_available": new_avail,
                        "description": f"[{new_grade_ui}] {new_desc.strip()}" if new_desc.strip() else f"[{new_grade_ui}]",
                    }
                    if new_image_base64:
                        product_data["image_base64"] = new_image_base64
                    supabase.table("products").insert(product_data).execute()
                    clear_data_cache()
                    st.success(f"✅ '{new_name}' listed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

    if not my_products:
        st.info("No products yet. Add your first product above.")
    else:
        for p in my_products:
            avail_badge = "🟢 Available" if p.get("is_available") else "🔴 Unavailable"
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 2, 2])
                with c1:
                    st.markdown(f"**{p['product_name']}** · {p['sector']} · Grade **{p['quality_grade']}**")
                    st.caption(f"📍 {p['region']} · {avail_badge}")
                with c2:
                    st.metric("Price", f"{p['price_birr']:,.0f} Birr")
                    st.caption(f"Qty: {p['quantity']} {p['unit']}")
                with c3:
                    if st.button("Toggle", key=f"tog_{p['id']}", use_container_width=True):
                        try:
                            supabase.table("products").update({"is_available": not p.get("is_available")}).eq("id", p["id"]).execute()
                            clear_data_cache()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                    confirm_del_key = f"confirm_del_{p['id']}"
                    if st.button("🗑️ Delete", key=f"del_{p['id']}", use_container_width=True):
                        st.session_state[confirm_del_key] = True
                    if st.session_state.get(confirm_del_key):
                        st.warning(f"Delete **{p['product_name']}**?")
                        dc1, dc2 = st.columns(2)
                        with dc1:
                            if st.button("✅ Yes", key=f"yes_del_{p['id']}", use_container_width=True, type="primary"):
                                try:
                                    supabase.table("products").delete().eq("id", p["id"]).execute()
                                    st.session_state[confirm_del_key] = False
                                    clear_data_cache()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Delete failed: {e}")
                        with dc2:
                            if st.button("✖ Cancel", key=f"no_del_{p['id']}", use_container_width=True):
                                st.session_state[confirm_del_key] = False
                                st.rerun()

# ─── DEMAND FORECAST ───
with tab_demand:
    st.subheader("📈 AI Demand Forecasting")
    products_for_forecast = cached_query("products", filters={"producer_id": user_id}, limit=200)
    if not products_for_forecast:
        st.info("Add products first to see forecasts.")
    else:
        product_names = [p["product_name"] for p in products_for_forecast]
        selected_product = st.selectbox("Select Product", product_names, key="demand_product_select")
        selected_p = next((x for x in products_for_forecast if x["product_name"] == selected_product), None)
        if selected_p:
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Stock", f"{selected_p['quantity']} {selected_p['unit']}")
            with col2: st.metric("Price", f"{selected_p['price_birr']:,.0f} Birr/{selected_p['unit']}")
            with col3: st.metric("Grade", selected_p.get('quality_grade', 'N/A'))
            forecast_horizon = st.selectbox("Period", ["Next 7 days", "Next 30 days", "Next 3 months", "Next 6 months"], key="demand_horizon")
            if st.button("🤖 Generate Forecast", type="primary", use_container_width=True):
                try:
                    with st.spinner("Running AI demand forecast…"):
                        forecast = forecast_demand(sector=selected_p["sector"], product=selected_p["product_name"], region=selected_p["region"], historical_data=None)
                    predicted = forecast.get("predicted_demand", 0)
                    confidence = forecast.get("confidence_interval", {})
                    trend = forecast.get("trend", "stable")
                    fcol1, fcol2, fcol3 = st.columns(3)
                    with fcol1: st.metric("Predicted Demand", f"{predicted:,.1f} {selected_p['unit']}")
                    with fcol2: st.metric("Range", f"{confidence.get('lower',0):,.0f} - {confidence.get('upper',0):,.0f}")
                    with fcol3:
                        trend_icon = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
                        st.metric("Trend", trend.capitalize(), delta=trend_icon)
                    st.info(f"💡 **Recommendation:** {forecast.get('recommendation', 'No recommendation')}")
                except Exception as e:
                    st.error(f"Forecast failed: {e}")

# ─── INCOMING ORDERS ───
with tab_incoming:
    st.subheader("📬 Incoming Orders")
    my_prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, order_by=None, limit=500)]
    if not my_prod_ids:
        st.info("No products yet.")
    else:
        try:
            incoming = supabase.table("orders").select("*, products(product_name, unit, sector, quality_grade, region), profiles(full_name, phone, region)").in_("product_id", my_prod_ids).neq("status", "delivered").order("created_at", desc=True).limit(50).execute().data or []
        except Exception as e:
            st.error(f"Could not load orders: {e}")
            incoming = []
        if not incoming:
            st.info("No orders yet.")
        else:
            for o in incoming:
                prod = o.get("products") or {}
                buyer = o.get("profiles") or {}
                status = o.get("status", "pending")
                status_icon = {"pending": "🟡", "confirmed": "🟢", "cancelled": "🔴"}.get(status, "⚪")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 2])
                    with c1:
                        st.markdown(f"**{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                        st.caption(f"👤 Buyer: **{buyer.get('full_name','Unknown')}** · 📞 {buyer.get('phone','N/A')}")
                        st.caption(f"📅 {str(o.get('created_at',''))[:10]} · {status_icon} **{status.capitalize()}**")
                    with c2:
                        st.metric("Qty", f"{o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                        st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")
                    with c3:
                        if status == "pending":
                            if st.button("✅ Confirm", key=f"confirm_{o['id']}", use_container_width=True):
                                try:
                                    supabase.table("orders").update({"status": "confirmed", "producer_confirmed": True}).eq("id", o["id"]).execute()
                                    send_notification(recipient_id=o["buyer_id"], title="✅ Order Confirmed", message=f"Your order for {prod.get('product_name','')} confirmed.", notif_type="success", order_id=str(o["id"]))
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")
                            if st.button("❌ Cancel", key=f"cancel_{o['id']}", use_container_width=True):
                                try:
                                    supabase.table("orders").update({"status": "cancelled"}).eq("id", o["id"]).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")
                        elif status == "confirmed":
                            if st.button("🚚 Mark Delivered", key=f"deliver_{o['id']}", use_container_width=True):
                                try:
                                    supabase.table("orders").update({"status": "delivered"}).eq("id", o["id"]).execute()
                                    send_notification(recipient_id=o["buyer_id"], title="🚚 Order Delivered", message=f"Your order for {prod.get('product_name','')} delivered.", notif_type="success", order_id=str(o["id"]))
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {e}")

# ─── AI MATCHING ───
with tab_match:
    st.subheader("🤝 AI Merchant Matching")
    my_products_m = cached_query("products", filters={"producer_id": user_id, "is_available": True}, limit=200)
    if not my_products_m:
        st.info("No available products.")
    else:
        product_names = [p["product_name"] for p in my_products_m]
        selected_name = st.selectbox("Select Product", product_names, key="match_product_select")
        p = next((x for x in my_products_m if x["product_name"] == selected_name), None)
        if p:
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Price", f"{p['price_birr']:,.0f} Birr/{p['unit']}")
            mc2.metric("Qty", f"{p['quantity']} {p['unit']}")
            mc3.metric("Grade", p.get("quality_grade",""))
            if st.button("🤖 Find Best Merchants", type="primary", use_container_width=True, key="run_match"):
                try:
                    with st.spinner("Running AI merchant matching…"):
                        merchants_raw = supabase.table("profiles").select("*").eq("role", "merchant").execute().data or []
                    if not merchants_raw:
                        st.warning("No merchants registered.")
                    else:
                        listing_data = {
                            "sector": p["sector"], "product_name": p["product_name"],
                            "price_birr": p["price_birr"], "quantity": p["quantity"],
                            "quality_grade": p["quality_grade"], "region": p["region"],
                            "is_verified": 1, "delivery_available": 1,
                            "producer_rating": 4.0, "producer_experience": 3,
                            "producer_tx": 0, "return_rate": 0.05,
                        }
                        merchant_list = [{
                            "id": m["id"], "name": m["full_name"],
                            "phone": m.get("phone"), "region": m.get("region"),
                            "preferred_sector": m.get("preferred_sector"),
                            "preferred_product": m.get("preferred_product"),
                            "max_budget_birr": m.get("max_budget_birr") or 0,
                            "preferred_quality": m.get("preferred_quality") or "Any",
                            "needs_delivery": m.get("needs_delivery") or False,
                            "is_verified": m.get("is_verified", True),
                            "rating": m.get("rating") or 4.0,
                            "total_transactions": m.get("total_transactions") or 0,
                            "years_in_business": m.get("years_in_business") or 1,
                            "return_rate": m.get("return_rate") or 0.05,
                            "payment_method": m.get("payment_method"),
                        } for m in merchants_raw]
                        ranked = rank_merchants(listing_data, merchant_list)
                        top_matches = [r for r in ranked if r["match_probability"] > 0.1][:5]
                        st.session_state["match_results"] = top_matches
                        st.session_state["match_product"] = p
                except Exception as e:
                    st.error(f"Matching failed: {e}")
            results = st.session_state.get("match_results")
            match_p = st.session_state.get("match_product")
            if results is not None and match_p and match_p["id"] == p["id"]:
                if not results:
                    st.info("No strong matches found.")
                else:
                    st.markdown(f"**Top {len(results)} matches for {p['product_name']}:**")
                    for r in results:
                        pct = r["match_probability"] * 100
                        badge = "🟢" if pct >= 60 else ("🟡" if pct >= 30 else "🔴")
                        with st.container(border=True):
                            st.markdown(f"{badge} **{r['name']}** — {pct:.1f}% match")
                            st.caption(f"📍 {r.get('region','N/A')} · 📞 {r.get('phone') or 'N/A'}")

# ─── AGREEMENTS ───
with tab_agree:
    st.subheader("📄 Supply Agreements")
    try:
        agree_orders = supabase.table("orders").select("*, products(product_name, sector, quality_grade, unit, region, producer_id), profiles!orders_buyer_id_fkey(full_name, phone, region)").eq("buyer_id", user_id).in_("status", ["confirmed", "delivered"]).order("created_at", desc=True).execute().data or []
    except Exception:
        agree_orders = []
    if not agree_orders:
        st.info("No confirmed agreements yet.")
    else:
        st.markdown(f"### 📄 Confirmed Agreements ({len(agree_orders)})")
        for o in agree_orders:
            prod = o.get("products") or {}
            with st.container(border=True):
                st.markdown(f"**{prod.get('product_name','Unknown')}** · Grade **{prod.get('quality_grade','')}**")
                st.metric("Qty", f"{o.get('quantity_ordered',0):,.1f} {prod.get('unit','')}")
                st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")

# ─── HISTORY ───
with tab_history:
    st.subheader("📜 Delivery History")
    hist_prod_ids = [p["id"] for p in cached_query("products", filters={"producer_id": user_id}, order_by=None, limit=500)]
    if not hist_prod_ids:
        st.info("No products.")
    else:
        try:
            hist_orders = supabase.table("orders").select("*, products(product_name, unit, sector, quality_grade, region), profiles(full_name, phone, region)").in_("product_id", hist_prod_ids).eq("status", "delivered").order("created_at", desc=True).execute().data or []
        except Exception:
            hist_orders = []
        if not hist_orders:
            st.info("No delivered orders yet.")
        else:
            total_rev = sum(float(o.get("total_price_birr") or 0) for o in hist_orders)
            st.metric("Total Revenue", f"{total_rev:,.0f} Birr")
            for o in hist_orders:
                prod = o.get("products") or {}
                buyer = o.get("profiles") or {}
                with st.container(border=True):
                    st.markdown(f"✅ **{prod.get('product_name','Unknown')}** · {prod.get('sector','')}")
                    st.caption(f"👤 Buyer: **{buyer.get('full_name','Unknown')}** · 📅 {str(o.get('created_at',''))[:10]}")
                    st.metric("Total", f"{o.get('total_price_birr',0):,.0f} Birr")

# ─── NOTIFICATIONS ───
with tab_notif:
    render_notifications_tab(user_id)

# ─── PROFILE ───
with tab_profile:
    render_profile_edit_tab(profile, user_id)
