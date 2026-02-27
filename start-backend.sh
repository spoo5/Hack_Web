#!/usr/bin/env bash
# DataSage – start the FastAPI backend (Mac / Linux)
set -e
cd "$(dirname "$0")/backend" || exit 1

echo "========================================"
echo " DataSage – Starting Backend Server"
echo "========================================"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "Installing / updating dependencies..."
pip install -r requirements.txt -q

echo ""
echo "========================================"
echo " FastAPI server → http://localhost:8000"
echo " API docs       → http://localhost:8000/docs"
echo "========================================"
echo ""

# Optional – set Mistral AI key for LLM-powered queries:
# export MISTRAL_API_KEY=sk-your-key-here

python main.py
