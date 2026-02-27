#!/bin/bash
echo "========================================"
echo "DataSage - Full Stack Startup"
echo "========================================"
echo ""
echo "Starting Backend and Frontend servers..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend in background
echo "Starting backend..."
cd "$SCRIPT_DIR/backend" || exit 1

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

python main.py &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to initialize
sleep 3

# Start frontend in background
echo "Starting frontend..."
cd "$SCRIPT_DIR/frontend" || exit 1

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "Both servers are running"
echo "========================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for either process to exit and then stop both
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait $BACKEND_PID $FRONTEND_PID
