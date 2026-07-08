"""Shared UI components used across multiple dashboards."""
import re
import base64
import logging
from typing import Optional, Dict, Any, List, Tuple
import streamlit as st
from utils.constants import REGIONS, SECTORS, UNITS, GRADES_DICT
from utils.db_helpers import (
    supabase, 
    cached_query, 
    cached_unread_count, 
    clear_data_cache, 
    reduce_product_stock,
    get_client
)
from utils.verification import check_verification_status

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_grades_for_product(sector: str, product_name: str = "") -> List[str]:
    """
    Get appropriate grades for a product based on sector and name.
    
    Args:
        sector: Product sector
        product_name: Product name for more specific grading
    
    Returns:
        List of grade names
    """
    sector_lower = sector.lower() if sector else ""
    product_lower = product_name.lower() if product_name else ""
    
    # Check product name first
    for key in GRADES_DICT:
        if key in product_lower:
            return GRADES_DICT[key]
    
    # Check sector mapping
    sector_mapping = {
        "agriculture": "grains", 
        "livestock": "cattle", 
        "manufacturing": "processed_foods",
        "handicrafts": "pottery", 
        "food processing": "dairy", 
        "textiles": "textiles",
        "services": "consulting",
        "coffee": "coffee",
        "fruits": "fruits",
        "vegetables": "vegetables",
        "honey": "honey",
        "spices": "spices"
    }
    
    for key, value in sector_mapping.items():
        if key in sector_lower:
            return GRADES_DICT.get(value, GRADES_DICT["general"])
    
    return GRADES_DICT["general"]

def map_grade_to_db(grade_name: str) -> str:
    """
    Map display grade to database grade (A, B, C).
    
    Args:
        grade_name: Display grade name
    
    Returns:
        Database grade (A, B, or C)
    """
    if not grade_name:
        return "B"
    
    grade_lower = grade_name.lower()
    
    # Premium grades
    if any(x in grade_lower for x in [
        'a', 'premium', 'specialty', 'export', 'master', 
        'luxury', 'extra virgin', 'orthodox premium', 'expert',
        'grade 1', 'grade a'
    ]):
        return 'A'
    # Standard grades
    elif any(x in grade_lower for x in [
        'b', 'standard', 'virgin', 'refined', 'professional', 
        'grade 2', 'grade 3', 'class ii', 'class iii',
        'choice', 'grade b'
    ]):
        return 'B'
    # Basic grades
    else:
        return 'C'

# ─────────────────────────────────────────────────────────────
# FRAUD RISK FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_fraud_risk(
    sector: str, 
    product: str, 
    region: str, 
    payment_method: str, 
    quantity: float, 
    price_birr: float
) -> Dict[str, Any]:
    """
    Get fraud risk assessment for a transaction.
    
    Args:
        sector: Product sector
        product: Product name
        region: Region
        payment_method: Payment method
        quantity: Quantity
        price_birr: Price in Birr
    
    Returns:
        Fraud risk assessment dictionary
    """
    try:
        # Try to import fraud engine
        from src.fraud_engine import check_fraud_risk
        return check_fraud_risk(
            sector=sector, 
            product=product, 
            region=region,
            payment_method=payment_method, 
            quantity=quantity,
            agreed_price_birr=price_birr, 
            market_price_birr=price_birr,
        )
    except ImportError:
        logger.warning("Fraud engine not available")
        return {"risk_level": "Unknown", "is_fraud": 0, "fraud_probability": 0.0}
    except Exception as e:
        logger.error(f"Fraud risk check error: {e}")
        return {"risk_level": "Unknown", "is_fraud": 0, "fraud_probability": 0.0}

def render_fraud_badge(risk: Dict[str, Any]) -> None:
    """
    Render a fraud risk badge.
    
    Args:
        risk: Fraud risk assessment dictionary
    """
    risk_level = risk.get("risk_level", "Unknown")
    badges = {
        "Low": "🟢",
        "Medium": "🟡", 
        "High": "🔴",
        "Unknown": "⚪"
    }
    badge = badges.get(risk_level, "⚪")
    
    # Show probability if available
    prob = risk.get("fraud_probability")
    if prob is not None:
        st.caption(f"{badge} Fraud Risk: {risk_level} ({prob*100:.1f}%)")
    else:
        st.caption(f"{badge} Fraud Risk: {risk_level}")

