#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  DataSage – start the React / Vite frontend (Mac / Linux)
# ─────────────────────────────────────────────────────────────────
set -e
cd "$(dirname "$0")/frontend"

echo "========================================"
echo " DataSage – Starting Frontend Server"
echo "========================================"

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

echo ""
echo "========================================"
echo " Vite dev server → http://localhost:3000"
echo " (proxies /api/* → http://localhost:8000)"
echo "========================================"
echo ""

npm run dev
