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

# Export commonly used constants
from .constants import (
    REGIONS,
    SECTORS,
    UNITS,
    GRADES_DICT,
    SESSION_KEYS,
    USER_ROLES,
    ROLE_ICONS,
    ROLE_NAMES,
    ORDER_STATUS,
    PRODUCT_STATUS,
    CURRENCY_SYMBOL,
    PLATFORM_NAME,
    PLATFORM_VERSION
)

# Export commonly used db functions
from .db_helpers import (
    supabase,
    get_client,
    cached_query,
    cached_get_profile,
    cached_unread_count,
    clear_data_cache,
    send_notification,
    reduce_product_stock,
    check_db_connection
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
    # Constants
    'REGIONS',
    'SECTORS',
    'UNITS',
    'GRADES_DICT',
    'SESSION_KEYS',
    'USER_ROLES',
    'ROLE_ICONS',
    'ROLE_NAMES',
    'ORDER_STATUS',
    'PRODUCT_STATUS',
    'CURRENCY_SYMBOL',
    'PLATFORM_NAME',
    'PLATFORM_VERSION',
    # DB functions
    'supabase',
    'get_client',
    'cached_query',
    'cached_get_profile',
    'cached_unread_count',
    'clear_data_cache',
    'send_notification',
    'reduce_product_stock',
    'check_db_connection'
]