# ─────────────────────────────────────────────────────────────
# PRODUCT IMAGE RENDERER
# ─────────────────────────────────────────────────────────────

def render_product_image(product: Dict[str, Any], height: int = 150) -> None:
    """
    Render product image from base64 data.
    
    Args:
        product: Product dictionary with image data
        height: Image height in pixels
    """
    img_b64 = product.get("image_base64")
    product_name = product.get("product_name", "Product")
    
    if img_b64:
        try:
            # Clean base64 string
            img_b64_clean = img_b64.replace('\n', '').replace('\r', '').replace(' ', '')
            
            # Detect image type
            try:
                raw = base64.b64decode(img_b64_clean[:16])
                if raw[:4] == b'\x89PNG':
                    mime = "image/png"
                elif raw[:2] == b'\xff\xd8':
                    mime = "image/jpeg"
                elif raw[:3] == b'GIF':
                    mime = "image/gif"
                elif raw[:6] in (b'RIFF.', b'WEBP'):
                    mime = "image/webp"
                else:
                    mime = "image/jpeg"  # Default
            except Exception:
                mime = "image/jpeg"
            
            st.markdown(
                f'<img src="data:{mime};base64,{img_b64_clean}" '
                f'style="width:100%;border-radius:8px;object-fit:cover;max-height:{height}px;" '
                f'alt="{product_name}">',
                unsafe_allow_html=True
            )
        except Exception as e:
            logger.error(f"Image rendering error: {e}")
            st.markdown(
                f'<div style="background:#1e2a3a;border-radius:8px;height:{height}px;'
                f'display:flex;align-items:center;justify-content:center;'
                f'border:1px dashed #334155;color:#64748b;">'
                f'📷 Image Error</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            f"""
            <div style="background: #1e2a3a; border-radius: 8px; height: {height}px; 
                        display: flex; align-items: center; justify-content: center; 
                        border: 1px dashed #334155; color: #64748b; font-size: 14px;">
                📷 No Image Uploaded
            </div>
            """,
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────────────────────
# BROWSE PRODUCTS TAB
# ─────────────────────────────────────────────────────────────

def render_browse_tab(role: str, profile: Dict[str, Any]) -> None:
    """
    Render the browse products tab.
    
    Args:
        role: User role (producer, merchant, customer, admin)
        profile: User profile dictionary
    """
    st.subheader("🛒 Browse Available Products")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_sector = st.selectbox("Sector", ["All"] + SECTORS, key=f"browse_sector_{role}")
    with col2:
        filter_region = st.selectbox("Region", ["All"] + REGIONS, key=f"browse_region_{role}")
    with col3:
        search_term = st.text_input("🔍 Search", key=f"browse_search_{role}", placeholder="Search products...")

    # Build filters
    filters = {"is_available": True}
    if filter_sector != "All":
        filters["sector"] = filter_sector
    if filter_region != "All":
        filters["region"] = filter_region

    # Fetch products
    try:
        products = cached_query("products", filters=filters, limit=200)
    except Exception as e:
        logger.error(f"Product fetch error: {e}")
        st.error("⚠️ Could not load products. Please try again.")
        return
    
    # Apply search filter
    if search_term:
        search_lower = search_term.lower()
        products = [
            p for p in products 
            if search_lower in p.get("product_name", "").lower() 
            or search_lower in p.get("description", "").lower()
        ]

    if not products:
        st.info("No products found matching your criteria.")
        return

    # Display products
    for idx, p in enumerate(products):
        with st.container(border=True):
            img_col, info_col = st.columns([1, 3])
            with img_col:
                render_product_image(p, height=150)
            with info_col:
                # Product header
                st.markdown(
                    f'**{p.get("product_name", "Unknown")}** · '
                    f'{p.get("sector", "N/A")} · Grade **{p.get("quality_grade", "N/A")}**'
                )
                
                # Description
                desc = p.get("description")
                if desc:
                    st.caption(desc[:150] + "..." if len(desc) > 150 else desc)
                else:
                    st.caption("No description available")
                
                # Location
                st.caption(f'📍 {p.get("region", "N/A")}')
                
                # Price and action
                c_price, c_action = st.columns(2)
                with c_price:
                    price = p.get("price_birr", 0)
                    st.metric("Price", f"{price:,.0f} Birr")
                    st.caption(f'Available: {p.get("quantity", 0)} {p.get("unit", "units")}')
                
                with c_action:
                    if role in ("merchant", "customer"):
                        # Quantity input
                        max_qty = max(1.0, float(p.get("quantity", 1)))
                        qty_to_order = st.number_input(
                            "Qty", 
                            min_value=0.1, 
                            max_value=max_qty, 
                            value=min(1.0, max_qty),
                            step=0.1,
                            key=f'qty_{p["id"]}_{idx}'
                        )
                        
                        # Total calculation
                        total = qty_to_order * price
                        st.caption(f"Total: **{total:,.0f} Birr**")
                        
                        # Fraud risk
                        risk = get_fraud_risk(
                            sector=p.get("sector", ""),
                            product=p.get("product_name", ""),
                            region=p.get("region", ""),
                            payment_method="Bank Transfer",
                            quantity=qty_to_order,
                            price_birr=price,
                        )
                        render_fraud_badge(risk)
                        
                        # Place order button
                        if st.button("🛒 Place Order", key=f'order_{p["id"]}_{idx}'):
                            if risk.get("risk_level") == "High":
                                st.warning("⚠️ High fraud risk — proceed with caution.")
                                if not st.button("⚠️ Confirm Order Anyway", key=f'confirm_order_{p["id"]}_{idx}'):
                                    st.stop()
                            
                            try:
                                # Create order
                                order_data = {
                                    "product_id": p["id"],
                                    "buyer_id": st.session_state.user.id,
                                    "quantity_ordered": float(qty_to_order),
                                    "total_price_birr": float(total),
                                    "status": "pending",
                                    "fraud_risk_level": risk.get("risk_level", "Unknown"),
                                    "fraud_probability": risk.get("fraud_probability", 0.0),
                                }
                                supabase.table("orders").insert(order_data).execute()
                                
                                # Reduce stock
                                reduce_product_stock(p["id"], qty_to_order)
                                
                                st.success(f"✅ Order placed — {total:,.0f} Birr")
                                clear_data_cache()
                                st.rerun()
                            except Exception as e:
                                logger.error(f"Order placement error: {e}")
                                st.error(f"Order failed: {str(e)}")
                    else:
                        st.caption(f"📍 {p.get('region', 'N/A')}")

# ─────────────────────────────────────────────────────────────
# NOTIFICATIONS TAB
# ─────────────────────────────────────────────────────────────

def render_notifications_tab(user_id: str) -> None:
    """
    Render the notifications tab.
    
    Args:
        user_id: Current user ID
    """
    st.subheader("🔔 Notifications")
    
    # Mark all read button
    if st.button("✅ Mark All Read", use_container_width=True):
        try:
            supabase.table("notifications").update({"is_read": True}).eq("recipient_id", user_id).eq("is_read", False).execute()
            clear_data_cache()
            st.rerun()
        except Exception as e:
            logger.error(f"Mark all read error: {e}")
            st.error(f"Failed to mark all as read: {e}")
    
    # Fetch notifications
    try:
        response = supabase.table("notifications").select("*").eq("recipient_id", user_id).order("created_at", desc=True).limit(50).execute()
        notifs = response.data if response else []
    except Exception as e:
        logger.error(f"Notification fetch error: {e}")
        st.error(f"Could not load notifications: {e}")
        notifs = []
    
    if not notifs:
        st.info("No notifications yet.")
        return
    
    # Display notifications
    for n in notifs:
        icon_map = {
            "success": "✅", 
            "warning": "⚠️", 
            "error": "❌", 
            "info": "ℹ️",
            "order": "📦",
            "message": "💬",
            "system": "⚙️",
            "alert": "🔔"
        }
        icon = icon_map.get(n.get("type", "info"), "ℹ️")
        is_read = n.get("is_read", False)
        opacity = "0.6" if is_read else "1"
        
        with st.container(border=True):
            st.markdown(
                f'{icon} **{n.get("title", "Notification")}**'
                f'{" (Read)" if is_read else ""}'
            )
            st.caption(n.get("message", ""))
            st.caption(f"📅 {str(n.get('created_at', ''))[:16]}")
        
        # Mark as read button for unread notifications
        if not is_read:
            if st.button(f"Mark as Read", key=f"mark_read_{n['id']}", use_container_width=True):
                try:
                    supabase.table("notifications").update({"is_read": True}).eq("id", n["id"]).execute()
                    clear_data_cache()
                    st.rerun()
                except Exception as e:
                    logger.error(f"Mark read error: {e}")
                    st.error(f"Failed to mark as read: {e}")

# ─────────────────────────────────────────────────────────────
# PROFILE EDIT TAB
# ─────────────────────────────────────────────────────────────

def render_profile_edit_tab(profile: Dict[str, Any], user_id: str) -> None:
    """
    Render the profile edit tab (simplified version for tabs).
    
    Args:
        profile: User profile dictionary
        user_id: Current user ID
    """
    st.subheader("✏️ Edit Profile")
    
    with st.form("profile_edit_form_simple"):
        pe1, pe2 = st.columns(2)
        with pe1:
            new_full_name = st.text_input(
                "Full Name", 
                value=profile.get("full_name", ""), 
                max_chars=100
            )
            new_phone = st.text_input(
                "Phone", 
                value=profile.get("phone") or "", 
                placeholder="+251 9xx xxx xxx", 
                max_chars=20
            )
        with pe2:
            current_region = profile.get("region", REGIONS[0])
            new_region = st.selectbox(
                "Region", 
                REGIONS,
                index=REGIONS.index(current_region) if current_region in REGIONS else 0,
            )
            st.text_input("Role (read-only)", value=profile.get("role", "").capitalize(), disabled=True)
        
        st.caption("Email cannot be changed here. Contact support if needed.")
        
        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
            if not new_full_name.strip():
                st.error("Full name cannot be empty.")
            else:
                phone_val = new_phone.strip()
                if phone_val and not re.match(r"^\+?[\d\s-]{7,20}$", phone_val):
                    st.error("Invalid phone number format.")
                else:
                    try:
                        update_data = {
                            "full_name": new_full_name.strip(),
                            "phone": phone_val or None,
                            "region": new_region,
                        }
                        supabase.table("profiles").update(update_data).eq("id", user_id).execute()
                        clear_data_cache()
                        st.session_state.profile = None
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Profile update error: {e}")
                        st.error(f"Update failed: {e}")

# ─────────────────────────────────────────────────────────────
# PROFILE EDITOR MODAL
# ─────────────────────────────────────────────────────────────

def render_profile_editor_modal(profile: Dict[str, Any], user_id: str, key_suffix: str = "main") -> None:
    """
    Render profile editor modal with image upload.
    
    Args:
        profile: User profile dictionary
        user_id: Current user ID
        key_suffix: Unique string to avoid DuplicateWidgetID
    """
    st.markdown("""
    <style>
    .profile-editor-modal {
        background: #161b27;
        border: 1px solid #1e2a3a;
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
        max-height: 90vh;
        overflow-y: auto;
    }
    .profile-pic-upload {
        text-align: center;
        margin: 20px 0;
    }
    @media (max-width: 768px) {
        .profile-editor-modal {
            padding: 16px;
            margin: 10px 0;
            max-height: 95vh;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="profile-editor-modal">', unsafe_allow_html=True)
        st.markdown("### 👤 Edit Profile")
        
        # Close button
        col_close, col_spacer = st.columns([1, 10])
        with col_close:
            if st.button("✖", key=f"close_profile_edit_{key_suffix}", help="Close profile editor"):
                st.session_state.show_profile_editor = False
                st.rerun()
        
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
                name_initial = profile.get('full_name', 'U')[0].upper()
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 15px;">
                    <div style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #D4A017; background: #1e2a3a; display: flex; align-items: center; justify-content: center; margin: 0 auto; font-size: 48px; color: #f1f5f9; font-weight: 700;">
                        {name_initial}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            uploaded_image = st.file_uploader(
                "Upload Profile Picture",
                type=["jpg", "jpeg", "png", "gif", "webp"],
                key=f"profile_pic_upload_{key_suffix}",
                help="Upload a profile picture (JPG, JPEG, PNG, GIF, or WEBP)"
            )
            if uploaded_image:
                try:
                    # Validate file size
                    if uploaded_image.size > 5 * 1024 * 1024:  # 5MB
                        st.error("Image size exceeds 5MB limit.")
                    else:
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
                    logger.error(f"Image upload error: {e}")
                    st.error(f"Failed to upload image: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Profile Information Form
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
                if st.session_state.get("user"):
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
                    placeholder="Your company name (optional)"
                )
            
            # Bio/About
            new_bio = st.text_area(
                "About Me / Bio",
                value=profile.get("bio", ""),
                placeholder="Tell us about yourself or your organization...",
                max_chars=500,
                height=100
            )
            
            submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        # Handle form submission
        if submitted:
            if not new_full_name.strip():
                st.error("Full name cannot be empty.")
            else:
                phone_val = new_phone.strip()
                if phone_val and not re.match(r"^\+?[\d\s-]{7,20}$", phone_val):
                    st.error("Invalid phone number format.")
                else:
                    try:
                        update_data = {
                            "full_name": new_full_name.strip(),
                            "phone": phone_val or None,
                            "region": new_region,
                            "company": new_company.strip() if new_company else None,
                            "bio": new_bio.strip() if new_bio else None,
                        }
                        supabase.table("profiles").update(update_data).eq("id", user_id).execute()
                        clear_data_cache()
                        st.session_state.profile = None
                        st.success("✅ Profile updated successfully!")
                        st.session_state.show_profile_editor = False
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Profile update error: {e}")
                        st.error(f"Update failed: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# ADDITIONAL UI HELPERS
# ─────────────────────────────────────────────────────────────

def render_verification_status(user_id: str) -> None:
    """
    Render user verification status.
    
    Args:
        user_id: User ID to check
    """
    try:
        status = check_verification_status(user_id)
        if status.get("is_verified", False):
            st.success("✅ Verified Account")
        elif status.get("has_documents", False):
            st.warning("⏳ Documents pending verification")
        else:
            st.info("📄 Upload documents to verify your account")
    except Exception as e:
        logger.error(f"Verification status error: {e}")
        st.caption("⚠️ Verification check unavailable")

def render_action_button(
    label: str, 
    icon: str = "", 
    key: str = "", 
    type: str = "default",
    **kwargs
) -> bool:
    """
    Render a styled action button.
    
    Args:
        label: Button label
        icon: Icon emoji
        key: Unique key for the button
        type: Button type (default, primary, danger, success)
    
    Returns:
        bool: True if button was clicked
    """
    button_text = f"{icon} {label}" if icon else label
    button_type = type.lower()
    
    if button_type == "primary":
        return st.button(button_text, key=key, type="primary", **kwargs)
    elif button_type == "danger":
        # Use custom styling for danger button
        return st.button(button_text, key=key, **kwargs)
    elif button_type == "success":
        return st.button(button_text, key=key, **kwargs)
    else:
        return st.button(button_text, key=key, **kwargs)

def render_empty_state(message: str, icon: str = "📭") -> None:
    """
    Render an empty state message.
    
    Args:
        message: Message to display
        icon: Icon emoji
    """
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px;">
        <div style="font-size: 48px; margin-bottom: 16px;">{icon}</div>
        <p style="font-size: 16px; color: #64748b;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def render_loading_state(message: str = "Loading...") -> None:
    """Render a loading state."""
    with st.spinner(message):
        # This will show a spinner
        pass
