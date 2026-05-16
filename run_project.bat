@echo off
TITLE SecurBank - Fraud Detection System
COLOR 0B

echo ======================================================
echo   SecurBank: Fraud Detection in Online Banking
echo ======================================================
echo.
echo [1/2] Starting Backend (Flask API)...
start "SecurBank Backend" cmd /k "echo Starting Flask API... && if exist .venv\Scripts\activate (call .venv\Scripts\activate) else (echo Virtual environment not found, trying global python...) && python app.py"

echo.
echo [2/2] Starting Frontend (React/Vite)...
start "SecurBank Frontend" cmd /k "echo Starting React Frontend... && cd frontend && npm run dev"

echo.
echo ------------------------------------------------------
echo BOTH SERVICES ARE STARTING
echo.
echo Backend URL:  http://localhost:5000
echo Frontend URL: http://localhost:5173
echo.
echo (Keep the other windows open while using the app)
echo ------------------------------------------------------
echo.
pause
