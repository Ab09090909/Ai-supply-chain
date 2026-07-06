"""Shared constants used across all pages."""

REGIONS = ["Addis Ababa", "Oromia", "SNNPR", "Amhara", "Tigray", "Sidama", "Dire Dawa", "Harari"]
SECTORS = ["Agriculture", "Manufacturing", "Handicrafts", "Livestock", "Food Processing", "Textiles", "Services"]
UNITS = [
    "kg", "g", "mg", "ton", "quintal", "pound (lb)", "ounce (oz)",
    "liter (L)", "milliliter (mL)", "gallon", "quart", "pint", "cup",
    "meter (m)", "centimeter (cm)", "millimeter (mm)", "kilometer (km)",
    "inch", "foot", "yard", "square meter", "hectare", "acre",
    "piece", "unit", "pair", "dozen", "gross", "head", "bundle",
    "bag", "box", "carton", "crate", "sack", "hour", "day", "week",
    "month", "year", "service", "set", "pack", "roll", "sheet"
]

GRADES_DICT = {
    "general": ["Premium", "Grade A", "Grade B", "Grade C", "Standard", "Economy"],
    "coffee": ["Specialty (90+)", "Premium (85-89)", "Grade 1 (80-84)", "Grade 2 (75-79)", "Grade 3 (70-74)", "Grade 4 (65-69)", "Grade 5 (60-64)", "Below Standard (<60)"],
    "tea": ["Orthodox Premium", "Orthodox Grade 1", "Orthodox Grade 2", "CTC Premium", "CTC Standard", "Dust/Fannings"],
    "spices": ["Export Quality", "Premium Grade", "Standard Grade", "Commercial Grade", "Substandard"],
    "grains": ["Premium", "Grade A", "Grade B", "Grade C", "Feed Grade", "Reject"],
    "fruits": ["Export Premium", "Class I", "Class II", "Class III", "Processing Grade", "Reject"],
    "vegetables": ["Premium Fresh", "Grade A", "Grade B", "Processing Grade", "Reject"],
    "cattle": ["Premium Breed", "Grade A (Excellent)", "Grade B (Good)", "Grade C (Fair)", "Grade D (Poor)", "Cull"],
    "sheep": ["Premium Wool", "Grade A", "Grade B", "Grade C", "Cull"],
    "goats": ["Premium Breed", "Grade A", "Grade B", "Grade C", "Cull"],
    "poultry": ["Premium Free-Range", "Grade A", "Grade B", "Grade C", "Cull"],
    "textiles": ["Luxury", "Premium", "Grade A", "Grade B", "Grade C", "Seconds/Reject"],
    "processed_foods": ["Premium Organic", "Grade A", "Grade B", "Grade C", "Substandard"],
    "oils": ["Extra Virgin", "Virgin", "Refined Premium", "Refined Standard", "Industrial Grade"],
    "dairy": ["Premium Organic", "Grade A", "Grade B", "Grade C", "Processing Grade"],
    "pottery": ["Master Artisan", "Premium Handmade", "Standard Handmade", "Mass Production", "Reject"],
    "basketry": ["Premium Natural", "Grade A", "Grade B", "Grade C", "Reject"],
    "leather": ["Full Grain Premium", "Top Grain", "Genuine Leather", "Bonded Leather", "Reject"],
    "cars": ["Luxury New", "Premium New", "Standard New", "Certified Pre-Owned", "Used Grade A", "Used Grade B", "Salvage"],
    "motorcycles": ["Premium New", "Standard New", "Used Grade A", "Used Grade B", "Salvage"],
    "tractors": ["Premium New", "Standard New", "Used Grade A", "Used Grade B", "Salvage"],
    "machinery": ["Premium New", "Standard New", "Refurbished", "Used Grade A", "Used Grade B", "Scrap"],
    "consulting": ["Expert/Premium", "Professional", "Standard", "Basic"],
    "transport": ["Premium Express", "Standard", "Economy", "Basic"],
    "cement": ["Premium Grade", "Standard Grade", "Economy Grade"],
    "steel": ["Premium Grade", "Standard Grade", "Economy Grade", "Scrap"],
    "timber": ["Premium Hardwood", "Standard Hardwood", "Softwood Grade A", "Softwood Grade B", "Reject"],
}

AGREEMENT_TERMS = [
    ("Quality Assurance", "The Producer guarantees that goods delivered shall conform to the agreed quality grade as specified above."),
    ("Payment Terms", "Payment shall be made via the agreed payment method upon delivery and confirmation of goods."),
    ("Delivery & Transfer of Risk", "The Producer shall deliver goods by the agreed delivery date."),
    ("Dispute Resolution", "Any disputes shall first be resolved through good-faith negotiation."),
    ("Force Majeure", "Neither party shall be liable for delays caused by circumstances beyond their control."),
    ("Governing Law", "This agreement is governed by the Commercial Code of Ethiopia."),
]

SESSION_KEYS = [
    "user", "profile", "edit_product_id", "show_pref_form",
    "agreement_product_id", "agreement_merchant",
    "agreement_pdf", "agreement_ref", "agreement_merchant_name",
    "agreement_pending_order_id", "agreement_preview_pdf",
    "agreement_preview_ref", "admin_viewing_user", "admin_viewing_doc",
    "match_results", "match_product",
]
