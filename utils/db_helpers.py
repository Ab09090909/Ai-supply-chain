"""Database helpers and cached queries — Works on Streamlit Cloud & Local."""
import os
import logging
from typing import Optional, Dict, Any, List, Union
import streamlit as st
from supabase import create_client, Client

# Configure logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# SUPABASE CLIENT INITIALIZATION (WITH ERROR HANDLING)
# ─────────────────────────────────────────────────────────────
def get_supabase_client() -> Optional[Client]:
    """
    Initialize and return Supabase client with proper error handling.
    
    Returns:
        Optional[Client]: Supabase client or None if initialization fails
    """
    try:
        # Try Streamlit Cloud secrets first
        if hasattr(st, 'secrets') and st.secrets:
            url = st.secrets.get("SUPABASE_URL")
            key = st.secrets.get("SUPABASE_KEY")
        else:
            url = None
            key = None
        
        # Fallback to environment variables
        if not url:
            url = os.getenv("SUPABASE_URL")
        if not key:
            key = os.getenv("SUPABASE_KEY")
        
        # Validate credentials
        if not url or not key:
            logger.error("Supabase credentials missing")
            st.error("⚠️ Database connection unavailable. Please check your configuration.")
            return None
        
        # Create client
        client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
        return client
        
    except Exception as e:
        logger.error(f"Supabase client initialization error: {e}")
        st.error(f"⚠️ Database connection error: {str(e)}")
        return None

# Initialize client once and reuse
_supabase_client = None

def get_client() -> Optional[Client]:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    return _supabase_client

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
    select_fields: str = "*"
) -> List[Dict[str, Any]]:
    """
    Fetch data from Supabase with caching.
    
    Args:
        table_name: Name of the table to query
        filters: Dictionary of filters (key: value)
        order_by: Column to order by
        desc: True for descending order
        limit: Maximum number of rows to return
        select_fields: Fields to select (default: "*")
    
    Returns:
        List of records or empty list on error
    """
    client = get_client()
    if not client:
        return []
    
    try:
        query = client.table(table_name).select(select_fields)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if value is None or value == "":
                    continue
                if isinstance(value, list) and value:
                    query = query.in_(key, value)
                elif isinstance(value, bool):
                    query = query.eq(key, value)
                elif isinstance(value, str) and "%" in value:
                    # For LIKE queries
                    query = query.ilike(key, value)
                else:
                    query = query.eq(key, value)
        
        # Apply ordering
        if order_by:
            query = query.order(order_by, desc=desc)
        
        # Apply limit
        if limit and limit > 0:
            query = query.limit(min(limit, 1000))  # Cap at 1000
        
        response = query.execute()
        
        if response and hasattr(response, 'data'):
            return response.data or []
        else:
            logger.warning(f"No data returned from query on {table_name}")
            return []
            
    except Exception as e:
        logger.error(f"Query failed on {table_name}: {e}")
        st.toast(f"⚠️ Query failed: {str(e)[:50]}...", icon="⚠️")
        return []

@st.cache_data(ttl=120, show_spinner=False)
def cached_get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user profile with caching.
    
    Args:
        user_id: User ID to fetch profile for
    
    Returns:
        Optional[Dict]: User profile or None if not found
    """
    if not user_id:
        logger.warning("cached_get_profile called with empty user_id")
        return None
    
    client = get_client()
    if not client:
        return None
    
    try:
        response = client.table("profiles").select("*").eq("id", user_id).execute()
        if response and response.data:
            return response.data[0]
        else:
            logger.warning(f"No profile found for user_id: {user_id}")
            return None
    except Exception as e:
        logger.error(f"Profile fetch error for {user_id}: {e}")
        return None

@st.cache_data(ttl=30, show_spinner=False)
def cached_unread_count(user_id: str) -> int:
    """
    Get unread notification count with caching.
    
    Args:
        user_id: User ID to get notifications for
    
    Returns:
        int: Number of unread notifications
    """
    if not user_id:
        return 0
    
    client = get_client()
    if not client:
        return 0
    
    try:
        response = client.table("notifications").select("id", count="exact") \
            .eq("recipient_id", user_id) \
            .eq("is_read", False) \
            .execute()
        
        return response.count if response else 0
    except Exception as e:
        logger.error(f"Unread count error for {user_id}: {e}")
        return 0

@st.cache_data(ttl=300, show_spinner=False)
def cached_get_all_products(
    sector: Optional[str] = None,
    region: Optional[str] = None,
    is_available: bool = True,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get products with optional filtering.
    
    Args:
        sector: Optional sector filter
        region: Optional region filter
        is_available: Filter by availability
        limit: Maximum number of products
    
    Returns:
        List of products
    """
    filters = {"is_available": is_available}
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
        select_fields="id, product_name, sector, region, price_birr, quantity, unit, producer_id, is_available, created_at"
    )

