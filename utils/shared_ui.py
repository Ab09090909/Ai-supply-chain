"""Shared UI components used across multiple dashboards."""
import re as _re
import base64
import streamlit as st
from utils.constants import REGIONS, SECTORS, UNITS, GRADES_DICT
from utils.db_helpers import supabase, cached_query, cached_unread_count, clear_data_cache, reduce_product_stock
from utils.verification import check_verification_status
from src.fraud_engine import check_fraud_risk


def get_grades_for_product(sector, product_name=""):
    sector_lower = sector.lower() if sector else ""
    product_lower = product_name.lower() if product_name else ""
    for key in GRADES_DICT:
        if key in product_lower:
            return GRADES_DICT[key]
    sector_mapping = {
        "agriculture": "grains", "livestock": "cattle", "manufacturing": "processed_foods",
        "handicrafts": "pottery", "food processing": "dairy", "textiles": "textiles",
        "services": "consulting",
    }
    for key, value in sector_mapping.items():
        if key in sector_lower:
            return GRADES_DICT.get(value, GRADES_DICT["general"])
    return GRADES_DICT["general"]


def map_grade_to_db(grade_name):
    if not grade_name:
        return "B"
    grade_lower = grade_name.lower()
    if any(x in grade_lower for x in ['a', 'premium', 'specialty', 'export', 'master', 'luxury', 'extra virgin', 'orthodox premium', 'expert']):
        return 'A'
    elif any(x in grade_lower for x in ['b', 'standard', 'virgin', 'refined', 'professional', 'grade 2', 'grade 3', 'class ii', 'class iii']):
        return 'B'
    else:
        return 'C'


def get_fraud_risk(sector, product, region, payment_method, quantity, price_birr):
    try:
        return check_fraud_risk(
            sector=sector, product=product, region=region,
            payment_method=payment_method, quantity=quantity,
            agreed_price_birr=price_birr, market_price_birr=price_birr,
        )
    except Exception:
        return {"risk_level": "Unknown", "is_fraud": 0, "fraud_probability": 0.0}


def render_fraud_badge(risk):
    badge = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(risk.get("risk_level"), "⚪")
    st.caption(f"{badge} Fraud Risk: {risk.get('risk_level', 'Unknown')}")


