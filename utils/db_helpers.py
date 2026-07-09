"""
utils/db_helpers.py — Cached DB queries and shared database utilities.

The Supabase client is sourced from src/db.py (single source of truth).
Use get_client() for direct access; use cached_* functions for read queries.
"""
import logging
from typing import Optional, Dict, Any, List, Union
import streamlit as st

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# CLIENT — delegate to src/db.py (single source of truth)
# ─────────────────────────────────────────────────────────────
def get_client():
    """Return the shared Supabase client from src/db.py."""
    from src.db import get_supabase_client
    return get_supabase_client()

# ─────────────────────────────────────────────────────────────
# CACHED QUERIES
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def cached_query(
    table_name: str,
    filters: Optional[Dict[str, Any]] = None,
    order_by: str = "created_at",
    desc: bool = True,
    limit: int = 200,
    select_fields: str = "*",
) -> List[Dict[str, Any]]:
    """
    Generic cached Supabase query.

    Supports eq, ilike (value contains '%'), and in_ (value is a list) filters.
    Returns [] on any error.
    """
    client = get_client()
    if not client:
        return []

    try:
        query = client.table(table_name).select(select_fields)

        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                if isinstance(value, list) and value:
                    query = query.in_(key, value)
                elif isinstance(value, bool):
                    query = query.eq(key, value)
                elif isinstance(value, str) and "%" in value:
                    query = query.ilike(key, value)
                else:
                    query = query.eq(key, value)

        if order_by:
            query = query.order(order_by, desc=desc)

        if limit and limit > 0:
            query = query.limit(min(limit, 1000))

        response = query.execute()
        return (response.data or []) if response else []

    except Exception as e:
        logger.error(f"cached_query failed on '{table_name}': {e}")
        return []


@st.cache_data(ttl=120, show_spinner=False)
def cached_get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch and cache a user's profile row by user ID."""
    if not user_id:
        return None

    client = get_client()
    if not client:
        return None

    try:
        response = (
            client.table("profiles")
            .select("*")
            .eq("id", user_id)
            .execute()
        )
        if response and response.data:
            return response.data[0]
        logger.warning(f"No profile found for user_id: {user_id}")
        return None
    except Exception as e:
        logger.error(f"cached_get_profile error for {user_id}: {e}")
        return None


