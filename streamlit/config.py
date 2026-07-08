# ─────────────────────────────────────────────
# Ethiopian AI Supply Chain Platform
# Streamlit Configuration
# ─────────────────────────────────────────────

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
# Max file upload size in MB
maxUploadSize = 200

# Security settings
enableXsrfProtection = true
enableCORS = false

# Performance
enableFileWatcher = false
runOnSave = false

# Port configuration
port = 8501
address = "0.0.0.0"

[browser]
# Disable usage stats collection
gatherUsageStats = false

# Default page
defaultPage = "app"

[runner]
# Disable magic commands for security
magicEnabled = false

[logger]
level = "info"

[client]
showErrorDetails = true
toolbarMode = "auto"
displayMode = "auto"

[theme.dark]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
