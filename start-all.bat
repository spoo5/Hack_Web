@echo off
echo ========================================
echo DataSage - Full Stack Startup
echo ========================================
echo.
echo Starting Backend and Frontend servers...
echo.

REM Start backend in new window
start "DataSage Backend" cmd /k "cd backend && (if not exist venv python -m venv venv) && call venv\Scripts\activate && pip install -r requirements.txt && python main.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "DataSage Frontend" cmd /k "cd frontend && (if not exist node_modules call npm install) && call npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit this window
echo (Server windows will remain open)
pause >nul
