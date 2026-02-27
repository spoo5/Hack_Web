@echo off
echo ========================================
echo DataSage - Starting Backend Server
echo ========================================
echo.

cd backend

echo Checking for virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Starting FastAPI server on port 8000
echo ========================================
echo.

python main.py

pause
