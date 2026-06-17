@echo off
cd /d "%~dp0..\frontend"

call npm install

echo.
echo Frontend build...
call npm run build
