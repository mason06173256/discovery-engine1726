@echo off
REM Discovery Engine - Start Backend and Frontend (Windows)

echo.
echo Starting Discovery Engine...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm not found. Please install Node.js 16+
    pause
    exit /b 1
)

REM Install backend dependencies if needed
echo Checking backend dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing backend dependencies...
    pip install -q fastapi uvicorn groq ddgs pytest
)

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start backend
echo Starting backend...
start "Discovery Engine - Backend" python -m uvicorn discovery_engine.api:app --reload --host 0.0.0.0 --port 8000
echo Backend started on port 8000

REM Wait a bit for backend to start
timeout /t 3 /nobreak

REM Start frontend
echo Starting frontend...
cd frontend
start "Discovery Engine - Frontend" npm run dev
cd ..

echo.
echo ================================================
echo Discovery Engine is running!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs:     http://localhost:8000/docs
echo.
echo Close the command windows to stop the servers
echo ================================================
echo.
pause
