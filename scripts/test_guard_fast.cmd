@echo off
cd /d "%~dp0.."

py scripts\strip_bom.py --check
if errorlevel 1 exit /b 1

call scripts\check_frontend.cmd
if errorlevel 1 exit /b 1

call scripts\test_ui.cmd
if errorlevel 1 exit /b 1

echo.
echo FAST UI GUARD PASSED
