#!/bin/bash

# Create necessary directories
mkdir -p .streamlit
mkdir -p models
mkdir -p logs

# Install system dependencies
apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create .env from template if not exists
if [ ! -f .env ]; then
    cp .env.example .env || true
fi

# Create streamlit config
if [ ! -f .streamlit/config.toml ]; then
    cp .streamlit/config.toml.example .streamlit/config.toml || true
fi

echo "Setup completed successfully!"