@st.cache_data(ttl=300, show_spinner=False)
def cached_get_users_by_role(role: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get users by role with caching.
    
    Args:
        role: User role (producer, merchant, customer, admin)
        limit: Maximum number of users
    
    Returns:
        List of users
    """
    return cached_query(
        table_name="profiles",
        filters={"role": role},
        order_by="full_name",
        desc=False,
        limit=limit,
        select_fields="id, full_name, email, region, phone, is_verified, created_at"
    )

# ─────────────────────────────────────────────────────────────
# CACHE MANAGEMENT
# ─────────────────────────────────────────────────────────────
def clear_data_cache() -> None:
    """Clear all cached queries and force fresh data fetch."""
    try:
        st.cache_data.clear()
        logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Cache clear error: {e}")

def clear_specific_caches(cache_names: List[str]) -> None:
    """
    Clear specific cached functions.
    
    Args:
        cache_names: List of cache names to clear
    """
    cache_map = {
        "profile": cached_get_profile,
        "unread": cached_unread_count,
        "products": cached_get_all_products,
        "users": cached_get_users_by_role,
        "query": cached_query
    }
    
    for name in cache_names:
        if name in cache_map:
            try:
                cache_map[name].clear()
                logger.info(f"Cleared cache: {name}")
            except Exception as e:
                logger.error(f"Failed to clear {name} cache: {e}")

# ─────────────────────────────────────────────────────────────
# NOTIFICATION FUNCTIONS
# ─────────────────────────────────────────────────────────────
def send_notification(
    recipient_id: str,
    title: str,
    message: str,
    notif_type: str = "info",
    order_id: Optional[str] = None,
    link: Optional[str] = None
) -> bool:
    """
    Send a notification to a user.
    
    Args:
        recipient_id: User ID to notify
        title: Notification title
        message: Notification message
        notif_type: Type (info, success, warning, error)
        order_id: Optional order ID reference
        link: Optional link URL
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not recipient_id or not title or not message:
        logger.warning("Missing required fields for notification")
        return False
    
    client = get_client()
    if not client:
        return False
    
    try:
        payload = {
            "recipient_id": str(recipient_id),
            "title": title[:100],  # Limit title length
            "message": message[:500],  # Limit message length
            "type": notif_type,
            "is_read": False,
            "created_at": "now()"
        }
        
        if order_id:
            payload["order_id"] = str(order_id)
        if link:
            payload["link"] = link
        
        response = client.table("notifications").insert(payload).execute()
        
        # Clear cache for this user's notifications
        try:
            cached_unread_count.clear()
        except Exception:
            pass
        
        logger.info(f"Notification sent to {recipient_id}: {title}")
        return True
        
    except Exception as e:
        logger.error(f"Notification send error: {e}")
        return False

def get_notifications(user_id: str, limit: int = 20, unread_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get notifications for a user.
    
    Args:
        user_id: User ID to get notifications for
        limit: Maximum number of notifications
        unread_only: Only fetch unread notifications
    
    Returns:
        List of notifications
    """
    filters = {"recipient_id": user_id}
    if unread_only:
        filters["is_read"] = False
    
    return cached_query(
        table_name="notifications",
        filters=filters,
        order_by="created_at",
        desc=True,
        limit=limit,
        select_fields="id, title, message, type, is_read, created_at, link, order_id"
    )

def mark_notification_read(notification_id: str) -> bool:
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID to mark as read
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not notification_id:
        return False
    
    client = get_client()
    if not client:
        return False
    
    try:
        client.table("notifications").update({"is_read": True}).eq("id", notification_id).execute()
        cached_unread_count.clear()
        return True
    except Exception as e:
        logger.error(f"Mark notification read error: {e}")
        return False

def mark_all_notifications_read(user_id: str) -> bool:
    """
    Mark all notifications as read for a user.
    
    Args:
        user_id: User ID to mark all notifications for
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not user_id:
        return False
    
    client = get_client()
    if not client:
        return False
    
    try:
        client.table("notifications").update({"is_read": True}).eq("recipient_id", user_id).eq("is_read", False).execute()
        cached_unread_count.clear()
        return True
    except Exception as e:
        logger.error(f"Mark all notifications read error: {e}")
        return False

# ─────────────────────────────────────────────────────────────
# PRODUCT FUNCTIONS
# ─────────────────────────────────────────────────────────────
def reduce_product_stock(product_id: str, qty_sold: Union[int, float]) -> bool:
    """
    Reduce product stock after an order.
    
    Args:
        product_id: Product ID to update
        qty_sold: Quantity sold
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not product_id or qty_sold <= 0:
        logger.warning("Invalid product_id or quantity")
        return False
    
    client = get_client()
    if not client:
        return False
    
    try:
        # Get current stock
        response = client.table("products").select("quantity").eq("id", product_id).execute()
        if not response or not response.data:
            logger.warning(f"Product not found: {product_id}")
            return False
        
        current_qty = float(response.data[0].get("quantity") or 0)
        new_qty = max(0.0, current_qty - float(qty_sold))
        
        # Prepare update payload
        update_payload = {"quantity": new_qty}
        if new_qty <= 0:
            update_payload["is_available"] = False
            update_payload["quantity"] = 0.0
        
        # Update product
        client.table("products").update(update_payload).eq("id", product_id).execute()
        
        # Clear relevant caches
        try:
            cached_query.clear()
            cached_get_all_products.clear()
        except Exception:
            pass
        
        logger.info(f"Stock updated for {product_id}: {current_qty} -> {new_qty}")
        return True
        
    except Exception as e:
        logger.error(f"Stock update error for {product_id}: {e}")
        return False

def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get product by ID.
    
    Args:
        product_id: Product ID to fetch
    
    Returns:
        Optional[Dict]: Product data or None
    """
    if not product_id:
        return None
    
    client = get_client()
    if not client:
        return None
    
    try:
        response = client.table("products").select("*").eq("id", product_id).execute()
        if response and response.data:
            return response.data[0]
        return None
    except Exception as e:
        logger.error(f"Product fetch error: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# DATABASE HEALTH CHECK
# ─────────────────────────────────────────────────────────────
def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    client = get_client()
    if not client:
        return False
    
    try:
        # Try a simple query
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return False

def get_db_status() -> Dict[str, Any]:
    """
    Get detailed database status.
    
    Returns:
        Dict: Status information
    """
    client = get_client()
    if not client:
        return {"status": "error", "message": "Supabase client not initialized"}
    
    try:
        # Check connection
        response = client.table("profiles").select("id", count="exact").limit(1).execute()
        return {
            "status": "connected",
            "message": "Database connection healthy",
            "has_data": bool(response and response.data)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)[:100]}"
        }

# ─────────────────────────────────────────────────────────────
# EXPOSE SUPABASE CLIENT (FOR BACKWARD COMPATIBILITY)
# ─────────────────────────────────────────────────────────────
# This is the legacy export for code that imports supabase directly
# Use get_client() in new code for better error handling
supabase = get_client()