def render_product_image(product, height=150):
    img_b64 = product.get("image_base64")
    if img_b64:
        try:
            img_b64_clean = img_b64.replace('\n', '').replace('\r', '').replace(' ', '')
            raw = base64.b64decode(img_b64_clean[:16])
            mime = "image/png" if raw[:4] == b'\x89PNG' else "image/jpeg"
            st.markdown(
                f'<img src="data:{mime};base64,{img_b64_clean}" '
                f'style="width:100%;border-radius:8px;object-fit:cover;max-height:{height}px;" '
                f'alt="{product.get("product_name","")}">',
                unsafe_allow_html=True
            )
        except Exception:
            st.markdown(f'<div style="background:#1e2a3a;border-radius:8px;height:{height}px;display:flex;align-items:center;justify-content:center;border:1px dashed #334155;color:#64748b;">📷 Error</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: #1e2a3a; border-radius: 8px; height: {height}px; 
                    display: flex; align-items: center; justify-content: center; 
                    border: 1px dashed #334155; color: #64748b; font-size: 14px;">
            📷 No Image Uploaded
        </div>
        """, unsafe_allow_html=True)


def render_browse_tab(role, profile):
    st.subheader("🛒 Browse Available Products")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_sector = st.selectbox("Sector", ["All"] + SECTORS, key=f"browse_sector_{role}")
    with col2:
        filter_region = st.selectbox("Region", ["All"] + REGIONS, key=f"browse_region_{role}")
    with col3:
        search_term = st.text_input("🔍 Search", key=f"browse_search_{role}")

    filters = {"is_available": True}
    if filter_sector != "All":
        filters["sector"] = filter_sector
    if filter_region != "All":
        filters["region"] = filter_region

    products = cached_query("products", filters=filters, limit=200)
    if search_term:
        products = [p for p in products if search_term.lower() in p.get("product_name", "").lower()]

    if not products:
        st.info("No products found.")
        return

    for p in products:
        with st.container(border=True):
            img_col, info_col = st.columns([1, 3])
            with img_col:
                render_product_image(p, height=150)
            with info_col:
                st.markdown(f'**{p["product_name"]}** · {p["sector"]} · Grade **{p["quality_grade"]}**')
                desc = p.get("description")
                if desc:
                    st.caption(desc[:100] + "..." if len(desc) > 100 else desc)
                else:
                    st.caption("No description")
                st.caption(f'📍 {p.get("region")}')
                c_price, c_action = st.columns(2)
                with c_price:
                    st.metric("Price", f'{p.get("price_birr", 0):,.0f} Birr')
                    st.caption(f'Available: {p.get("quantity")} {p.get("unit")}')
                with c_action:
                    if role in ("merchant", "customer"):
                        _qty_max = max(1.0, float(p.get("quantity", 1)))
                        qty_to_order = st.number_input("Qty", min_value=1.0, max_value=_qty_max, value=min(1.0, _qty_max), key=f'qty_{p["id"]}')
                        total = qty_to_order * p.get("price_birr", 0)
                        st.caption(f"Total: **{total:,.0f} Birr**")
                        risk = get_fraud_risk(
                            sector=p.get("sector"), product=p.get("product_name"),
                            region=p.get("region"), payment_method="Bank Transfer",
                            quantity=qty_to_order, price_birr=p.get("price_birr", 0),
                        )
                        render_fraud_badge(risk)
                        if st.button("🛒 Place Order", key=f'order_{p["id"]}'):
                            if risk["risk_level"] == "High":
                                st.warning("⚠️ High fraud risk — proceed with caution.")
                            try:
                                supabase.table("orders").insert({
                                    "product_id": p["id"],
                                    "buyer_id": st.session_state.user.id,
                                    "quantity_ordered": qty_to_order,
                                    "total_price_birr": total,
                                    "status": "pending",
                                    "fraud_risk_level": risk["risk_level"],
                                    "fraud_probability": risk["fraud_probability"],
                                }).execute()
                                reduce_product_stock(p["id"], qty_to_order)
                                st.success(f"✅ Order placed — {total:,.0f} Birr")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Order failed: {e}")
                    else:
                        st.caption("📍 " + p.get("region", ""))


def render_notifications_tab(user_id):
    st.subheader("🔔 Notifications")
    if st.button("✅ Mark All Read", use_container_width=True):
        try:
            supabase.table("notifications").update({"is_read": True}).eq("recipient_id", user_id).eq("is_read", False).execute()
            cached_unread_count.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Failed: {e}")
    try:
        notifs = supabase.table("notifications").select("*").eq("recipient_id", user_id).order("created_at", desc=True).limit(30).execute().data or []
    except Exception as e:
        st.error(f"Could not load notifications: {e}")
        notifs = []
    if not notifs:
        st.info("No notifications yet.")
        return
    for n in notifs:
        icon = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(n.get("type", "info"), "")
        with st.container(border=True):
            st.markdown(f"{icon} **{n.get('title', '')}**")
            st.caption(n.get("message", ""))
            st.caption(f" {str(n.get('created_at', ''))[:16]}")


def render_profile_edit_tab(profile, user_id):
    st.subheader(" Edit Profile")
    with st.form("profile_edit_form"):
        pe1, pe2 = st.columns(2)
        with pe1:
            new_full_name = st.text_input("Full Name", value=profile.get("full_name", ""), max_chars=100)
            new_phone = st.text_input("Phone", value=profile.get("phone") or "", placeholder="+251 9xx xxx xxx", max_chars=20)
        with pe2:
            current_region = profile.get("region", REGIONS[0])
            new_region = st.selectbox(
                "Region", REGIONS,
                index=REGIONS.index(current_region) if current_region in REGIONS else 0,
            )
            st.text_input("Role (read-only)", value=profile.get("role", "").capitalize(), disabled=True)
        st.caption("Email cannot be changed here. Contact support if needed.")
        save_profile = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        if save_profile:
            if not new_full_name.strip():
                st.error("Full name cannot be empty.")
            else:
                phone_val = new_phone.strip()
                if phone_val and not _re.match(r"^\+?[\d\s-]{7,20}$", phone_val):
                    st.error("Invalid phone number format.")
                else:
                    try:
                        supabase.table("profiles").update({
                            "full_name": new_full_name.strip(),
                            "phone": phone_val or None,
                            "region": new_region,
                        }).eq("id", user_id).execute()
                        clear_data_cache()
                        st.session_state.profile = None
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")


def render_profile_editor_modal(profile, user_id, key_suffix="main"):
    """Render profile editor modal with image upload.
    
    key_suffix: unique string to avoid DuplicateWidgetID when this is
    called from multiple locations. Use 'tab' for the Profile tab call
    and 'modal' for the header-button triggered call.
    """
    st.markdown("""
    <style>
    .profile-editor-modal {
        background: #161b27;
        border: 1px solid #1e2a3a;
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
    }
    .profile-pic-upload {
        text-align: center;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="profile-editor-modal">', unsafe_allow_html=True)
        st.markdown("### 👤 Edit Profile")
        
        # Profile Picture Upload Section
        st.markdown('<div class="profile-pic-upload">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            profile_pic = profile.get("profile_image")
            if profile_pic:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <img src="data:image/jpeg;base64,{profile_pic}" 
                         style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #D4A017; object-fit: cover;">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 48px; color: #f1f5f9; font-weight: 700;">
                        {profile.get('full_name', 'U')[0].upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            uploaded_image = st.file_uploader(
                "Upload Profile Picture",
                type=["jpg", "jpeg", "png"],
                key=f"profile_pic_upload_{key_suffix}",
                help="Upload a profile picture (JPG, JPEG, or PNG)"
            )
            if uploaded_image:
                try:
                    image_bytes = uploaded_image.read()
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                    supabase.table("profiles").update({
                        "profile_image": image_base64
                    }).eq("id", user_id).execute()
                    clear_data_cache()
                    st.success("✅ Profile picture updated!")
                    st.session_state.profile = None
                    st.session_state.show_profile_editor = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to upload image: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Profile Information Form — key also unique
        with st.form(f"profile_info_form_{key_suffix}"):
            st.markdown("#### 📝 Profile Information")
            pe1, pe2 = st.columns(2)
            with pe1:
                new_full_name = st.text_input(
                    "Full Name / Company Name *",
                    value=profile.get("full_name", ""),
                    max_chars=100,
                    help="Enter your full name or company name"
                )
                new_phone = st.text_input(
                    "Phone",
                    value=profile.get("phone") or "",
                    placeholder="+251 9xx xxx xxx",
                    max_chars=20
                )
                new_region = st.selectbox(
                    "Region",
                    REGIONS,
                    index=REGIONS.index(profile.get("region", REGIONS[0])) if profile.get("region") in REGIONS else 0
                )
            with pe2:
                st.text_input(
                    "Email (Read-only)",
                    value=st.session_state.user.email if st.session_state.user else "",
                    disabled=True
                )
                st.text_input(
                    "Role (Read-only)",
                    value=profile.get("role", "").capitalize(),
                    disabled=True
                )
                new_company = st.text_input(
                    "Company/Organization",
                    value=profile.get("company", ""),
                    placeholder="Your company name"
                )
            
            st.markdown("")
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
            
        # Cancel button — unique key
        if st.button("✖ Cancel", use_container_width=True, key=f"cancel_profile_edit_{key_suffix}"):
            st.session_state.show_profile_editor = False
            st.rerun()

        # Handle form submission
        if submitted:
            if not new_full_name.strip():
                st.error("Full name cannot be empty.")
            else:
                phone_val = new_phone.strip()
                if phone_val and not _re.match(r"^\+?[\d\s-]{7,20}$", phone_val):
                    st.error("Invalid phone number format.")
                else:
                    try:
                        update_data = {
                            "full_name": new_full_name.strip(),
                            "phone": phone_val or None,
                            "region": new_region,
                            "company": new_company.strip() if new_company else None,
                        }
                        supabase.table("profiles").update(update_data).eq("id", user_id).execute()
                        clear_data_cache()
                        st.session_state.profile = None
                        st.success("✅ Profile updated successfully!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
