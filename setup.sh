#!/bin/bash

# ─────────────────────────────────────────────
# Ethiopian AI Supply Chain Platform
# Streamlit Cloud Deployment Setup Script
# ─────────────────────────────────────────────

echo "🚀 Setting up Ethiopian AI Supply Chain Platform..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p .streamlit
mkdir -p models
mkdir -p logs
mkdir -p data

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create .streamlit directory if not exists
if [ ! -d ".streamlit" ]; then
    mkdir -p .streamlit
fi

# Create config.toml if not exists
if [ ! -f ".streamlit/config.toml" ]; then
    echo "⚙️ Creating Streamlit config..."
    cat > .streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false
enableFileWatcher = false

[browser]
gatherUsageStats = false

[runner]
magicEnabled = false

[logger]
level = "info"

[client]
showErrorDetails = true
toolbarMode = "auto"
displayMode = "auto"
EOF
fi

# Create .env from template if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE=your_service_role_key

# Groq API
GROQ_API_KEY=your_groq_api_key

# App Configuration
APP_SECRET_KEY=your-secret-key-here-32-characters-minimum
ADMIN_PASSWORD=admin_secure_password
SESSION_TIMEOUT=3600

# Database
DB_HOST=localhost
DB_NAME=supply_chain
DB_USER=postgres
DB_PASSWORD=your_db_password

# AI Model Paths
MODEL_PATH=models/
DEMAND_MODEL=demand_forecaster.pkl
FRAUD_MODEL=fraud_detector.pkl
PRICE_MODEL=price_predictor.pkl
MATCHING_MODEL=merchant_matcher.pkl
RECOMMENDATION_MODEL=recommendation_engine.pkl

# Deployment Mode
ENVIRONMENT=production
DEBUG=False
EOF
fi

# Create runtime.txt if not exists
if [ ! -f "runtime.txt" ]; then
    echo "🐍 Creating runtime.txt..."
    echo "python-3.10.12" > runtime.txt
fi

# Create packages.txt if not exists
if [ ! -f "packages.txt" ]; then
    echo "📦 Creating packages.txt..."
    cat > packages.txt << 'EOF'
build-essential
python3-dev
gcc
g++
make
libpq-dev
EOF
fi

# Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    echo "🔒 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/
.venv/
*.egg-info/
dist/
build/
*.egg

# Environment
.env
.env.local
.env.*.local
.secrets
.secrets.toml

# Logs
logs/
*.log
*.pid
*.seed

# Database
*.db
*.sqlite
*.sqlite3
*.db-journal

# Models (large files)
models/*.pkl
models/*.joblib
*.h5
*.pt
*.pth
*.onnx
models/*.zip

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
Thumbs.db
*.code-workspace

# Streamlit
.streamlit/secrets.toml
.streamlit/cache/
.streamlit/uploads/

# Coverage
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Deployment
*.pid
*.seed
*.pid.lock

# Testing
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Temp files
tmp/
temp/
*.tmp
*.temp

# OS
.DS_Store
Thumbs.db
*.swp
*.swo
EOF
fi

# Create streamlit secrets example
if [ ! -f ".streamlit/secrets.toml.example" ]; then
    echo "🔐 Creating secrets.toml.example..."
    cat > .streamlit/secrets.toml.example << 'EOF'
# Supabase Configuration
SUPABASE_URL = "your_supabase_project_url"
SUPABASE_KEY = "your_supabase_anon_key"
SUPABASE_SERVICE_ROLE = "your_service_role_key"

# Groq API
GROQ_API_KEY = "your_groq_api_key"

# App Security
APP_SECRET_KEY = "your-secret-key-here-32-characters-minimum"
ADMIN_PASSWORD = "admin_secure_password"

# Database
DB_HOST = "localhost"
DB_NAME = "supply_chain"
DB_USER = "postgres"
DB_PASSWORD = "your_db_password"
EOF
fi

# Set permissions
chmod +x setup.sh

echo "✅ Setup completed successfully!"
echo ""
echo "📌 Next steps:"
echo "1. Add your Supabase credentials to .env or Streamlit Cloud secrets"
echo "2. Place your AI model files in the models/ directory"
echo "3. Deploy to Streamlit Cloud"
echo ""
echo "🚀 To deploy:"
echo "   git add ."
echo "   git commit -m 'Initial deployment setup'"
echo "   git push origin main"
echo ""
echo "🌐 Then deploy on: https://share.streamlit.io"
