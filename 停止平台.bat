@echo off
chcp 65001
echo.
echo Stopping Backend...
taskkill /f /fi "WINDOWTITLE eq Backend*" 2>nul

echo Stopping Frontend...
taskkill /f /fi "WINDOWTITLE eq Frontend*" 2>nul

echo Cleaning Port 5000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5000.*LISTENING"') do taskkill /f /pid %%a 2>nul

echo Cleaning Port 3000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000.*LISTENING"') do taskkill /f /pid %%a 2>nul

echo.
echo All services stopped.
echo.
pause
