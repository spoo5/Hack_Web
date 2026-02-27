#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  DataSage – launch BOTH backend and frontend (Mac / Linux)
#
#  Usage:
#    chmod +x start-all.sh          # make executable (first time only)
#    ./start-all.sh                 # run
#
#  Optional – set Mistral AI key for LLM-powered queries:
#    MISTRAL_API_KEY=sk-... ./start-all.sh
# ─────────────────────────────────────────────────────────────────
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo " DataSage – Full Stack Startup"
echo "========================================"
echo ""

# ── Backend ──────────────────────────────────────────────────────
BACKEND_DIR="$ROOT/backend"

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[backend] Creating Python virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"
echo "[backend] Installing Python dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt" -q

echo "[backend] Starting FastAPI on http://localhost:8000 ..."
(cd "$BACKEND_DIR" && python main.py) &
BACKEND_PID=$!

# Give the backend a moment to bind its port
sleep 2

# ── Frontend ─────────────────────────────────────────────────────
FRONTEND_DIR="$ROOT/frontend"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "[frontend] Installing Node dependencies..."
    (cd "$FRONTEND_DIR" && npm install)
fi

echo "[frontend] Starting Vite dev server on http://localhost:3000 ..."
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo " Backend  → http://localhost:8000"
echo " API docs → http://localhost:8000/docs"
echo " Frontend → http://localhost:3000   ← open this in your browser"
echo "========================================"
echo ""
echo "Press Ctrl-C to stop both servers."

# Wait for either process to exit (e.g. on Ctrl-C)
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait $BACKEND_PID $FRONTEND_PID
