#!/bin/bash

# 🔄 Gravity Analyst Suite - Update Script
# Pulls latest changes from all component repos

set -e

SUITE_DIR="$HOME/Documents/gravity-analyst-suite"
cd "$SUITE_DIR"

echo "🔄 Updating Gravity Analyst Suite..."
echo "================================================"

# Pull latest master repo changes
echo ""
echo "📥 Pulling master repo..."
git pull origin main

# Update all submodules to latest
echo ""
echo "📦 Updating submodules to latest commits..."
git submodule update --remote --merge

# Show status
echo ""
echo "📊 Current submodule versions:"
git submodule status

echo ""
echo "================================================"
echo "✅ Update Complete!"
echo ""
echo "If you want to lock these versions in the master repo:"
echo "  git add . && git commit -m 'Update submodules' && git push"
