# utils/__init__.py
"""
Utility modules for the AI Supply Chain Platform
"""

from . import auth
from . import chatbot
from . import constants
from . import db_helpers
from . import pdf_generator
from . import shared_ui
from . import theme
from . import verification

# Export commonly used functions
from .db_helpers import (
    supabase,
    get_client,
    cached_query,
    cached_get_profile,
    cached_unread_count,
    clear_data_cache,
    send_notification,
    reduce_product_stock,
    check_db_connection,
    get_db_status
)

__all__ = [
    'auth',
    'chatbot',
    'constants',
    'db_helpers',
    'pdf_generator',
    'shared_ui',
    'theme',
    'verification',
    # Exported functions
    'supabase',
    'get_client',
    'cached_query',
    'cached_get_profile',
    'cached_unread_count',
    'clear_data_cache',
    'send_notification',
    'reduce_product_stock',
    'check_db_connection',
    'get_db_status'
]