@st.cache_data(ttl=30, show_spinner=False)
def cached_unread_count(user_id: str) -> int:
    """Return the number of unread notifications for a user."""
    if not user_id:
        return 0

    client = get_client()
    if not client:
        return 0

    try:
        response = (
            client.table("notifications")
            .select("id", count="exact")
            .eq("recipient_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        return response.count if response else 0
    except Exception as e:
        logger.error(f"cached_unread_count error for {user_id}: {e}")
        return 0


@st.cache_data(ttl=300, show_spinner=False)
def cached_get_all_products(
    sector: Optional[str] = None,
    region: Optional[str] = None,
    is_available: bool = True,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Fetch available products with optional sector/region filter."""
    filters: Dict[str, Any] = {"is_available": is_available}
    if sector:
        filters["sector"] = sector
    if region:
        filters["region"] = region

    return cached_query(
        table_name="products",
        filters=filters,
        order_by="created_at",
        desc=True,
        limit=limit,
        select_fields=(
            "id, product_name, sector, region, price_birr, "
            "quantity, unit, producer_id, is_available, created_at"
        ),
    )


@st.cache_data(ttl=300, show_spinner=False)
def cached_get_users_by_role(role: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch users by role. Note: email lives in Supabase Auth, not profiles."""
    return cached_query(
        table_name="profiles",
        filters={"role": role},
        order_by="full_name",
        desc=False,
        limit=limit,
        # 'email' is NOT in profiles — it's in Supabase Auth only
        select_fields="id, full_name, region, phone, is_verified, created_at",
    )

# ─────────────────────────────────────────────────────────────
# CACHE MANAGEMENT
# ─────────────────────────────────────────────────────────────
def clear_data_cache() -> None:
    """Clear all @st.cache_data caches and force fresh data on next fetch."""
    try:
        st.cache_data.clear()
        logger.info("All data caches cleared")
    except Exception as e:
        logger.error(f"clear_data_cache error: {e}")


def clear_specific_caches(cache_names: List[str]) -> None:
    """
    Clear specific named caches.

    Valid names: 'profile', 'unread', 'products', 'users', 'query'
    """
    cache_map = {
        "profile":  cached_get_profile,
        "unread":   cached_unread_count,
        "products": cached_get_all_products,
        "users":    cached_get_users_by_role,
        "query":    cached_query,
    }
    for name in cache_names:
        if name in cache_map:
            try:
                cache_map[name].clear()
                logger.info(f"Cleared cache: {name}")
            except Exception as e:
                logger.error(f"Failed to clear '{name}' cache: {e}")

# ─────────────────────────────────────────────────────────────
# NOTIFICATION FUNCTIONS
# ─────────────────────────────────────────────────────────────
def send_notification(
    recipient_id: str,
    title: str,
    message: str,
    notif_type: str = "info",
    order_id: Optional[str] = None,
    link: Optional[str] = None,
) -> bool:
    """
    Insert a notification row for the given user.
    Returns True on success, False on failure.
    """
    if not recipient_id or not title or not message:
        logger.warning("send_notification: missing required fields")
        return False

    client = get_client()
    if not client:
        return False

    try:
        payload: Dict[str, Any] = {
            "recipient_id": str(recipient_id),
            "title": title[:100],
            "message": message[:500],
            "type": notif_type,
            "is_read": False,
            # Omit created_at — let Supabase column default handle it
        }
        if order_id:
            payload["order_id"] = str(order_id)
        if link:
            payload["link"] = link

        client.table("notifications").insert(payload).execute()

        # Invalidate unread count cache for this user
        try:
            cached_unread_count.clear()
        except Exception:
            pass

        logger.info(f"Notification sent to {recipient_id}: {title}")
        return True

    except Exception as e:
        logger.error(f"send_notification error: {e}")
        return False


def get_notifications(
    user_id: str,
    limit: int = 20,
    unread_only: bool = False,
) -> List[Dict[str, Any]]:
    """Fetch notifications for a user, newest first."""
    filters: Dict[str, Any] = {"recipient_id": user_id}
    if unread_only:
        filters["is_read"] = False

    return cached_query(
        table_name="notifications",
        filters=filters,
        order_by="created_at",
        desc=True,
        limit=limit,
        select_fields="id, title, message, type, is_read, created_at, link, order_id",
    )


def mark_notification_read(notification_id: str) -> bool:
    """Mark a single notification as read."""
    if not notification_id:
        return False

    client = get_client()
    if not client:
        return False

    try:
        client.table("notifications").update({"is_read": True}).eq("id", notification_id).execute()
        try:
            cached_unread_count.clear()
        except Exception:
            pass
        return True
    except Exception as e:
        logger.error(f"mark_notification_read error: {e}")
        return False


def mark_all_notifications_read(user_id: str) -> bool:
    """Mark all unread notifications as read for a user."""
    if not user_id:
        return False

    client = get_client()
    if not client:
        return False

    try:
        (
            client.table("notifications")
            .update({"is_read": True})
            .eq("recipient_id", user_id)
            .eq("is_read", False)
            .execute()
        )
        try:
            cached_unread_count.clear()
        except Exception:
            pass
        return True
    except Exception as e:
        logger.error(f"mark_all_notifications_read error: {e}")
        return False

# ─────────────────────────────────────────────────────────────
# PRODUCT FUNCTIONS
# ─────────────────────────────────────────────────────────────
def reduce_product_stock(product_id: str, qty_sold: Union[int, float]) -> bool:
    """
    Deduct qty_sold from a product's quantity.
    Sets is_available=False if stock reaches zero.
    Returns True on success.
    """
    if not product_id or qty_sold <= 0:
        logger.warning("reduce_product_stock: invalid product_id or quantity")
        return False

    client = get_client()
    if not client:
        return False

    try:
        response = client.table("products").select("quantity").eq("id", product_id).execute()
        if not response or not response.data:
            logger.warning(f"Product not found: {product_id}")
            return False

        current_qty = float(response.data[0].get("quantity") or 0)
        new_qty = max(0.0, current_qty - float(qty_sold))

        update_payload: Dict[str, Any] = {"quantity": new_qty}
        if new_qty <= 0:
            update_payload["is_available"] = False
            update_payload["quantity"] = 0.0

        client.table("products").update(update_payload).eq("id", product_id).execute()

        try:
            cached_query.clear()
            cached_get_all_products.clear()
        except Exception:
            pass

        logger.info(f"Stock updated for {product_id}: {current_qty} → {new_qty}")
        return True

    except Exception as e:
        logger.error(f"reduce_product_stock error for {product_id}: {e}")
        return False


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single product row by ID."""
    if not product_id:
        return None

    client = get_client()
    if not client:
        return None

    try:
        response = client.table("products").select("*").eq("id", product_id).execute()
        return response.data[0] if (response and response.data) else None
    except Exception as e:
        logger.error(f"get_product_by_id error: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# DATABASE HEALTH
# ─────────────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """Return True if the database is reachable."""
    client = get_client()
    if not client:
        return False
    try:
        client.table("profiles").select("id", count="exact").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return False


def get_db_status() -> Dict[str, Any]:
    """Return a dict describing the current DB connection status."""
    client = get_client()
    if not client:
        return {"status": "error", "message": "Supabase client not initialized"}
    try:
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return {
            "status": "connected",
            "message": "Database connection healthy",
            "has_data": bool(response and response.data),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)[:100]}",
        }

# ─────────────────────────────────────────────────────────────
# BACKWARD COMPATIBILITY EXPORT
# ─────────────────────────────────────────────────────────────
# Existing code that does `from utils.db_helpers import supabase` still works.
supabase = get_client()
