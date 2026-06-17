@echo off
cd /d "%~dp0..\frontend"

npm install

echo.
echo Frontend build...
npm run build
