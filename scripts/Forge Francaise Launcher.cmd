@echo off
title Forge Francaise Launcher
cd /d "D:\PYTHON\Forge Francaise"

echo.
echo ==========================================
echo  Forge Francaise
echo  Backend:  http://127.0.0.1:8797/api/health
echo  Frontend: http://127.0.0.1:5197
echo ==========================================
echo.

start "Forge Backend 8797" cmd /k scripts\dev_backend.cmd
timeout /t 4 /nobreak >nul
start "Forge Frontend 5197" cmd /k scripts\dev_frontend.cmd
timeout /t 7 /nobreak >nul
start "" "http://127.0.0.1:5197"
