#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  DataSage – start the FastAPI backend (Mac / Linux)
# ─────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/backend"

echo "========================================"
echo " DataSage – Starting Backend Server"
echo "========================================"

# Create virtual environment if it doesn't exist yet
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

echo "Installing / updating dependencies..."
pip install -r requirements.txt -q

echo ""
echo "========================================"
echo " FastAPI server → http://localhost:8000"
echo " API docs       → http://localhost:8000/docs"
echo "========================================"
echo ""

# Optional Mistral AI key – export before running this script or set it here:
# export MISTRAL_API_KEY=your_key_here

python main.py
