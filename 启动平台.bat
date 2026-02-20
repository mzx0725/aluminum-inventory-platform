@echo off
chcp 65001
cd /d "%~dp0"

echo.
echo Starting Backend Service...
cd backend
start "Backend" cmd /k python run.py
cd ..

echo Waiting 5 seconds...
ping 127.0.0.1 -n 6 > nul

echo Starting Frontend Service...
cd frontend
start "Frontend" cmd /k npm run dev
cd ..

echo Waiting 8 seconds...
ping 127.0.0.1 -n 9 > nul

echo Opening Browser...
start http://localhost:3000

echo.
echo ========================================
echo   Platform Started!
echo   Frontend: http://localhost:3000
echo   Backend: http://127.0.0.1:5000
echo   Login: admin / admin123
echo ========================================
echo.
pause
