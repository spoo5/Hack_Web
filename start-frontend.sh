#!/bin/bash
echo "========================================"
echo "DataSage - Starting Frontend Server"
echo "========================================"
echo ""

cd "$(dirname "$0")/frontend" || exit 1

echo "Checking for node_modules..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "========================================"
echo "Starting Vite dev server on port 3000"
echo "========================================"
echo ""

npm run dev
