@echo off
echo ========================================
echo DataSage - Starting Frontend Server
echo ========================================
echo.

cd frontend

echo Checking for node_modules...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo ========================================
echo Starting Vite dev server on port 3000
echo ========================================
echo.

call npm run dev

pause
