"""Constants used across the Ethiopian AI Supply Chain Platform."""

# ─────────────────────────────────────────────────────────────
# REGIONS
# ─────────────────────────────────────────────────────────────
REGIONS = [
    "Addis Ababa", "Afar", "Amhara", "Benishangul-Gumuz", "Dire Dawa",
    "Gambela", "Harari", "Oromia", "Sidama", "Somali", "South West",
    "Tigray", "Central Ethiopia", "South Ethiopia"
]

# ─────────────────────────────────────────────────────────────
# SECTORS
# ─────────────────────────────────────────────────────────────
SECTORS = [
    "Agriculture", "Livestock", "Manufacturing", "Handicrafts",
    "Food Processing", "Textiles", "Services", "Other"
]

# ─────────────────────────────────────────────────────────────
# UNITS
# ─────────────────────────────────────────────────────────────
UNITS = ["kg", "g", "ton", "litre", "ml", "piece", "dozen", "bunch", "bag", "box"]

# ─────────────────────────────────────────────────────────────
# GRADES
# ─────────────────────────────────────────────────────────────
GRADES_DICT = {
    "general": ["A", "B", "C"],
    "grains": ["Premium", "Standard", "Grade 2", "Grade 3"],
    "cattle": ["A", "B", "C"],
    "processed_foods": ["Grade A", "Grade B", "Grade C"],
    "pottery": ["Master", "Standard", "Basic"],
    "dairy": ["A", "B", "C"],
    "textiles": ["Premium", "Standard", "Economy"],
    "consulting": ["Expert", "Professional", "Standard"],
}

# ─────────────────────────────────────────────────────────────
# SESSION KEYS - All keys used in session_state
# ─────────────────────────────────────────────────────────────
SESSION_KEYS = [
    "user", 
    "profile", 
    "auth_token", 
    "show_profile_editor",
    "theme_mode", 
    "sidebar_light_mode", 
    "match_results",
    "forecast_result", 
    "m_forecast_result", 
    "wishlist",
    "auth_redirect",
]
