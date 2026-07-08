"""Database helpers and cached queries — Works on Streamlit Cloud & Local."""
import os
import streamlit as st
from supabase import create_client, Client

# ─────────────────────────────────────────────────────────────
# STREAMLIT CLOUD SECRETS BRIDGE
# ─────────────────────────────────────────────────────────────
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "❌ Supabase credentials missing! "
        "Please add SUPABASE_URL and SUPABASE_KEY to your Streamlit Cloud Secrets "
        "or your local .env file."
    )

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─────────────────────────────────────────────────────────────
# CACHED QUERIES
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def cached_query(table_name, filters=None, order_by="created_at", desc=True, limit=200):
    """Fetch data from Supabase with caching."""
    try:
        query = supabase.table(table_name).select("*")
        if filters:
            for key, value in filters.items():
                if value is None:
                    continue
                if isinstance(value, list):
                    query = query.in_(key, value)
                elif isinstance(value, bool):
                    query = query.eq(key, value)
                else:
                    query = query.eq(key, value)
        if order_by:
            query = query.order(order_by, desc=desc)
        if limit:
            query = query.limit(limit)
        return query.execute().data or []
    except Exception as e:
        st.toast(f"Query failed: {e}", icon="⚠️")
        return []


@st.cache_data(ttl=120, show_spinner=False)
def cached_get_profile(user_id):
    """Get user profile with caching."""
    try:
        res = supabase.table("profiles").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_unread_count(user_id):
    """Get unread notification count with caching."""
    try:
        res = supabase.table("notifications").select("id", count="exact") \
            .eq("recipient_id", user_id).eq("is_read", False).execute()
        return res.count or 0
    except Exception:
        return 0


def clear_data_cache():
    """Clear all cached queries."""
    st.cache_data.clear()
    cached_query.clear()
    cached_get_profile.clear()
    cached_unread_count.clear()


def send_notification(recipient_id, title, message, notif_type="info", order_id=None):
    """Send a notification to a user."""
    try:
        payload = {
            "recipient_id": str(recipient_id),
            "title": title,
            "message": message,
            "type": notif_type,
            "is_read": False,
        }
        if order_id:
            payload["order_id"] = str(order_id)
        supabase.table("notifications").insert(payload).execute()
        cached_unread_count.clear()
    except Exception as e:
        st.toast(f"Notification failed: {e}", icon="⚠️")


def reduce_product_stock(product_id, qty_sold):
    """Reduce product stock after an order."""
    try:
        res = supabase.table("products").select("quantity").eq("id", product_id).execute()
        if not res.data:
            return
        current_qty = float(res.data[0].get("quantity") or 0)
        new_qty = max(0.0, current_qty - float(qty_sold))
        update_payload = {"quantity": new_qty}
        if new_qty <= 0:
            update_payload["is_available"] = False
        supabase.table("products").update(update_payload).eq("id", product_id).execute()
        cached_query.clear()
    except Exception as e:
        st.toast(f"Stock update failed: {e}", icon="⚠️")
