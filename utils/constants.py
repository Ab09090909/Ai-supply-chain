"""Constants used across the Ethiopian AI Supply Chain Platform."""

# ─────────────────────────────────────────────────────────────
# REGIONS - Ethiopian Administrative Regions
# ─────────────────────────────────────────────────────────────
REGIONS = [
    "Addis Ababa", 
    "Afar", 
    "Amhara", 
    "Benishangul-Gumuz", 
    "Dire Dawa",
    "Gambela", 
    "Harari", 
    "Oromia", 
    "Sidama", 
    "Somali", 
    "South West",
    "Tigray", 
    "Central Ethiopia", 
    "South Ethiopia"
]

# Region codes for API/DB usage
REGION_CODES = {
    "Addis Ababa": "AA",
    "Afar": "AF",
    "Amhara": "AM",
    "Benishangul-Gumuz": "BG",
    "Dire Dawa": "DD",
    "Gambela": "GA",
    "Harari": "HA",
    "Oromia": "OR",
    "Sidama": "SI",
    "Somali": "SO",
    "South West": "SW",
    "Tigray": "TI",
    "Central Ethiopia": "CE",
    "South Ethiopia": "SE"
}

# Zone names by region (for future expansion)
REGION_ZONES = {
    "Addis Ababa": ["Addis Ketema", "Akaki Kality", "Arada", "Bole", "Gullele", "Kirkos", "Kolfe Keranio", "Lideta", "Nifas Silk-Lafto", "Yeka"],
    "Oromia": ["Arsi", "Bale", "Borana", "Buno Bedele", "East Hararghe", "East Shewa", "Guji", "Horo Gudru", "Illubabor", "Jimma", "Kelem Welega", "North Shewa", "Southwest Shewa", "West Arsi", "West Hararghe", "West Shewa", "West Welega"],
    "Amhara": ["Agew Awi", "East Gojjam", "North Gondar", "North Shewa", "North Wollo", "Oromia", "South Gondar", "South Wollo", "Wag Hemra", "West Gojjam"],
    "Tigray": ["Central Tigray", "East Tigray", "Northwest Tigray", "South Tigray", "Southeast Tigray", "Western Tigray"],
    # Add other regions as needed
}

# ─────────────────────────────────────────────────────────────
# SECTORS - Trade and Economic Sectors
# ─────────────────────────────────────────────────────────────
SECTORS = [
    "Agriculture", 
    "Livestock", 
    "Manufacturing", 
    "Handicrafts",
    "Food Processing", 
    "Textiles", 
    "Services", 
    "Technology",
    "Construction",
    "Transportation",
    "Energy",
    "Mining",
    "Tourism",
    "Education",
    "Healthcare",
    "Other"
]

# Sector icons for UI
SECTOR_ICONS = {
    "Agriculture": "🌾",
    "Livestock": "🐄",
    "Manufacturing": "🏭",
    "Handicrafts": "🧵",
    "Food Processing": "🍲",
    "Textiles": "👕",
    "Services": "🛠️",
    "Technology": "💻",
    "Construction": "🏗️",
    "Transportation": "🚚",
    "Energy": "⚡",
    "Mining": "⛏️",
    "Tourism": "🏖️",
    "Education": "📚",
    "Healthcare": "🏥",
    "Other": "📦"
}

# ─────────────────────────────────────────────────────────────
# UNITS - Measurement Units
# ─────────────────────────────────────────────────────────────
UNITS = [
    "kg", 
    "g", 
    "ton", 
    "litre", 
    "ml", 
    "piece", 
    "dozen", 
    "bunch", 
    "bag", 
    "box",
    "bottle",
    "carton",
    "crate",
    "head",
    "pair",
    "roll",
    "sheet",
    "bale",
    "sack"
]

# Unit conversion factors (to kg where applicable)
UNIT_CONVERSIONS = {
    "kg": 1.0,
    "g": 0.001,
    "ton": 1000.0,
    "litre": 1.0,  # For water equivalent
    "ml": 0.001,
    "piece": 0.5,  # Approximate
    "dozen": 6.0,  # Approximate
    "bunch": 0.5,  # Approximate
    "bag": 50.0,   # Standard bag
    "box": 10.0,   # Approximate
    "bottle": 1.0, # Approximate
    "carton": 20.0, # Approximate
    "crate": 15.0,  # Approximate
    "head": 250.0,  # Average cattle weight
    "pair": 1.0,
    "roll": 5.0,
    "sheet": 1.0,
    "bale": 200.0,  # Standard bale
    "sack": 50.0    # Standard sack
}

