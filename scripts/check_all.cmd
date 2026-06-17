@echo off
cd /d "%~dp0.."

call scripts\check_backend.cmd
if errorlevel 1 exit /b 1

call scripts\check_frontend.cmd
if errorlevel 1 exit /b 1

py scripts\mvp_report.py

echo.
echo ALL CHECKS PASSED
