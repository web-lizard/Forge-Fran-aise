@echo off
setlocal
set "ROOT=%~dp0.."

call "%ROOT%\scripts\check_backend.cmd"
if errorlevel 1 exit /b 1

call "%ROOT%\scripts\check_frontend.cmd"
if errorlevel 1 exit /b 1

py "%ROOT%\scripts\mvp_report.py"

echo.
echo ALL CHECKS PASSED
endlocal