# ─────────────────────────────────────────────────────────────
# GRADES - Product Quality Grades
# ─────────────────────────────────────────────────────────────
GRADES_DICT = {
    "general": ["A", "B", "C", "D"],
    "grains": ["Premium", "Standard", "Grade 2", "Grade 3", "Grade 4"],
    "cattle": ["A", "B", "C", "D"],
    "processed_foods": ["Grade A", "Grade B", "Grade C", "Grade D"],
    "pottery": ["Master", "Standard", "Basic", "Economy"],
    "dairy": ["A", "B", "C", "D"],
    "textiles": ["Premium", "Standard", "Economy", "Basic"],
    "consulting": ["Expert", "Professional", "Standard", "Entry"],
    "coffee": ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
    "fruits": ["Premium", "Choice", "Standard", "Commercial"],
    "vegetables": ["Premium", "Choice", "Standard", "Commercial"],
    "honey": ["Grade A", "Grade B", "Grade C"],
    "spices": ["Premium", "Standard", "Commercial"],
}

# ─────────────────────────────────────────────────────────────
# PRODUCT STATUS
# ─────────────────────────────────────────────────────────────
PRODUCT_STATUS = {
    "available": "🟢 Available",
    "low_stock": "🟡 Low Stock",
    "out_of_stock": "🔴 Out of Stock",
    "pending": "⏳ Pending",
    "discontinued": "⛔ Discontinued"
}

# ─────────────────────────────────────────────────────────────
# ORDER STATUS
# ─────────────────────────────────────────────────────────────
ORDER_STATUS = [
    "pending",
    "confirmed",
    "processing",
    "shipped",
    "delivered",
    "completed",
    "cancelled",
    "refunded"
]

ORDER_STATUS_COLORS = {
    "pending": "#F59E0B",      # Yellow
    "confirmed": "#3B82F6",    # Blue
    "processing": "#8B5CF6",   # Purple
    "shipped": "#06B6D4",      # Cyan
    "delivered": "#10B981",    # Green
    "completed": "#10B981",    # Green
    "cancelled": "#EF4444",    # Red
    "refunded": "#EF4444"      # Red
}

# ─────────────────────────────────────────────────────────────
# USER ROLES
# ─────────────────────────────────────────────────────────────
USER_ROLES = [
    "producer",
    "merchant",
    "customer",
    "admin"
]

ROLE_ICONS = {
    "producer": "🚜",
    "merchant": "🏬",
    "customer": "🛒",
    "admin": "🛡️"
}

ROLE_NAMES = {
    "producer": "Producer",
    "merchant": "Merchant",
    "customer": "Customer",
    "admin": "Administrator"
}

ROLE_DESCRIPTIONS = {
    "producer": "Farmers and producers who list products for sale",
    "merchant": "Traders and businesses who buy and sell products",
    "customer": "End consumers looking to purchase products",
    "admin": "Platform administrators who manage the system"
}

# ─────────────────────────────────────────────────────────────
# NOTIFICATION TYPES
# ─────────────────────────────────────────────────────────────
NOTIFICATION_TYPES = {
    "info": "ℹ️",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "order": "📦",
    "message": "💬",
    "system": "⚙️",
    "alert": "🔔"
}

# ─────────────────────────────────────────────────────────────
# SESSION KEYS - All keys used in session_state
# ─────────────────────────────────────────────────────────────
SESSION_KEYS = [
    "user", 
    "profile", 
    "auth_token", 
    "authenticated",
    "user_role",
    "user_email",
    "show_profile_editor",
    "theme_mode", 
    "sidebar_light_mode", 
    "match_results",
    "forecast_result", 
    "m_forecast_result", 
    "wishlist",
    "auth_redirect",
    "nav_clicked",
    "cart",
    "order_history",
    "chat_open",
    "chat_messages",
    "page"
]

# ─────────────────────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────────────────────
ITEMS_PER_PAGE = 20
MAX_DISPLAY_ITEMS = 100

