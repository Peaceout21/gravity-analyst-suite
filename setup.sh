#!/bin/bash

# 🌌 Gravity Analyst Suite - Automated Setup Script
# This script initializes submodules and sets up virtual environments

set -e  # Exit on error

SUITE_DIR="$HOME/Documents/gravity-analyst-suite"
cd "$SUITE_DIR"

echo "🌌 Starting Gravity Analyst Suite Setup..."
echo "================================================"

# Initialize and update submodules
echo ""
echo "📦 Initializing git submodules..."
git submodule update --init --recursive
echo "✓ Submodules initialized"

# Setup gravitic-macro
echo ""
echo "📊 Setting up gravitic-macro..."
cd "$SUITE_DIR/gravitic-macro"
if [ ! -d "macro-venv" ]; then
    python3 -m venv macro-venv
    echo "✓ Created macro-venv"
else
    echo "✓ macro-venv already exists"
fi
source macro-venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Installed dependencies"
elif [ -f "pyproject.toml" ]; then
    pip install -e .
    echo "✓ Installed package in editable mode"
fi
deactivate

# Setup gravitic-celestial
echo ""
echo "🎨 Setting up gravitic-celestial..."
cd "$SUITE_DIR/gravitic-celestial"
if [ ! -d "celestial-venv" ]; then
    python3 -m venv celestial-venv
    echo "✓ Created celestial-venv"
else
    echo "✓ celestial-venv already exists"
fi
source celestial-venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Installed dependencies"
elif [ -f "pyproject.toml" ]; then
    pip install -e .
    echo "✓ Installed package in editable mode"
fi
deactivate

# Setup gravitic-nebula
echo ""
echo "🪐 Setting up gravitic-nebula..."
cd "$SUITE_DIR/gravitic-nebula"
if [ ! -d "nebula-venv" ]; then
    python3 -m venv nebula-venv
    echo "✓ Created nebula-venv"
else
    echo "✓ nebula-venv already exists"
fi
source nebula-venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Installed dependencies"
elif [ -f "pyproject.toml" ]; then
    pip install -e .
    echo "✓ Installed package in editable mode"
fi
deactivate

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Add API keys to .env files in each repository"
echo "2. Initialize Macro index: cd gravitic-macro && source macro-venv/bin/activate && python3 scripts/test_ingestion.py"
echo "3. Fetch Nebula signals: cd gravitic-nebula && source nebula-venv/bin/activate && python3 scripts/run_alpha_sync.py TSLA,NVDA"
echo "4. Launch dashboard: cd gravitic-celestial && source celestial-venv/bin/activate && export PYTHONPATH=\$PYTHONPATH:../gravitic-macro && streamlit run ui/app.py"
echo ""
echo "See README.md for detailed instructions!"
