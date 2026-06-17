@echo off
setlocal
set "ROOT=%~dp0.."

echo.
echo === BOM CHECK ===
py "%ROOT%\scripts\strip_bom.py" --check
if errorlevel 1 exit /b 1

echo.
echo === BACKEND CHECK ===
call "%ROOT%\scripts\check_backend.cmd"
if errorlevel 1 exit /b 1

echo.
echo === FRONTEND BUILD CHECK ===
call "%ROOT%\scripts\check_frontend.cmd"
if errorlevel 1 exit /b 1

echo.
echo === UI / UX PLAYWRIGHT CHECK ===
call "%ROOT%\scripts\test_ui.cmd"
if errorlevel 1 exit /b 1

echo.
echo TEST GUARD PASSED
endlocal