# ─────────────────────────────────────────────────────────────
# FILE UPLOAD LIMITS
# ─────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
ALLOWED_DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx"]

# ─────────────────────────────────────────────────────────────
# DATE FORMATS
# ─────────────────────────────────────────────────────────────
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"
DISPLAY_DATETIME_FORMAT = "%B %d, %Y at %I:%M %p"

# ─────────────────────────────────────────────────────────────
# CURRENCY
# ─────────────────────────────────────────────────────────────
CURRENCY_SYMBOL = "ETB"
CURRENCY_CODE = "ETB"
DECIMAL_PLACES = 2

# ─────────────────────────────────────────────────────────────
# DEFAULT VALUES
# ─────────────────────────────────────────────────────────────
DEFAULT_REGION = "Addis Ababa"
DEFAULT_ROLE = "customer"
DEFAULT_UNIT = "kg"
DEFAULT_GRADE = "Standard"
DEFAULT_SECTOR = "Agriculture"

# ─────────────────────────────────────────────────────────────
# API CONFIGURATION
# ─────────────────────────────────────────────────────────────
API_TIMEOUT_SECONDS = 30
CACHE_TTL_SECONDS = {
    "profile": 120,
    "products": 300,
    "notifications": 30,
    "stats": 600
}

# ─────────────────────────────────────────────────────────────
# PLATFORM MESSAGES
# ─────────────────────────────────────────────────────────────
WELCOME_MESSAGES = {
    "producer": "Welcome to the Producer Dashboard! 🚜\nManage your products, track sales, and connect with merchants.",
    "merchant": "Welcome to the Merchant Dashboard! 🏬\nFind products, manage orders, and grow your business.",
    "customer": "Welcome to the Customer Dashboard! 🛒\nDiscover products, place orders, and track deliveries.",
    "admin": "Welcome to the Admin Dashboard! 🛡️\nOversee the platform, manage users, and monitor analytics."
}

ERROR_MESSAGES = {
    "auth_failed": "Authentication failed. Please check your credentials.",
    "session_expired": "Your session has expired. Please sign in again.",
    "permission_denied": "You don't have permission to perform this action.",
    "not_found": "The requested resource was not found.",
    "server_error": "Server error. Please try again later.",
    "network_error": "Network connection error. Please check your internet connection.",
    "validation_error": "Please check your input and try again.",
    "database_error": "Database error. Please contact support."
}

SUCCESS_MESSAGES = {
    "profile_updated": "Profile updated successfully! ✅",
    "product_added": "Product added successfully! ✅",
    "product_updated": "Product updated successfully! ✅",
    "order_placed": "Order placed successfully! ✅",
    "order_cancelled": "Order cancelled successfully! ✅",
    "notification_sent": "Notification sent successfully! ✅",
    "stock_updated": "Stock updated successfully! ✅"
}

# ─────────────────────────────────────────────────────────────
# PLATFORM METADATA
# ─────────────────────────────────────────────────────────────
PLATFORM_NAME = "Ethiopian AI Supply Chain Platform"
PLATFORM_SHORT_NAME = "AI Supply Chain"
PLATFORM_VERSION = "2.0.0"
PLATFORM_DESCRIPTION = "Connecting Ethiopian farmers, merchants, and consumers through AI-powered supply chain management"
PLATFORM_ORGANIZATION = "Wolaita Sodo University"
PLATFORM_DEPARTMENT = "Department of Electrical and Computer Engineering"

# ─────────────────────────────────────────────────────────────
# SOCIAL LINKS
# ─────────────────────────────────────────────────────────────
SOCIAL_LINKS = {
    "github": "https://github.com/your-repo",
    "twitter": "https://twitter.com/your-handle",
    "linkedin": "https://linkedin.com/company/your-company",
    "website": "https://your-website.com"
}

# ─────────────────────────────────────────────────────────────
# SUPPORT CONTACT
# ─────────────────────────────────────────────────────────────
SUPPORT_EMAIL = "support@supplychain.et"
SUPPORT_PHONE = "+251-XXX-XXX-XXX"

# ─────────────────────────────────────────────────────────────
# ANALYTICS & TRACKING (Optional)
# ─────────────────────────────────────────────────────────────
ENABLE_ANALYTICS = False  # Set to True to enable analytics
ANALYTICS_ID = ""  # Google Analytics or other tracking ID
