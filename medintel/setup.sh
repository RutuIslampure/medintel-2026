#!/bin/bash
# setup.sh - One-click setup for MedIntel
# Usage: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   MedIntel AI — Setup & Launch       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Generate synthetic data
echo "🗄️  Generating patient dataset..."
python generate_data.py

# Train ML model
echo "🤖 Training risk prediction model..."
python train_model.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Launching MedIntel dashboard..."
echo "   Open http://localhost:8501 in your browser"
echo ""
streamlit run app.py
