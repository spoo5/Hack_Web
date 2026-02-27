#!/bin/bash
echo "========================================"
echo "DataSage - Starting Backend Server"
echo "========================================"
echo ""

cd "$(dirname "$0")/backend" || exit 1

echo "Checking for virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "Starting FastAPI server on port 8000"
echo "========================================"
echo ""

python main.py
