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

# Export from verification
from .verification import (
    check_verification_status,
    upload_document,
    render_document_upload,
    render_document_list,
    render_verification_status,
    render_verification_badge,
    get_verified_documents,
    get_pending_documents,
    get_pending_verifications,
    render_admin_verification_panel,
    DOCUMENT_TYPE_LABELS,
    DOCUMENT_TYPE_DESCRIPTIONS
)

# Export from shared_ui
from .shared_ui import (
    render_browse_tab,
    render_notifications_tab,
    render_profile_edit_tab,
    render_profile_editor_modal,
    render_product_image,
    render_fraud_badge,
    get_fraud_risk,
    get_grades_for_product,
    map_grade_to_db
)

# Export constants
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

# Export db helpers
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
    # Verification functions
    'check_verification_status',
    'upload_document',
    'render_document_upload',
    'render_document_list',
    'render_verification_status',
    'render_verification_badge',
    'get_verified_documents',
    'get_pending_documents',
    'get_pending_verifications',
    'render_admin_verification_panel',
    'DOCUMENT_TYPE_LABELS',
    'DOCUMENT_TYPE_DESCRIPTIONS',
    # Shared UI functions
    'render_browse_tab',
    'render_notifications_tab',
    'render_profile_edit_tab',
    'render_profile_editor_modal',
    'render_product_image',
    'render_fraud_badge',
    'get_fraud_risk',
    'get_grades_for_product',
    'map_grade_to_db',
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
